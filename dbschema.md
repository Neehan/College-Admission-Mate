# Postgres Database Schema

# Tables

## `college_metadata`

- `college_id` (PRIMARY KEY, SERIAL)
- `name` (VARCHAR(255) NOT NULL)
- `website` (VARCHAR(500))
- `financial_aid_website` (VARCHAR(500))
- `application_website` (VARCHAR(500))
- `country` (VARCHAR(100) NOT NULL)
- `state` (VARCHAR(100))
- `city` (VARCHAR(100))
- `known_for` (TEXT)
- `is_liberal_arts_college` (BOOLEAN DEFAULT FALSE)
- `housing_guaranteed_years` (INT)
- `has_research_opportunities` (BOOLEAN DEFAULT FALSE)
- `study_abroad_programs_count` (INT)
- `setting_type` (VARCHAR(20)) -- urban/suburban/rural
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: (country, is_liberal_arts_college)

## `enrollment`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `academic_year` (INT NOT NULL)
- `total_enrolled` (INT)
- `international_enrolled` (INT)
- `tuition` (DECIMAL(10,2))
- `out_of_state_tuition` (DECIMAL(10,2))
- `total_cost` (DECIMAL(10,2))
- `graduation_rate_4yr` (DECIMAL(5,2)) -- percentage
- `graduation_rate_6yr` (DECIMAL(5,2)) -- percentage
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

PRIMARY KEY: (college_id, academic_year)
INDEX: (college_id, academic_year, total_cost)

## `financial_aid`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `academic_year` (INT NOT NULL)
- `income_bracket_range_min` (DECIMAL(12,2) NOT NULL)
- `income_bracket_range_max` (DECIMAL(12,2) NOT NULL)
- `avg_aid` (DECIMAL(10,2))
- `avg_net_cost_after_aid` (DECIMAL(10,2))

PRIMARY KEY: (college_id, academic_year, income_bracket_range_min, income_bracket_range_max)
INDEX: (college_id, income_bracket_range_min, income_bracket_range_max, avg_net_cost_after_aid)

## `tests_and_scores`

- `id` (PRIMARY KEY, SERIAL)
- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `test_type` (VARCHAR(50) NOT NULL) -- sat/act/toefl/ielts/duolingo/a_level/gaokao/eju
- `score_25th` (VARCHAR(50)) -- 25th percentile score (e.g., "1400", "AAB", "650")
- `score_75th` (VARCHAR(50)) -- 75th percentile score (e.g., "1550", "A*A*A", "720")
- `is_required` (BOOLEAN DEFAULT TRUE) -- vs optional/test-optional
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: (college_id, test_type)

## `acceptance`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `academic_year` (INT NOT NULL)
- `accepted_total` (INT)
- `accepted_female` (INT)
- `accepted_international` (INT)
- `acceptance_rate` (DECIMAL(5,2))
- `acceptance_rate_female` (DECIMAL(5,2))
- `acceptance_rate_international` (DECIMAL(5,2))
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

PRIMARY KEY: (college_id, academic_year)
INDEX: (college_id, academic_year, acceptance_rate, acceptance_rate_female, acceptance_rate_international)

## `college_world_rank`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `year_reported` (INT NOT NULL)
- `ranking_system` (VARCHAR(50) NOT NULL) -- usnews/qs/times/shanghai
- `overall_rank` (INT)
- `source_url` (VARCHAR(500))
- `education_quality_rank` (INT)
- `faculty_quality_rank` (INT)
- `publications_rank` (INT)
- `alumni_employment_rank` (INT)
- `influence_rank` (INT)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

PRIMARY KEY: (college_id, year_reported, ranking_system)
INDEX: (college_id, year_reported, education_quality_rank)

## `degrees_offered`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `degree_type` (VARCHAR(50) NOT NULL) -- BS/BA/MS/MA/PhD/MD/JD
- `department` (VARCHAR(255) NOT NULL)
- `duration_years` (DECIMAL(3,1))
- `department_us_news_rank` (INT)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

PRIMARY KEY: (college_id, degree_type, department)
INDEX: (college_id, duration_years, degree_type)

## `scholarships`

- `id` (PRIMARY KEY, SERIAL)
- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `scholarship_name` (VARCHAR(255) NOT NULL)
- `eligibility_conditions` (TEXT)
- `awarded_amount` (DECIMAL(10,2))
- `internationals_eligible` (BOOLEAN DEFAULT FALSE)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: (college_id, internationals_eligible)


## `application_deadlines`

- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `academic_year` (INT NOT NULL)
- `deadline_type` (VARCHAR(50) NOT NULL) -- early_action/early_decision/regular/rolling
- `deadline_date` (DATE)
- `decision_date` (DATE)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

PRIMARY KEY: (college_id, academic_year, deadline_type)
INDEX: (college_id, academic_year, deadline_type)

## `application_requirements`

- `id` (PRIMARY KEY, SERIAL)
- `requirement_type` (VARCHAR(100) NOT NULL) -- essay/interview/portfolio/recommendation_letter/transcript
- `details` (TEXT)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: (requirement_type)

## `college_application_requirements_map`

- `id` (PRIMARY KEY, SERIAL)
- `college_id` (INT NOT NULL, FOREIGN KEY REFERENCES college_metadata(college_id))
- `requirement_id` (INT NOT NULL, FOREIGN KEY REFERENCES application_requirements(id))
- `is_optional` (BOOLEAN DEFAULT TRUE)
- `additional_notes` (TEXT)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: (college_id, requirement_id)