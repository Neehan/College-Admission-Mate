import pandas as pd
from pathlib import Path
from processing.usa.constants import (
    LOCALE_TO_SETTING_TYPE,
    CARNEGIE_LIBERAL_ARTS_CODES,
    CONTROL_CODE_PUBLIC,
    CALENDAR_SYSTEM_MAP,
    COUNTRY_USA,
    LEVEL_GRADUATE,
    IPEDS_COLUMNS_IC,
    IPEDS_MERGE_KEY,
)


class LocaleMapper:
    @staticmethod
    def map(locale_code):
        if pd.isna(locale_code):
            return None
        return LOCALE_TO_SETTING_TYPE.get(int(locale_code))


class CarnegieMapper:
    @staticmethod
    def is_liberal_arts(carnegie_code):
        if pd.isna(carnegie_code):
            return False
        return int(carnegie_code) in CARNEGIE_LIBERAL_ARTS_CODES


class ControlMapper:
    @staticmethod
    def is_public(control_code):
        if pd.isna(control_code):
            return None
        return int(control_code) == CONTROL_CODE_PUBLIC


class CalendarSystemMapper:
    @staticmethod
    def map(calsys_code):
        if pd.isna(calsys_code):
            return None
        return CALENDAR_SYSTEM_MAP.get(int(calsys_code))


class CollegeMetadataProcessor:
    def __init__(self, hd_path, ic_path, output_path):
        self.hd_path = Path(hd_path)
        self.ic_path = Path(ic_path)
        self.output_path = Path(output_path)

    def load_data(self):
        self.hd_df = pd.read_csv(self.hd_path)
        self.ic_df = pd.read_csv(self.ic_path)

    def merge_datasets(self):
        self.merged_df = self.hd_df.merge(
            self.ic_df[IPEDS_COLUMNS_IC], on=IPEDS_MERGE_KEY, how="left"
        )

    def transform(self):
        result = pd.DataFrame()

        result["college_id"] = self.merged_df["UNITID"]
        result["name"] = self.merged_df["INSTNM"]
        result["website"] = self.merged_df["WEBADDR"]
        result["admissions_website"] = self.merged_df["ADMINURL"]
        result["financial_aid_website"] = self.merged_df["FAIDURL"]
        result["application_website"] = self.merged_df["APPLURL"]
        result["country"] = COUNTRY_USA
        result["state"] = self.merged_df["STABBR"]
        result["city"] = self.merged_df["CITY"]

        result["is_liberal_arts_college"] = self.merged_df["C21BASIC"].apply(
            CarnegieMapper.is_liberal_arts
        )

        result["has_research_opportunities"] = (
            (self.merged_df["LEVEL5"] == LEVEL_GRADUATE)
            | (self.merged_df["LEVEL6"] == LEVEL_GRADUATE)
            | (self.merged_df["LEVEL7"] == LEVEL_GRADUATE)
            | (self.merged_df["LEVEL8"] == LEVEL_GRADUATE)
        )

        result["setting_type"] = self.merged_df["LOCALE"].apply(LocaleMapper.map)
        result["is_public"] = self.merged_df["CONTROL"].apply(ControlMapper.is_public)
        result["calendar_system"] = self.merged_df["CALSYS"].apply(
            CalendarSystemMapper.map
        )

        self.result_df = result

    def save(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        self.load_data()
        self.merge_datasets()
        self.transform()
        self.save()
        return self.result_df


def process_college_metadata(hd_path, ic_path, output_path):
    processor = CollegeMetadataProcessor(hd_path, ic_path, output_path)
    return processor.process()
