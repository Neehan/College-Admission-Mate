from pathlib import Path
from processing.usa.college_metadata import process_college_metadata
from processing.usa.constants import (
    DATA_DIR_USA_2024,
    UNZIPPED_DIR,
    PROCESSED_DIR,
    HD2024_FILENAME,
    IC2024_FILENAME,
    COLLEGE_METADATA_OUTPUT
)


def main():
    base_path = Path(DATA_DIR_USA_2024)
    unzipped_path = base_path / UNZIPPED_DIR
    processed_path = base_path / PROCESSED_DIR

    print("Processing college_metadata...")
    result = process_college_metadata(
        hd_path=unzipped_path / HD2024_FILENAME,
        ic_path=unzipped_path / IC2024_FILENAME,
        output_path=processed_path / COLLEGE_METADATA_OUTPUT
    )

    print(f"Processed {len(result)} colleges")
    print(f"Output saved to: {processed_path / COLLEGE_METADATA_OUTPUT}")
    print(f"\nSample output:\n{result.head()}")


if __name__ == '__main__':
    main()
