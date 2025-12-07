from pathlib import Path
import pandas as pd
from usa.processing.base_processor import BaseProcessor
from usa.processing.constants import (
    UNITID_COLUMN,
    PERCENTAGE_MULTIPLIER,
    PERCENTAGE_DECIMALS,
    MAX_PERCENTAGE,
    MIN_COHORT_SIZE,
)


class EnrollmentProcessor(BaseProcessor):

    def __init__(
        self,
        enrollment_path: Path,
        academic_year: int,
        field_map: dict,
        level_value: int,
        output_path: Path,
        tuition_path: Path,
        tuition_fields: dict,
        net_price_path: Path,
        net_price_field: str,
        graduation_rates_path: Path,
        graduation_fields: dict,
    ):
        super().__init__(output_path)
        self.enrollment_path = Path(enrollment_path)
        self.academic_year = academic_year
        self.field_map = field_map
        self.level_value = level_value
        self.tuition_path = Path(tuition_path) if tuition_path else None
        self.tuition_fields = tuition_fields
        self.net_price_path = Path(net_price_path) if net_price_path else None
        self.net_price_field = net_price_field
        self.graduation_rates_path = Path(graduation_rates_path) if graduation_rates_path else None
        self.graduation_fields = graduation_fields
        self.data = {}

    def load_data(self):
        self.data["enrollment"] = pd.read_csv(self.enrollment_path)
        if self.tuition_path:
            self.data["tuition"] = pd.read_csv(self.tuition_path)
        if self.net_price_path:
            self.data["net_price"] = pd.read_csv(self.net_price_path)
        if self.graduation_rates_path:
            self.data["graduation"] = pd.read_csv(self.graduation_rates_path)

    def transform(self):
        enrollment = self.data["enrollment"]
        enrollment = enrollment[enrollment[self.field_map["level"]] == self.level_value]

        self.result_df = pd.DataFrame({
            "college_id": enrollment[UNITID_COLUMN],
            "academic_year": self.academic_year,
            "total_enrolled": enrollment[self.field_map["total"]],
            "international_enrolled": enrollment[self.field_map["international"]],
            "tuition": None,
            "out_of_state_tuition": None,
            "total_cost": None,
            "graduation_rate_4yr": None,
            "graduation_rate_6yr": None,
        })

        self._attach_tuition()
        self._attach_net_price()
        self._attach_graduation_rates()

    def _attach_tuition(self):
        if "tuition" not in self.data:
            return

        tuition_lookup = self.data["tuition"].set_index(UNITID_COLUMN)

        tuition_col = self.tuition_fields["tuition"]
        out_state_col = self.tuition_fields["out_of_state_tuition"]

        self.result_df["tuition"] = self.result_df["college_id"].map(tuition_lookup[tuition_col])
        self.result_df["out_of_state_tuition"] = self.result_df["college_id"].map(tuition_lookup[out_state_col])

    def _attach_net_price(self):
        if "net_price" not in self.data:
            return

        net_price_lookup = self.data["net_price"].set_index(UNITID_COLUMN)
        self.result_df["total_cost"] = self.result_df["college_id"].map(net_price_lookup[self.net_price_field])

    def _attach_graduation_rates(self):
        if "graduation" not in self.data:
            return

        grad_df = self.data["graduation"]
        cohort_value = self.graduation_fields["cohort_filter"]
        adjusted_code = self.graduation_fields["adjusted"]
        complete_4yr = self.graduation_fields["complete_4yr"]
        complete_5yr = self.graduation_fields["complete_5yr"]
        complete_6yr = self.graduation_fields["complete_6yr"]

        grad_df = grad_df[grad_df["COHORT"] == cohort_value]

        adjusted = grad_df[grad_df["CHRTSTAT"] == adjusted_code][[UNITID_COLUMN, "GRTOTLT"]].rename(
            columns={"GRTOTLT": "adjusted_cohort"}
        )
        completed_4yr = grad_df[grad_df["CHRTSTAT"] == complete_4yr][[UNITID_COLUMN, "GRTOTLT"]].rename(
            columns={"GRTOTLT": "completions_4yr"}
        )
        completed_5yr = grad_df[grad_df["CHRTSTAT"] == complete_5yr][[UNITID_COLUMN, "GRTOTLT"]].rename(
            columns={"GRTOTLT": "completions_5yr"}
        )
        completed_6yr = grad_df[grad_df["CHRTSTAT"] == complete_6yr][[UNITID_COLUMN, "GRTOTLT"]].rename(
            columns={"GRTOTLT": "completions_6yr"}
        )

        rates = (
            adjusted.merge(completed_4yr, on=UNITID_COLUMN, how="left")
            .merge(completed_5yr, on=UNITID_COLUMN, how="left")
            .merge(completed_6yr, on=UNITID_COLUMN, how="left")
            .fillna(MIN_COHORT_SIZE)
        )

        rates = rates[rates["adjusted_cohort"] > MIN_COHORT_SIZE]
        rates["graduation_rate_4yr"] = (
            (rates["completions_4yr"] / rates["adjusted_cohort"]) * PERCENTAGE_MULTIPLIER
        ).clip(upper=MAX_PERCENTAGE).round(PERCENTAGE_DECIMALS)
        rates["graduation_rate_6yr"] = (
            ((rates["completions_4yr"] + rates["completions_5yr"] + rates["completions_6yr"]) / rates["adjusted_cohort"]) * PERCENTAGE_MULTIPLIER
        ).clip(upper=MAX_PERCENTAGE).round(PERCENTAGE_DECIMALS)

        grad_lookup = rates.set_index(UNITID_COLUMN)
        self.result_df["graduation_rate_4yr"] = self.result_df["college_id"].map(grad_lookup["graduation_rate_4yr"])
        self.result_df["graduation_rate_6yr"] = self.result_df["college_id"].map(grad_lookup["graduation_rate_6yr"])

    def validate(self):
        self.result_df = self.result_df.dropna(subset=["total_enrolled"])
        self.result_df = self.result_df[self.result_df["total_enrolled"] > MIN_COHORT_SIZE]


def process_enrollment(
    enrollment_path: Path,
    academic_year: int,
    field_map: dict,
    level_value: int,
    tuition_path: Path,
    tuition_fields: dict,
    net_price_path: Path,
    net_price_field: str,
    graduation_rates_path: Path,
    graduation_fields: dict,
):
    processor = EnrollmentProcessor(
        enrollment_path,
        academic_year,
        field_map,
        level_value,
        Path("/tmp/placeholder"),
        tuition_path,
        tuition_fields,
        net_price_path,
        net_price_field,
        graduation_rates_path,
        graduation_fields,
    )
    processor.load_data()
    processor.transform()
    processor.validate()
    return processor.result_df
