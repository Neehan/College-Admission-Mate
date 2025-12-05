import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast
from processing.usa.constants import (
    AWLEVEL_TO_DEGREE_TYPE,
    CIPCODE_VARNAME,
    CIP_FREQUENCIES_SHEET,
    FIRST_MAJOR_CODE,
    GRAND_TOTAL_CIP_CODE,
    UNDERGRAD_DEGREE_TYPES,
)

if TYPE_CHECKING:
    from pandas import Series


class CIPCodeFormatter:
    @staticmethod
    def format(cip_code):
        if pd.isna(cip_code):
            return None
        return int(cip_code * 100)

    @staticmethod
    def to_department_id(cip_code):
        if pd.isna(cip_code):
            return None
        return int(float(cip_code) * 100)


class DepartmentNameCleaner:
    @staticmethod
    def clean(name):
        if pd.isna(name):
            return None
        return str(name).strip()


class AwardLevelMapper:
    @staticmethod
    def map(awlevel_code):
        if pd.isna(awlevel_code):
            return None
        return AWLEVEL_TO_DEGREE_TYPE.get(int(awlevel_code))


class DepartmentsProcessor:
    def __init__(self, cip_lookup_path, output_path: Optional[Path]):
        self.cip_lookup_path = Path(cip_lookup_path)
        self.output_path = Path(output_path) if output_path is not None else None

    def load_data(self):
        self.cip_df = pd.read_excel(
            self.cip_lookup_path, sheet_name=CIP_FREQUENCIES_SHEET
        )

    def _pick_column(self, candidates):
        for col in candidates:
            if col in self.cip_df.columns:
                return col
        raise KeyError(f"Missing expected columns from {candidates}")

    def _varname_column(self):
        if "VarName" in self.cip_df.columns:
            return "VarName"
        if "varname" in self.cip_df.columns:
            return "varname"
        raise KeyError("CIP lookup missing VarName/varname column")

    def filter_cip_codes(self):
        var_col = self._varname_column()
        self.code_col = self._pick_column(["CodeValue", "codevalue"])
        self.label_col = self._pick_column(["ValueLabel", "valuelabel"])

        self.cip_codes_df = self.cip_df[self.cip_df[var_col] == CIPCODE_VARNAME][
            [self.code_col, self.label_col]
        ].copy()

    def filter_broad_categories(self):
        self.cip_codes_df = self.cip_codes_df[
            self.cip_codes_df[self.code_col] != GRAND_TOTAL_CIP_CODE
        ].copy()
        code_value_series = cast("Series", self.cip_codes_df[self.code_col])
        self.cip_codes_df["FourDigit"] = code_value_series.apply(
            lambda x: int(x * 100) / 100
        )
        self.cip_codes_df = self.cip_codes_df.drop_duplicates(  # type: ignore
            subset=["FourDigit"]
        ).copy()

    def transform(self):
        result = pd.DataFrame()
        code_value_series = cast("Series", self.cip_codes_df[self.code_col])
        value_label_series = cast("Series", self.cip_codes_df[self.label_col])
        result["department_id"] = code_value_series.apply(CIPCodeFormatter.format)
        result["department_name"] = value_label_series.apply(
            DepartmentNameCleaner.clean
        )
        result["country"] = "USA"
        self.result_df = result.dropna().drop_duplicates()

    def save(self):
        if self.output_path is None:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        self.load_data()
        self.filter_cip_codes()
        self.filter_broad_categories()
        self.transform()
        self.save()
        return self.result_df


class DegreesProcessor:
    def __init__(self, completions_path, output_path: Optional[Path], academic_year: int):
        self.completions_path = Path(completions_path)
        self.output_path = Path(output_path) if output_path is not None else None
        self.academic_year = academic_year

    def load_data(self):
        self.completions_df = pd.read_csv(self.completions_path)

    def filter_first_majors(self):
        self.completions_df = self.completions_df[
            self.completions_df["MAJORNUM"] == FIRST_MAJOR_CODE
        ].copy()

    def map_degree_types(self):
        awlevel_series = cast("Series", self.completions_df["AWLEVEL"])
        self.completions_df["degree_type"] = awlevel_series.apply(AwardLevelMapper.map)
        self.completions_df = (
            self.completions_df.dropna(subset=["degree_type"])  # type: ignore
        )
        self.completions_df = self.completions_df[
            self.completions_df["degree_type"].isin(UNDERGRAD_DEGREE_TYPES)
        ].copy()

    def map_departments(self):
        cipcode_series = cast("Series", self.completions_df["CIPCODE"])
        self.completions_df["department_id"] = cipcode_series.apply(
            CIPCodeFormatter.to_department_id
        )

    def aggregate_by_department(self):
        self.aggregated_df = self.completions_df.groupby(
            ["UNITID", "department_id", "degree_type"], as_index=False
        ).agg({"CTOTALT": "sum", "CTOTALW": "sum", "CNRALT": "sum"})

    def transform(self):
        result = pd.DataFrame()
        result["college_id"] = self.aggregated_df["UNITID"]
        result["academic_year"] = self.academic_year
        result["department_id"] = self.aggregated_df["department_id"]
        result["degree_type"] = self.aggregated_df["degree_type"]
        result["total_graduates"] = self.aggregated_df["CTOTALT"]
        result["total_female_graduates"] = self.aggregated_df["CTOTALW"]
        result["total_international_graduates"] = self.aggregated_df["CNRALT"]

        self.result_df = result[result["total_graduates"] > 0].copy()

    def save(self):
        if self.output_path is None:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        self.load_data()
        self.filter_first_majors()
        self.map_degree_types()
        self.map_departments()
        self.aggregate_by_department()
        self.transform()
        self.save()
        return self.result_df


def process_degrees(
    completions_path,
    cip_lookup_path,
    output_degrees_path,
    output_departments_path,
    academic_year: int,
):
    departments_processor = DepartmentsProcessor(
        cip_lookup_path, output_departments_path
    )
    departments_df = departments_processor.process()

    degrees_processor = DegreesProcessor(
        completions_path, output_degrees_path, academic_year
    )
    degrees_df = degrees_processor.process()

    return degrees_df, departments_df
