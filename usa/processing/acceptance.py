from pathlib import Path
import pandas as pd
from usa.processing.base_processor import YearlyProcessor
from usa.processing.constants import (
    UNITID_COLUMN,
    PERCENTAGE_MULTIPLIER,
    PERCENTAGE_DECIMALS,
    MIN_DENOMINATOR,
)


class AcceptanceProcessor(YearlyProcessor):

    def transform(self):
        df = self.data

        applicants_total = df["APPLCN"]
        applicants_female = df["APPLCNW"]
        applicants_intl = df["APPLCNAN"]
        admitted_total = df["ADMSSN"]
        admitted_female = df["ADMSSNW"]
        admitted_intl = df["ADMSSNAN"]

        acceptance_rate = (admitted_total / applicants_total * PERCENTAGE_MULTIPLIER).round(PERCENTAGE_DECIMALS)
        acceptance_rate_female = (admitted_female / applicants_female * PERCENTAGE_MULTIPLIER).round(PERCENTAGE_DECIMALS)
        acceptance_rate_intl = (admitted_intl / applicants_intl * PERCENTAGE_MULTIPLIER).round(PERCENTAGE_DECIMALS)

        self.result_df = pd.DataFrame({
            "college_id": df[UNITID_COLUMN],
            "academic_year": self.academic_year,
            "accepted_total": admitted_total,
            "accepted_female": admitted_female,
            "accepted_international": admitted_intl,
            "acceptance_rate": acceptance_rate,
            "acceptance_rate_female": acceptance_rate_female,
            "acceptance_rate_international": acceptance_rate_intl,
        })

    def validate(self):
        self.result_df = self.result_df.dropna(subset=["accepted_total"])
        self.result_df = self.result_df[
            (self.result_df["accepted_total"] > MIN_DENOMINATOR) &
            (self.result_df["acceptance_rate"] > MIN_DENOMINATOR)
        ]


def process_acceptance(admissions_path: Path, academic_year: int):
    processor = AcceptanceProcessor(admissions_path, academic_year, Path("/tmp/placeholder"))
    processor.load_data()
    processor.transform()
    processor.validate()
    return processor.result_df
