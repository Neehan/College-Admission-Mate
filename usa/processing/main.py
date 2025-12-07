from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from usa.processing.college_metadata import process_college_metadata
from usa.processing.degrees import process_degrees
from usa.processing.enrollment import process_enrollment
from usa.processing.acceptance import process_acceptance
from usa.processing.financial_aid import process_financial_aid
from usa.processing.tests_scores import process_tests_scores
from usa.processing.requirements import process_requirements
from usa.processing.constants import (
    ENROLLMENT_LEVEL_ALL,
    COLLEGE_METADATA_OUTPUT,
    DATA_DIR_USA,
    DEGREES_OUTPUT,
    DEPARTMENTS_OUTPUT,
    ENROLLMENT_OUTPUT,
    ACCEPTANCE_OUTPUT,
    FINANCIAL_AID_OUTPUT,
    TESTS_SCORES_OUTPUT,
    APPLICATION_REQUIREMENTS_OUTPUT,
    COLLEGE_REQUIREMENTS_MAP_OUTPUT,
    PROCESSED_DIR,
    YEAR_FILE_CONFIGS,
    FINANCIAL_AID_BUCKETS,
    ADM_REQUIREMENTS,
)


def find_unzipped_dir(base_path: Path, year: int) -> Optional[Path]:
    candidate = base_path / str(year) / "unzipped"
    if candidate.exists():
        return candidate
    return None


def resolve_file(unzipped_path: Path, filename: Optional[str]) -> Optional[Path]:
    if not filename:
        return None
    path = unzipped_path / filename
    if path.exists():
        return path
    if filename.lower().endswith(".csv"):
        stem, ext = filename.rsplit(".", 1)
        rv_path = unzipped_path / f"{stem}_rv.{ext}"
        if rv_path.exists():
            return rv_path
    return None


def build_year_contexts(base_path: Path):
    contexts = []
    for year in sorted(YEAR_FILE_CONFIGS):
        unzipped = find_unzipped_dir(base_path, year)
        if not unzipped:
            continue
        files = YEAR_FILE_CONFIGS[year]["files"]
        resolved_paths = {
            key: resolve_file(unzipped, fname) for key, fname in files.items()
        }
        contexts.append(
            {"year": year, "config": YEAR_FILE_CONFIGS[year], "paths": resolved_paths}
        )
    return contexts


def concat_and_dedupe(frames, subset):
    non_empty = [
        df
        for df in frames
        if not df.dropna(how="all").empty and not df.dropna(axis=1, how="all").empty
    ]
    if not non_empty:
        return pd.DataFrame()
    cleaned = [df.dropna(axis=1, how="all") for df in non_empty]
    return pd.concat(cleaned, ignore_index=True).drop_duplicates(subset=subset)


def main():
    base_path = Path(DATA_DIR_USA)
    processed_path = Path(PROCESSED_DIR)
    processed_path.mkdir(parents=True, exist_ok=True)

    contexts = build_year_contexts(base_path)
    if not contexts:
        raise RuntimeError("No USA data directories found")

    metadata_candidates = [
        ctx for ctx in contexts if ctx["paths"].get("hd") and ctx["paths"].get("ic")
    ]
    if not metadata_candidates:
        raise RuntimeError("No metadata files (HD/IC) found for any year")

    metadata_ctx = max(metadata_candidates, key=lambda ctx: ctx["year"])
    print(f"Processing college_metadata using {metadata_ctx['year']} data...")
    college_metadata = process_college_metadata(
        metadata_ctx["paths"]["hd"],
        metadata_ctx["paths"]["ic"],
        processed_path / COLLEGE_METADATA_OUTPUT,
    )
    print(f"✓ Processed {len(college_metadata)} colleges")
    print(f"✓ Output: {processed_path / COLLEGE_METADATA_OUTPUT}\n")

    degrees_frames = []
    departments_frames = []
    for ctx in contexts:
        completions_path = ctx["paths"].get("completions")
        cip_lookup_path = ctx["paths"].get("cip_lookup")
        if completions_path and cip_lookup_path:
            print(f"Processing degrees for {ctx['year']}...")
            degrees_df, departments_df = process_degrees(
                completions_path,
                cip_lookup_path,
                ctx["year"],
            )
            degrees_frames.append(degrees_df)
            departments_frames.append(departments_df)

    if departments_frames:
        departments = concat_and_dedupe(departments_frames, subset=None)
        departments.to_csv(processed_path / DEPARTMENTS_OUTPUT, index=False)
        print(f"✓ Processed {len(departments)} departments")
        print(f"✓ Output: {processed_path / DEPARTMENTS_OUTPUT}")

    if degrees_frames:
        degrees = concat_and_dedupe(
            degrees_frames,
            subset=["college_id", "academic_year", "department_id", "degree_type"],
        )
        degrees.to_csv(processed_path / DEGREES_OUTPUT, index=False)
        print(f"✓ Processed {len(degrees)} degree records")
        print(f"✓ Output: {processed_path / DEGREES_OUTPUT}\n")

    enrollment_frames = []
    for ctx in contexts:
        enrollment_path = ctx["paths"].get("enrollment")
        if not enrollment_path:
            continue
        print(f"Processing enrollment for {ctx['year']}...")
        enrollment_df = process_enrollment(
            enrollment_path,
            ctx["year"],
            ctx["config"]["enrollment_fields"],
            ctx["config"].get("enrollment_level", ENROLLMENT_LEVEL_ALL),
            ctx["paths"].get("ic_ay"),
            ctx["config"].get("tuition_fields", {}),
            ctx["paths"].get("net_price"),
            ctx["config"].get("net_price_field"),
            ctx["paths"].get("graduation"),
            ctx["config"].get("graduation_fields", {}),
        )
        if not enrollment_df.empty:
            enrollment_frames.append(enrollment_df)

    if enrollment_frames:
        enrollment = concat_and_dedupe(
            enrollment_frames, subset=["college_id", "academic_year"]
        )
        enrollment.to_csv(processed_path / ENROLLMENT_OUTPUT, index=False)
        print(f"✓ Processed {len(enrollment)} enrollment records")
        print(f"✓ Output: {processed_path / ENROLLMENT_OUTPUT}")

    acceptance_frames = []
    for ctx in contexts:
        admissions_path = ctx["paths"].get("admissions")
        if not admissions_path:
            continue
        print(f"Processing acceptance for {ctx['year']}...")
        acceptance_df = process_acceptance(
            admissions_path,
            ctx["year"],
        )
        if not acceptance_df.empty:
            acceptance_frames.append(acceptance_df)

    if acceptance_frames:
        acceptance = concat_and_dedupe(
            acceptance_frames, subset=["college_id", "academic_year"]
        )
        acceptance.to_csv(processed_path / ACCEPTANCE_OUTPUT, index=False)
        print(f"✓ Processed {len(acceptance)} acceptance records")
        print(f"✓ Output: {processed_path / ACCEPTANCE_OUTPUT}")

    financial_aid_frames = []
    for ctx in contexts:
        sfa_path = ctx["paths"].get("net_price")
        if not sfa_path:
            continue
        print(f"Processing financial aid for {ctx['year']}...")
        aid_df = process_financial_aid(
            sfa_path,
            ctx["year"],
            FINANCIAL_AID_BUCKETS,
        )
        if not aid_df.empty:
            financial_aid_frames.append(aid_df)

    if financial_aid_frames:
        financial_aid = concat_and_dedupe(
            financial_aid_frames,
            subset=[
                "college_id",
                "academic_year",
                "income_bracket_range_min",
                "income_bracket_range_max",
            ],
        )
        financial_aid.to_csv(processed_path / FINANCIAL_AID_OUTPUT, index=False)
        print(f"✓ Processed {len(financial_aid)} financial aid records")
        print(f"✓ Output: {processed_path / FINANCIAL_AID_OUTPUT}")

    tests_frames = []
    for ctx in contexts:
        admissions_path = ctx["paths"].get("admissions")
        if not admissions_path:
            continue
        print(f"Processing tests and scores for {ctx['year']}...")
        tests_df = process_tests_scores(
            admissions_path,
        )
        if not tests_df.empty:
            tests_frames.append(tests_df)

    if tests_frames:
        tests = concat_and_dedupe(tests_frames, subset=["college_id", "test_type"])
        tests.to_csv(processed_path / TESTS_SCORES_OUTPUT, index=False)
        print(f"✓ Processed {len(tests)} tests_and_scores records")
        print(f"✓ Output: {processed_path / TESTS_SCORES_OUTPUT}")

    print("Processing application requirements (from ADM requirement flags)...")
    requirements_df, req_map_df = process_requirements(
        contexts,
        ADM_REQUIREMENTS,
        processed_path / APPLICATION_REQUIREMENTS_OUTPUT,
        processed_path / COLLEGE_REQUIREMENTS_MAP_OUTPUT,
    )
    print(f"✓ Processed {len(requirements_df)} requirement definitions")
    print(f"✓ Processed {len(req_map_df)} college requirement mappings")
    print(f"✓ Output: {processed_path / APPLICATION_REQUIREMENTS_OUTPUT}")
    print(f"✓ Output: {processed_path / COLLEGE_REQUIREMENTS_MAP_OUTPUT}")


if __name__ == "__main__":
    main()
