import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple


class FinancialAidProcessor:
    def __init__(
        self,
        sfa_path: Path,
        academic_year: int,
        buckets: List[Tuple[str, int, Optional[int]]],
        output_path: Optional[Path] = None,
    ):
        self.sfa_path = Path(sfa_path)
        self.academic_year = academic_year
        self.buckets = buckets
        self.output_path = Path(output_path) if output_path else None

    def load_data(self):
        self.sfa_df = pd.read_csv(self.sfa_path)

    def transform(self):
        records = []
        for col, min_income, max_income in self.buckets:
            if col not in self.sfa_df.columns:
                continue
            values = pd.to_numeric(self.sfa_df[col], errors="coerce")
            for college_id, avg_net in zip(self.sfa_df["UNITID"], values):
                if pd.isna(avg_net):
                    continue
                records.append(
                    {
                        "college_id": college_id,
                        "academic_year": self.academic_year,
                        "income_bracket_range_min": min_income,
                        "income_bracket_range_max": max_income,
                        "avg_aid": None,
                        "avg_net_cost_after_aid": avg_net,
                    }
                )
        self.result_df = pd.DataFrame(records)

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


def process_financial_aid(
    sfa_path: Path,
    academic_year: int,
    buckets: List[Tuple[str, int, Optional[int]]],
    output_path: Optional[Path] = None,
):
    processor = FinancialAidProcessor(sfa_path, academic_year, buckets, output_path)
    return processor.process()
