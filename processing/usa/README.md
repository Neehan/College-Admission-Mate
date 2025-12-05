# USA Data Processing

Pipeline for processing IPEDS (Integrated Postsecondary Education Data System) data for US colleges.

## Data Sources

All data is sourced from [IPEDS Data Center](https://nces.ed.gov/ipeds/datacenter/).

### Files Used

- **HD2024.csv** - Institutional Characteristics (Directory Information)
- **IC2024.csv** - Institutional Characteristics (Additional Info)
- **C2024_A.csv** - Completions data (degrees awarded)
- **C2024_A.xlsx** - Data dictionary for completions

## Output Tables

### college_metadata.csv
Basic information about colleges including name, location, websites, type, and characteristics.

**Fields:** college_id, name, website, admissions_website, financial_aid_website, application_website, country, state, city, is_liberal_arts_college, has_research_opportunities, setting_type, is_public, calendar_system

**Count:** ~4,660 colleges

### departments.csv
Academic departments/programs using 4-digit CIP codes.

**Fields:** department_id, department_name

**Count:** 403 departments

**Examples:**
- 1107: Computer Science
- 2701: Mathematics, General
- 2601: Biology, General

### degrees.csv
Degrees awarded by college, department, and degree type for academic year 2024.

**Fields:** college_id, academic_year, department_id, degree_type, total_graduates, total_female_graduates, total_international_graduates

**Count:** ~132,000 records

**Degree Types:** Associate, Bachelor, Master, PhD, Professional Doctorate, Doctorate - Other

## Usage

```bash
# Run full pipeline
python3 -m processing.usa.main
```

## Module Structure

```
processing/usa/
├── README.md
├── main.py                  # Main pipeline
├── constants.py             # All constants and mappings
├── college_metadata.py      # Process college metadata
└── degrees.py              # Process degrees and departments
```

## Notes

- Only first majors are included (MAJORNUM = 1)
- Certificate programs are excluded
- CIP codes are truncated to 4 digits for broader department categories
- Grand total (CIP 99.0) is filtered out
