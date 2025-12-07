# USA Data Processing

Pipeline for processing IPEDS (Integrated Postsecondary Education Data System) data for US colleges.

## Data Sources

All data is sourced from [IPEDS Data Center](https://nces.ed.gov/ipeds/datacenter/).

### Files Used (per year)

For each year you want to process (e.g., 2024, 2023, extendable to 2022):
- **HD{year}.csv** and **IC{year}.csv** — directory + institutional characteristics (for college metadata)
- **C{year}_A.csv** and **C{year}_A.xlsx** — completions + CIP dictionary (for degrees/departments)
- **Enrollment file** — **EFFY{year}.csv** (fall enrollment, all students) or **ef{year}a.csv** if EFFY is not available
- **IC{year}_AY.csv** — tuition/fees (optional; enriches enrollment with tuition/out-of-state tuition)
- **SFA{yy}{yy+1}.csv** — net price (optional; enriches enrollment total_cost; e.g., **SFA2223.csv** for 2023 cycle)
- **GR{year}.csv** — graduation outcomes (optional; enriches enrollment graduation_rate_4yr/6yr)

File names per year are configured in `processing/usa/constants.py::YEAR_FILE_CONFIGS`; adjust there when adding another year or if filenames differ. The pipeline looks for `data/USA/{year}/unzipped` (prefers revised `*_rv.csv` when available).

### Relevant columns by table

- **college_metadata** (from HD/IC):
  - `HD{year}.csv`: `UNITID` (IPEDS id), `INSTNM` (name), `WEBADDR` (site), `ADMINURL` (admissions), `FAIDURL` (financial aid), `APPLURL` (application), `STABBR` (state), `CITY`, `LOCALE` (urban/suburban/rural code), `CONTROL` (public/private), `C21BASIC` (Carnegie code)
  - `IC{year}.csv`: `UNITID`, `CALSYS` (calendar system), `LEVEL5/6/7/8` (grad-level flags)
- **degrees/departments** (from completions + CIP dictionary):
  - `C{year}_A.csv`: `UNITID`, `CIPCODE` (program), `MAJORNUM` (first major filter), `AWLEVEL` (award level), `CTOTALT` (total grads), `CTOTALW` (female grads), `CNRALT` (international grads)
  - `C{year}_A.xlsx` (sheet “Frequencies”): `VarName/varname` (variable id), `CodeValue/codevalue` (CIP), `ValueLabel/valuelabel` (CIP title)
- **enrollment**:
  - `EFFY{year}.csv` (or `ef{year}a.csv` if no EFFY): `UNITID`, `EFFYLEV/EFALEVEL` (level filter), `EFYTOTLT/EFTOTLT` (total enrollment), `EFYNRALT/EFNRALT` (international enrollment)
  - `IC{year}_AY.csv` (optional tuition): `UNITID`, `TUITION2` (in-state), `TUITION3` (out-of-state)
  - `SFA{yy}{yy+1}.csv` (optional net price): `UNITID`, `NPIST2` (avg net price for students with aid)
  - `GR{year}.csv` (optional grad rates): `UNITID`, `COHORT` (subcohort id), `CHRTSTAT` (status code), `GRTOTLT` (counts used to compute 4yr/6yr rates)

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
Undergraduate degrees awarded by college, department, and degree type (year-specific; Associate/Bachelor only).

**Fields:** college_id, academic_year, department_id, degree_type, total_graduates, total_female_graduates, total_international_graduates

**Degree Types:** Associate, Bachelor, Master, PhD, Professional Doctorate, Doctorate - Other

### enrollment.csv
Enrollment, tuition, net price proxy, and grad rates per college/year.

**Fields:** college_id, academic_year, total_enrolled, international_enrolled, tuition, out_of_state_tuition, total_cost, graduation_rate_4yr, graduation_rate_6yr

### acceptance.csv
Acceptance counts and rates per college/year (from ADM files; international fields null).

**Fields:** college_id, academic_year, accepted_total, accepted_female, accepted_international, acceptance_rate, acceptance_rate_female, acceptance_rate_international

### financial_aid.csv
Average net price by income bracket per college/year (from SFA files).

**Fields:** college_id, academic_year, income_bracket_range_min, income_bracket_range_max, avg_aid, avg_net_cost_after_aid

### tests_and_scores.csv
SAT/ACT percentile bands per college (from ADM files).

**Fields:** college_id, test_type (sat/act), score_25th, score_75th, is_required

## Usage

```bash
# Run full pipeline (processes every available year under data/USA/*/unzipped*)
python3 -m processing.usa.main
```

## Module Structure

```
processing/usa/
├── README.md
├── main.py                  # Main pipeline
├── constants.py             # All constants and mappings
├── college_metadata.py      # Process college metadata
├── degrees.py               # Process degrees and departments
└── enrollment.py            # Process enrollment, tuition, net price, grad rates
```

## Notes

- Only first majors are included (MAJORNUM = 1) for completions
- Certificate programs are excluded
- CIP codes are truncated to 4 digits for broader department categories
- Grand total (CIP 99.0) is filtered out
- Processed outputs are written to `data/USA/processed` and include all available academic years
