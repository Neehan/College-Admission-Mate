from pathlib import Path
import pandas as pd
from usa.processing.base_processor import BaseProcessor
from usa.processing.constants import UNITID_COLUMN


class FinancialAidProcessor(BaseProcessor):

    def __init__(self, sfa_path: Path, academic_year: int, buckets: list, output_path: Path):
        super().__init__(output_path)
        self.sfa_path = Path(sfa_path)
        self.academic_year = academic_year
        self.buckets = buckets
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.sfa_path)

    def transform(self):
        records = []
        for col, min_income, max_income in self.buckets:
            if col not in self.data.columns:
                continue

            for college_id, avg_net in zip(self.data[UNITID_COLUMN], self.data[col]):
                if pd.isna(avg_net):
                    continue

                records.append({
                    "college_id": college_id,
                    "academic_year": self.academic_year,
                    "income_bracket_range_min": min_income,
                    "income_bracket_range_max": max_income,
                    "avg_net_cost_after_aid": avg_net,
                })

        self.result_df = pd.DataFrame(records)


def process_financial_aid(sfa_path: Path, academic_year: int, buckets: list):
    processor = FinancialAidProcessor(sfa_path, academic_year, buckets, Path("/tmp/placeholder"))
    processor.load_data()
    processor.transform()
    processor.validate()
    return processor.result_df
