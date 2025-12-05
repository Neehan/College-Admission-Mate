from pathlib import Path
from processing.usa.college_metadata import process_college_metadata
from processing.usa.degrees import process_degrees
from processing.usa.constants import (
    DATA_DIR_USA_2024,
    UNZIPPED_DIR,
    PROCESSED_DIR,
    HD2024_FILENAME,
    IC2024_FILENAME,
    COLLEGE_METADATA_OUTPUT,
    C2024_A_CSV_FILENAME,
    C2024_A_XLSX_FILENAME,
    DEGREES_OUTPUT,
    DEPARTMENTS_OUTPUT,
)


def main():
    base_path = Path(DATA_DIR_USA_2024)
    unzipped_path = base_path / UNZIPPED_DIR
    processed_path = base_path / PROCESSED_DIR

    print("Processing college_metadata...")
    college_metadata = process_college_metadata(
        hd_path=unzipped_path / HD2024_FILENAME,
        ic_path=unzipped_path / IC2024_FILENAME,
        output_path=processed_path / COLLEGE_METADATA_OUTPUT
    )
    print(f"✓ Processed {len(college_metadata)} colleges")
    print(f"✓ Output: {processed_path / COLLEGE_METADATA_OUTPUT}\n")

    print("Processing degrees and departments...")
    degrees, departments = process_degrees(
        completions_path=unzipped_path / C2024_A_CSV_FILENAME,
        cip_lookup_path=unzipped_path / C2024_A_XLSX_FILENAME,
        output_degrees_path=processed_path / DEGREES_OUTPUT,
        output_departments_path=processed_path / DEPARTMENTS_OUTPUT,
    )
    print(f"✓ Processed {len(departments)} departments")
    print(f"✓ Processed {len(degrees)} degree records")
    print(f"✓ Output: {processed_path / DEPARTMENTS_OUTPUT}")
    print(f"✓ Output: {processed_path / DEGREES_OUTPUT}")


if __name__ == '__main__':
    main()
