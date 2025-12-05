LOCALE_TO_SETTING_TYPE = {
    11: "urban",
    12: "urban",
    13: "urban",
    21: "suburban",
    22: "suburban",
    23: "suburban",
    31: "rural",
    32: "rural",
    33: "rural",
    41: "rural",
    42: "rural",
    43: "rural",
}

CARNEGIE_LIBERAL_ARTS_CODES = {21, 22, 23}

CONTROL_CODE_PUBLIC = 1

CALENDAR_SYSTEM_MAP = {1: "semester", 2: "quarter", 3: "trimester", 4: "other"}

COUNTRY_USA = "USA"
ACADEMIC_YEAR_2024 = 2024

LEVEL_GRADUATE = 1

IPEDS_COLUMNS_IC = ["UNITID", "CALSYS", "LEVEL5", "LEVEL6", "LEVEL7", "LEVEL8"]
IPEDS_MERGE_KEY = "UNITID"

DATA_DIR_USA_2024 = "data/USA/2024"
UNZIPPED_DIR = "unzipped"
PROCESSED_DIR = "processed"

HD2024_FILENAME = "HD2024.csv"
IC2024_FILENAME = "IC2024.csv"
COLLEGE_METADATA_OUTPUT = "college_metadata.csv"

REQUIRED_FIELDS_COLLEGE_METADATA = [
    "website",
    "admissions_website",
    "financial_aid_website",
    "application_website",
    "setting_type",
]

C2024_A_CSV_FILENAME = "C2024_A.csv"
C2024_A_XLSX_FILENAME = "C2024_A.xlsx"
DEGREES_OUTPUT = "degrees.csv"
DEPARTMENTS_OUTPUT = "departments.csv"

AWLEVEL_TO_DEGREE_TYPE = {
    3: "Associate",
    5: "Bachelor",
    7: "Master",
    17: "PhD",
    18: "Professional Doctorate",
    19: "Doctorate - Other",
}

CIPCODE_VARNAME = "CIPCODE"
CIP_FREQUENCIES_SHEET = "Frequencies"
FIRST_MAJOR_CODE = 1
GRAND_TOTAL_CIP_CODE = 99.0
