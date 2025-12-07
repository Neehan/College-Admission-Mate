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

LEVEL_GRADUATE = 1

IPEDS_COLUMNS_IC = ["UNITID", "CALSYS", "LEVEL5", "LEVEL6", "LEVEL7", "LEVEL8"]
IPEDS_MERGE_KEY = "UNITID"

DATA_DIR_USA = "data/USA/IPEDS"
PROCESSED_DIR = "data/USA/processed"

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

ENROLLMENT_OUTPUT = "enrollment.csv"
ACCEPTANCE_OUTPUT = "acceptance.csv"
FINANCIAL_AID_OUTPUT = "financial_aid.csv"
TESTS_SCORES_OUTPUT = "tests_and_scores.csv"
APPLICATION_REQUIREMENTS_OUTPUT = "application_requirements.csv"
COLLEGE_REQUIREMENTS_MAP_OUTPUT = "college_application_requirements_map.csv"

AWLEVEL_TO_DEGREE_TYPE = {
    3: "Associate",
    5: "Bachelor",
    7: "Master",
    17: "PhD",
    18: "Professional Doctorate",
    19: "Doctorate - Other",
}
UNDERGRAD_DEGREE_TYPES = {"Associate", "Bachelor"}

CIPCODE_VARNAME = "CIPCODE"
CIP_FREQUENCIES_SHEET = "Frequencies"
FIRST_MAJOR_CODE = 1
GRAND_TOTAL_CIP_CODE = 99.0

ENROLLMENT_LEVEL_ALL = 1
ENROLLMENT_LEVEL_UNDERGRAD = 2
ENROLLMENT_LEVEL_GRAD = 4

YEAR_FILE_CONFIGS = {
    2022: {
        "files": {
            "hd": "hd2022.csv",
            "ic": "ic2022.csv",
            "ic_ay": "ic2022_ay.csv",
            "completions": "c2022_a.csv",
            "cip_lookup": "c2022_a.xlsx",
            "enrollment": "effy2022.csv",
            "net_price": "sfa2122.csv",
            "graduation": "gr2022.csv",
            "admissions": "adm2022.csv",
        },
        "enrollment_fields": {
            "level": "EFFYLEV",
            "total": "EFYTOTLT",
            "international": "EFYNRALT",
        },
        "enrollment_level": ENROLLMENT_LEVEL_UNDERGRAD,
        "tuition_fields": {
            "tuition": "TUITION2",
            "out_of_state_tuition": "TUITION3",
        },
        "net_price_field": "NPIST2",  # average net price 2021-22 (students with aid)
        "graduation_fields": {
            "cohort_filter": 2,
            "adjusted": 12,
            "complete_4yr": 16,
            "complete_5yr": 17,
            "complete_6yr": 18,
        },
    },
    2023: {
        "files": {
            "hd": "HD2023.csv",
            "ic": "IC2023.csv",
            "ic_ay": "IC2023_AY.csv",
            "completions": "C2023_A.csv",
            "cip_lookup": "C2023_A.xlsx",
            "enrollment": "EFFY2023.csv",
            "net_price": "SFA2223.csv",
            "graduation": "GR2023.csv",
            "admissions": "ADM2023.csv",
        },
        "enrollment_fields": {
            "level": "EFFYLEV",
            "total": "EFYTOTLT",
            "international": "EFYNRALT",
        },
        "enrollment_level": ENROLLMENT_LEVEL_UNDERGRAD,
        "tuition_fields": {
            "tuition": "TUITION2",  # in-state average tuition FT undergrad
            "out_of_state_tuition": "TUITION3",
        },
        "net_price_field": "NPIST2",  # average net price (students with aid), 2022-23
        "graduation_fields": {
            "cohort_filter": 2,  # bachelor's subcohort
            "adjusted": 12,
            "complete_4yr": 16,
            "complete_5yr": 17,
            "complete_6yr": 18,
        },
    },
    2024: {
        "files": {
            "hd": "HD2024.csv",
            "ic": "IC2024.csv",
            "completions": "C2024_A.csv",
            "cip_lookup": "C2024_A.xlsx",
            "enrollment": "EFFY2024.csv",
        },
        "enrollment_fields": {
            "level": "EFFYLEV",
            "total": "EFYTOTLT",
            "international": "EFYNRALT",
        },
        "enrollment_level": ENROLLMENT_LEVEL_UNDERGRAD,
    },
}

FINANCIAL_AID_BUCKETS = [
    ("NPIS410", 0, 30000),
    ("NPIS420", 30001, 48000),
    ("NPIS430", 48001, 75000),
    ("NPIS440", 75001, 110000),
    ("NPIS450", 110001, None),
]

ADM_REQUIREMENTS = {
    "ADMCON1": ("gpa", "Secondary school GPA"),
    "ADMCON2": ("class_rank", "Secondary school rank"),
    "ADMCON3": ("transcript", "Secondary school record/transcript"),
    "ADMCON4": ("college_prep_program", "Completion of college-preparatory program"),
    "ADMCON5": ("recommendations", "Recommendations"),
    "ADMCON6": ("competencies", "Formal demonstration of competencies"),
    "ADMCON7": ("admission_tests", "Admission test scores"),
    "ADMCON8": ("english_proficiency", "English proficiency test"),
    "ADMCON9": ("other_test", "Other test (Wonderlic, etc.)"),
    "ADMCON10": ("work_experience", "Work experience"),
    "ADMCON11": ("essay", "Personal statement or essay"),
    "ADMCON12": ("legacy_status", "Legacy status"),
}

# Numeric transformations
CIP_MULTIPLIER = 100
PERCENTAGE_MULTIPLIER = 100
PERCENTAGE_DECIMALS = 2
MAX_PERCENTAGE = 100
MIN_GRADUATES = 0
MIN_COHORT_SIZE = 0
MIN_DENOMINATOR = 0

# IPEDS requirement codes
REQUIRED_CODE = 1
RECOMMENDED_CODE = 2
NOT_REQUIRED_CODE = 3
NOT_USED_CODE = 4
CONSIDERED_CODE = 5

# Common IPEDS columns
UNITID_COLUMN = "UNITID"

# File naming
REVISED_SUFFIX = "_rv"
CSV_EXTENSION = ".csv"
