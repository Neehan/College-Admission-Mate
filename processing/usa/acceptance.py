import pandas as pd
from pathlib import Path
from typing import Optional


class AcceptanceProcessor:
    def __init__(self, admissions_path: Path, academic_year: int, output_path: Optional[Path] = None):
        self.admissions_path = Path(admissions_path)
        self.academic_year = academic_year
        self.output_path = Path(output_path) if output_path else None

    def load_data(self):
        self.admissions_df = pd.read_csv(self.admissions_path)

    def _safe_rate(self, numerator, denominator):
        if pd.isna(numerator) or pd.isna(denominator) or denominator <= 0:
            return None
        return float(numerator) / float(denominator) * 100

    def transform(self):
        applicants_total = pd.to_numeric(self.admissions_df.get("APPLCN"), errors="coerce")
        applicants_female = pd.to_numeric(self.admissions_df.get("APPLCNW"), errors="coerce")
        admitted_total = pd.to_numeric(self.admissions_df.get("ADMSSN"), errors="coerce")
        admitted_female = pd.to_numeric(self.admissions_df.get("ADMSSNW"), errors="coerce")

        result = pd.DataFrame()
        result["college_id"] = self.admissions_df["UNITID"]
        result["academic_year"] = self.academic_year
        result["accepted_total"] = admitted_total.astype("Int64")
        result["accepted_female"] = admitted_female.astype("Int64")
        result["accepted_international"] = None
        result["acceptance_rate"] = [
            round(self._safe_rate(a, b), 2) if self._safe_rate(a, b) is not None else None
            for a, b in zip(admitted_total, applicants_total)
        ]
        result["acceptance_rate_female"] = [
            round(self._safe_rate(a, b), 2) if self._safe_rate(a, b) is not None else None
            for a, b in zip(admitted_female, applicants_female)
        ]
        result["acceptance_rate_international"] = None

        self.result_df = result.dropna(subset=["accepted_total"])
        self.result_df = self.result_df[
            (self.result_df["accepted_total"] > 0) & (self.result_df["acceptance_rate"] > 0)
        ]

    def save(self):
        if self.output_path is None:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        self.load_data()
        self.transform()
        self.save()
        return self.result_df


def process_acceptance(admissions_path: Path, academic_year: int, output_path: Optional[Path] = None):
    processor = AcceptanceProcessor(admissions_path, academic_year, output_path)
    return processor.process()
