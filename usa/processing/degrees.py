from pathlib import Path
import pandas as pd
from usa.processing.base_processor import BaseProcessor, YearlyProcessor
from usa.processing.constants import (
    AWLEVEL_TO_DEGREE_TYPE,
    CIPCODE_VARNAME,
    CIP_FREQUENCIES_SHEET,
    FIRST_MAJOR_CODE,
    GRAND_TOTAL_CIP_CODE,
    UNDERGRAD_DEGREE_TYPES,
    COUNTRY_USA,
    CIP_MULTIPLIER,
    MIN_GRADUATES,
    UNITID_COLUMN,
)


class DepartmentsProcessor(BaseProcessor):

    def __init__(self, cip_lookup_path: Path, output_path: Path):
        super().__init__(output_path)
        self.cip_lookup_path = Path(cip_lookup_path)
        self.data = None

    def load_data(self):
        self.data = pd.read_excel(self.cip_lookup_path, sheet_name=CIP_FREQUENCIES_SHEET)

    def transform(self):
        var_col = self._get_column(["VarName", "varname"])
        code_col = self._get_column(["CodeValue", "codevalue"])
        label_col = self._get_column(["ValueLabel", "valuelabel"])

        cip_codes = self.data[self.data[var_col] == CIPCODE_VARNAME][[code_col, label_col]]
        cip_codes = cip_codes[cip_codes[code_col] != GRAND_TOTAL_CIP_CODE]

        cip_codes["four_digit"] = (cip_codes[code_col] * CIP_MULTIPLIER).astype(int) / CIP_MULTIPLIER
        cip_codes = cip_codes.drop_duplicates(subset=["four_digit"])

        self.result_df = pd.DataFrame({
            "department_id": (cip_codes[code_col] * CIP_MULTIPLIER).astype(int).astype(str),
            "department_name": cip_codes[label_col].str.strip(),
            "country": COUNTRY_USA,
        }).dropna().drop_duplicates()

    def _get_column(self, candidates: list):
        for col in candidates:
            if col in self.data.columns:
                return col
        raise KeyError(f"Missing expected columns: {candidates}")


class DegreesProcessor(YearlyProcessor):

    def __init__(self, completions_path: Path, academic_year: int, output_path: Path):
        super().__init__(completions_path, academic_year, output_path)

    def transform(self):
        df = self.data[self.data["MAJORNUM"] == FIRST_MAJOR_CODE].copy()

        df["degree_type"] = df["AWLEVEL"].map(AWLEVEL_TO_DEGREE_TYPE)
        df = df.dropna(subset=["degree_type"])
        df = df[df["degree_type"].isin(UNDERGRAD_DEGREE_TYPES)]

        df["department_id"] = (df["CIPCODE"] * CIP_MULTIPLIER).astype(int).astype(str)

        aggregated = df.groupby(
            [UNITID_COLUMN, "department_id", "degree_type"], as_index=False
        ).agg({"CTOTALT": "sum", "CTOTALW": "sum", "CNRALT": "sum"})

        self.result_df = pd.DataFrame({
            "college_id": aggregated[UNITID_COLUMN],
            "academic_year": self.academic_year,
            "department_id": aggregated["department_id"],
            "degree_type": aggregated["degree_type"],
            "total_graduates": aggregated["CTOTALT"],
            "total_female_graduates": aggregated["CTOTALW"],
            "total_international_graduates": aggregated["CNRALT"],
        })

    def validate(self):
        self.result_df = self.result_df[self.result_df["total_graduates"] > MIN_GRADUATES]


def process_degrees(
    completions_path: Path,
    cip_lookup_path: Path,
    academic_year: int,
):
    departments_processor = DepartmentsProcessor(cip_lookup_path, Path("/tmp/placeholder"))
    departments_processor.load_data()
    departments_processor.transform()
    departments_processor.validate()

    degrees_processor = DegreesProcessor(completions_path, academic_year, Path("/tmp/placeholder"))
    degrees_processor.load_data()
    degrees_processor.transform()
    degrees_processor.validate()

    return degrees_processor.result_df, departments_processor.result_df
