from pathlib import Path
import pandas as pd
from usa.processing.base_processor import MultiFileProcessor
from usa.processing.constants import (
    LOCALE_TO_SETTING_TYPE,
    CARNEGIE_LIBERAL_ARTS_CODES,
    CONTROL_CODE_PUBLIC,
    CALENDAR_SYSTEM_MAP,
    COUNTRY_USA,
    LEVEL_GRADUATE,
    UNITID_COLUMN,
    REQUIRED_FIELDS_COLLEGE_METADATA,
)


class CollegeMetadataProcessor(MultiFileProcessor):

    def __init__(self, hd_path: Path, ic_path: Path, output_path: Path):
        super().__init__({"hd": hd_path, "ic": ic_path}, output_path)

    def transform(self):
        hd = self.data["hd"]
        ic = self.data["ic"][[UNITID_COLUMN, "CALSYS", "LEVEL5", "LEVEL6", "LEVEL7", "LEVEL8"]]
        merged = hd.merge(ic, on=UNITID_COLUMN, how="left")

        self.result_df = pd.DataFrame({
            "college_id": merged[UNITID_COLUMN],
            "name": merged["INSTNM"],
            "website": merged["WEBADDR"],
            "admissions_website": merged["ADMINURL"],
            "financial_aid_website": merged["FAIDURL"],
            "application_website": merged["APPLURL"],
            "country": COUNTRY_USA,
            "state": merged["STABBR"],
            "city": merged["CITY"],
            "is_liberal_arts_college": merged["C21BASIC"].isin(CARNEGIE_LIBERAL_ARTS_CODES),
            "has_research_opportunities": (
                (merged["LEVEL5"] == LEVEL_GRADUATE) |
                (merged["LEVEL6"] == LEVEL_GRADUATE) |
                (merged["LEVEL7"] == LEVEL_GRADUATE) |
                (merged["LEVEL8"] == LEVEL_GRADUATE)
            ),
            "setting_type": merged["LOCALE"].map(LOCALE_TO_SETTING_TYPE),
            "is_public": merged["CONTROL"] == CONTROL_CODE_PUBLIC,
            "calendar_system": merged["CALSYS"].map(CALENDAR_SYSTEM_MAP),
        })

    def validate(self):
        self.result_df = self.result_df.dropna(subset=REQUIRED_FIELDS_COLLEGE_METADATA)


def process_college_metadata(hd_path: Path, ic_path: Path, output_path: Path):
    processor = CollegeMetadataProcessor(hd_path, ic_path, output_path)
    return processor.process()
