from pathlib import Path
import pandas as pd
from usa.processing.base_processor import SingleFileProcessor
from usa.processing.constants import UNITID_COLUMN


class TestsScoresProcessor(SingleFileProcessor):

    def transform(self):
        df = self.data
        df.columns = df.columns.str.strip()

        sat_vr25 = df["SATVR25"]
        sat_vr75 = df["SATVR75"]
        sat_mt25 = df["SATMT25"]
        sat_mt75 = df["SATMT75"]
        act_cm25 = df["ACTCM25"]
        act_cm75 = df["ACTCM75"]
        act_en25 = df["ACTEN25"]
        act_en75 = df["ACTEN75"]
        act_mt25 = df["ACTMT25"]
        act_mt75 = df["ACTMT75"]

        sat_total25 = sat_vr25 + sat_mt25
        sat_total75 = sat_vr75 + sat_mt75

        records = []

        for college_id, s25, s75 in zip(df[UNITID_COLUMN], sat_total25, sat_total75):
            if pd.notna(s25) and pd.notna(s75):
                records.append({
                    "college_id": college_id,
                    "test_type": "sat",
                    "score_25th": str(int(s25)),
                    "score_75th": str(int(s75)),
                    "is_required": True,
                })

        for college_id, vr25, vr75 in zip(df[UNITID_COLUMN], sat_vr25, sat_vr75):
            if pd.notna(vr25) and pd.notna(vr75):
                records.append({
                    "college_id": college_id,
                    "test_type": "sat_reading",
                    "score_25th": str(int(vr25)),
                    "score_75th": str(int(vr75)),
                    "is_required": True,
                })

        for college_id, mt25, mt75 in zip(df[UNITID_COLUMN], sat_mt25, sat_mt75):
            if pd.notna(mt25) and pd.notna(mt75):
                records.append({
                    "college_id": college_id,
                    "test_type": "sat_math",
                    "score_25th": str(int(mt25)),
                    "score_75th": str(int(mt75)),
                    "is_required": True,
                })

        for college_id, a25, a75 in zip(df[UNITID_COLUMN], act_cm25, act_cm75):
            if pd.notna(a25) and pd.notna(a75):
                records.append({
                    "college_id": college_id,
                    "test_type": "act",
                    "score_25th": str(int(a25)),
                    "score_75th": str(int(a75)),
                    "is_required": True,
                })

        for college_id, e25, e75 in zip(df[UNITID_COLUMN], act_en25, act_en75):
            if pd.notna(e25) and pd.notna(e75):
                records.append({
                    "college_id": college_id,
                    "test_type": "act_english",
                    "score_25th": str(int(e25)),
                    "score_75th": str(int(e75)),
                    "is_required": True,
                })

        for college_id, m25, m75 in zip(df[UNITID_COLUMN], act_mt25, act_mt75):
            if pd.notna(m25) and pd.notna(m75):
                records.append({
                    "college_id": college_id,
                    "test_type": "act_math",
                    "score_25th": str(int(m25)),
                    "score_75th": str(int(m75)),
                    "is_required": True,
                })

        self.result_df = pd.DataFrame(records).drop_duplicates()


def process_tests_scores(admissions_path: Path):
    processor = TestsScoresProcessor(admissions_path, Path("/tmp/placeholder"))
    processor.load_data()
    processor.transform()
    processor.validate()
    return processor.result_df
