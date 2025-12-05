import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from processing.usa.constants import ENROLLMENT_LEVEL_ALL


class EnrollmentProcessor:
    def __init__(
        self,
        enrollment_path: Path,
        academic_year: int,
        field_map: Dict[str, str],
        level_value: int,
        output_path: Optional[Path] = None,
        tuition_path: Optional[Path] = None,
        tuition_fields: Optional[Dict[str, str]] = None,
        net_price_path: Optional[Path] = None,
        net_price_field: Optional[str] = None,
        graduation_rates_path: Optional[Path] = None,
        graduation_fields: Optional[Dict[str, int]] = None,
    ):
        self.enrollment_path = Path(enrollment_path)
        self.academic_year = academic_year
        self.field_map = field_map
        self.level_value = level_value
        self.output_path = Path(output_path) if output_path else None
        self.tuition_path = Path(tuition_path) if tuition_path else None
        self.tuition_fields = tuition_fields or {}
        self.net_price_path = Path(net_price_path) if net_price_path else None
        self.net_price_field = net_price_field
        self.graduation_rates_path = (
            Path(graduation_rates_path) if graduation_rates_path else None
        )
        self.graduation_fields = graduation_fields or {}

    def load_data(self):
        self.enrollment_df = pd.read_csv(self.enrollment_path)
        self.tuition_df = pd.read_csv(self.tuition_path) if self.tuition_path else None
        self.net_price_df = (
            pd.read_csv(self.net_price_path) if self.net_price_path else None
        )
        self.grad_rates_df = (
            pd.read_csv(self.graduation_rates_path)
            if self.graduation_rates_path
            else None
        )

    def filter_all_students(self):
        level_col = self.field_map["level"]
        self.enrollment_df = self.enrollment_df[
            self.enrollment_df[level_col] == self.level_value
        ]

    def transform(self):
        total_col = self.field_map["total"]
        intl_col = self.field_map["international"]

        total_enrolled = pd.to_numeric(self.enrollment_df[total_col], errors="coerce")
        international_enrolled = pd.to_numeric(
            self.enrollment_df[intl_col], errors="coerce"
        )

        result = pd.DataFrame()
        result["college_id"] = self.enrollment_df["UNITID"]
        result["academic_year"] = self.academic_year
        result["total_enrolled"] = total_enrolled
        result["international_enrolled"] = international_enrolled
        result["tuition"] = None
        result["out_of_state_tuition"] = None
        result["total_cost"] = None
        result["graduation_rate_4yr"] = None
        result["graduation_rate_6yr"] = None

        self.result_df = result.dropna(subset=["total_enrolled"])
        self.result_df = self.result_df[self.result_df["total_enrolled"] > 0]

    def attach_tuition(self):
        if self.tuition_df is None:
            return

        tuition_col = self.tuition_fields.get("tuition")
        out_state_col = self.tuition_fields.get("out_of_state_tuition")
        lookup = self.tuition_df.set_index("UNITID")

        if tuition_col:
            self.result_df["tuition"] = self.result_df["college_id"].map(
                lookup[tuition_col]
            )
        if out_state_col:
            self.result_df["out_of_state_tuition"] = self.result_df["college_id"].map(
                lookup[out_state_col]
            )

    def attach_net_price(self):
        if self.net_price_df is None or not self.net_price_field:
            return

        lookup = self.net_price_df.set_index("UNITID")
        self.result_df["total_cost"] = self.result_df["college_id"].map(
            lookup[self.net_price_field]
        )

    def attach_graduation_rates(self):
        if self.grad_rates_df is None or not self.graduation_fields:
            return

        cohort_value = self.graduation_fields["cohort_filter"]
        adjusted_code = self.graduation_fields["adjusted"]
        complete_4yr = self.graduation_fields["complete_4yr"]
        complete_5yr = self.graduation_fields["complete_5yr"]
        complete_6yr = self.graduation_fields["complete_6yr"]

        grad_df = self.grad_rates_df[self.grad_rates_df["COHORT"] == cohort_value]
        adjusted = grad_df[grad_df["CHRTSTAT"] == adjusted_code][
            ["UNITID", "GRTOTLT"]
        ].rename(columns={"GRTOTLT": "adjusted_cohort"})
        completed_4yr = grad_df[grad_df["CHRTSTAT"] == complete_4yr][
            ["UNITID", "GRTOTLT"]
        ].rename(columns={"GRTOTLT": "completions_4yr"})
        completed_5yr = grad_df[grad_df["CHRTSTAT"] == complete_5yr][
            ["UNITID", "GRTOTLT"]
        ].rename(columns={"GRTOTLT": "completions_5yr"})
        completed_6yr = grad_df[grad_df["CHRTSTAT"] == complete_6yr][
            ["UNITID", "GRTOTLT"]
        ].rename(columns={"GRTOTLT": "completions_6yr"})

        rates = (
            adjusted.merge(completed_4yr, on="UNITID", how="left")
            .merge(completed_5yr, on="UNITID", how="left")
            .merge(completed_6yr, on="UNITID", how="left")
            .fillna(0)
        )

        rates = rates[rates["adjusted_cohort"] > 0]
        rates["graduation_rate_4yr"] = (
            rates["completions_4yr"] / rates["adjusted_cohort"]
        ) * 100
        rates["graduation_rate_6yr"] = (
            (
                rates["completions_4yr"]
                + rates["completions_5yr"]
                + rates["completions_6yr"]
            )
            / rates["adjusted_cohort"]
        ) * 100
        rates["graduation_rate_4yr"] = (
            rates["graduation_rate_4yr"].clip(upper=100).round(2)
        )
        rates["graduation_rate_6yr"] = (
            rates["graduation_rate_6yr"].clip(upper=100).round(2)
        )

        lookup = rates.set_index("UNITID")
        self.result_df["graduation_rate_4yr"] = self.result_df["college_id"].map(
            lookup["graduation_rate_4yr"]
        )
        self.result_df["graduation_rate_6yr"] = self.result_df["college_id"].map(
            lookup["graduation_rate_6yr"]
        )

    def save(self):
        if self.output_path is None:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        self.load_data()
        self.filter_all_students()
        self.transform()
        self.attach_tuition()
        self.attach_net_price()
        self.attach_graduation_rates()
        self.save()
        return self.result_df


def process_enrollment(
    enrollment_path: Path,
    academic_year: int,
    field_map: Dict[str, str],
    level_value: int,
    output_path: Optional[Path] = None,
    tuition_path: Optional[Path] = None,
    tuition_fields: Optional[Dict[str, str]] = None,
    net_price_path: Optional[Path] = None,
    net_price_field: Optional[str] = None,
    graduation_rates_path: Optional[Path] = None,
    graduation_fields: Optional[Dict[str, int]] = None,
):
    processor = EnrollmentProcessor(
        enrollment_path=enrollment_path,
        academic_year=academic_year,
        field_map=field_map,
        level_value=level_value,
        output_path=output_path,
        tuition_path=tuition_path,
        tuition_fields=tuition_fields,
        net_price_path=net_price_path,
        net_price_field=net_price_field,
        graduation_rates_path=graduation_rates_path,
        graduation_fields=graduation_fields,
    )
    return processor.process()
