import pandas as pd
from pathlib import Path
from typing import Optional


class TestsScoresProcessor:
    def __init__(self, admissions_path: Path, output_path: Optional[Path] = None):
        self.admissions_path = Path(admissions_path)
        self.output_path = Path(output_path) if output_path else None

    def load_data(self):
        self.admissions_df = pd.read_csv(self.admissions_path)

    def _combine_sat(self, vr_col_25, vr_col_75, mt_col_25, mt_col_75):
        vr25 = pd.to_numeric(self.admissions_df.get(vr_col_25), errors="coerce")
        vr75 = pd.to_numeric(self.admissions_df.get(vr_col_75), errors="coerce")
        mt25 = pd.to_numeric(self.admissions_df.get(mt_col_25), errors="coerce")
        mt75 = pd.to_numeric(self.admissions_df.get(mt_col_75), errors="coerce")
        total25 = vr25.fillna(0) + mt25.fillna(0)
        total75 = vr75.fillna(0) + mt75.fillna(0)
        total25 = total25.where(~(vr25.isna() & mt25.isna()))
        total75 = total75.where(~(vr75.isna() & mt75.isna()))
        return total25, total75

    def _act_composite(self, cm25_col, cm75_col):
        cm25 = pd.to_numeric(self.admissions_df.get(cm25_col), errors="coerce")
        cm75 = pd.to_numeric(self.admissions_df.get(cm75_col), errors="coerce")
        return cm25, cm75

    def transform(self):
        records = []
        sat25, sat75 = self._combine_sat("SATVR25", "SATVR75", "SATMT25", "SATMT75")
        act25, act75 = self._act_composite("ACTCM25", "ACTCM75")

        for college_id, s25, s75 in zip(self.admissions_df["UNITID"], sat25, sat75):
            if pd.isna(s25) or pd.isna(s75):
                continue
            records.append(
                {
                    "college_id": college_id,
                    "test_type": "sat",
                    "score_25th": str(int(s25)),
                    "score_75th": str(int(s75)),
                    "is_required": True,
                }
            )

        for college_id, a25, a75 in zip(self.admissions_df["UNITID"], act25, act75):
            if pd.isna(a25) or pd.isna(a75):
                continue
            records.append(
                {
                    "college_id": college_id,
                    "test_type": "act",
                    "score_25th": str(int(a25)),
                    "score_75th": str(int(a75)),
                    "is_required": True,
                }
            )

        self.result_df = pd.DataFrame(records).drop_duplicates()

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


def process_tests_scores(admissions_path: Path, output_path: Optional[Path] = None):
    processor = TestsScoresProcessor(admissions_path, output_path)
    return processor.process()
