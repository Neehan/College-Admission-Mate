import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING, cast
from processing.usa.constants import (
    ACADEMIC_YEAR_2024,
    AWLEVEL_TO_DEGREE_TYPE,
    CIPCODE_VARNAME,
    CIP_FREQUENCIES_SHEET,
    FIRST_MAJOR_CODE,
    GRAND_TOTAL_CIP_CODE,
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
    def __init__(self, cip_lookup_path, output_path):
        self.cip_lookup_path = Path(cip_lookup_path)
        self.output_path = Path(output_path)

    def load_data(self):
        self.cip_df = pd.read_excel(
            self.cip_lookup_path, sheet_name=CIP_FREQUENCIES_SHEET
        )

    def filter_cip_codes(self):
        self.cip_codes_df = self.cip_df[self.cip_df["VarName"] == CIPCODE_VARNAME][
            ["CodeValue", "ValueLabel"]
        ].copy()

    def filter_broad_categories(self):
        self.cip_codes_df = self.cip_codes_df[
            self.cip_codes_df["CodeValue"] != GRAND_TOTAL_CIP_CODE
        ].copy()
        code_value_series = cast("Series", self.cip_codes_df["CodeValue"])
        self.cip_codes_df["FourDigit"] = code_value_series.apply(
            lambda x: int(x * 100) / 100
        )
        self.cip_codes_df = self.cip_codes_df.drop_duplicates(  # type: ignore
            subset=["FourDigit"]
        ).copy()

    def transform(self):
        result = pd.DataFrame()
        code_value_series = cast("Series", self.cip_codes_df["CodeValue"])
        value_label_series = cast("Series", self.cip_codes_df["ValueLabel"])
        result["department_id"] = code_value_series.apply(CIPCodeFormatter.format)
        result["department_name"] = value_label_series.apply(
            DepartmentNameCleaner.clean
        )
        self.result_df = result.dropna().drop_duplicates()

    def save(self):
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
    def __init__(self, completions_path, output_path):
        self.completions_path = Path(completions_path)
        self.output_path = Path(output_path)

    def load_data(self):
        self.completions_df = pd.read_csv(self.completions_path)

    def filter_first_majors(self):
        self.completions_df = self.completions_df[
            self.completions_df["MAJORNUM"] == FIRST_MAJOR_CODE
        ].copy()

    def map_degree_types(self):
        awlevel_series = cast("Series", self.completions_df["AWLEVEL"])
        self.completions_df["degree_type"] = awlevel_series.apply(AwardLevelMapper.map)
        self.completions_df = self.completions_df.dropna(subset=["degree_type"]).copy()  # type: ignore

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
        result["academic_year"] = ACADEMIC_YEAR_2024
        result["department_id"] = self.aggregated_df["department_id"]
        result["degree_type"] = self.aggregated_df["degree_type"]
        result["total_graduates"] = self.aggregated_df["CTOTALT"]
        result["total_female_graduates"] = self.aggregated_df["CTOTALW"]
        result["total_international_graduates"] = self.aggregated_df["CNRALT"]

        self.result_df = result[result["total_graduates"] > 0].copy()

    def save(self):
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
    completions_path, cip_lookup_path, output_degrees_path, output_departments_path
):
    departments_processor = DepartmentsProcessor(
        cip_lookup_path, output_departments_path
    )
    departments_df = departments_processor.process()

    degrees_processor = DegreesProcessor(completions_path, output_degrees_path)
    degrees_df = degrees_processor.process()

    return degrees_df, departments_df
