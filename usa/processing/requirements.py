from pathlib import Path
import pandas as pd
from usa.processing.constants import (
    UNITID_COLUMN,
    REQUIRED_CODE,
    CONSIDERED_CODE,
)


class RequirementsProcessor:

    def __init__(
        self,
        contexts: list,
        adm_requirements: dict,
        output_requirements: Path,
        output_map: Path,
    ):
        self.contexts = contexts
        self.adm_requirements = adm_requirements
        self.output_requirements = Path(output_requirements)
        self.output_map = Path(output_map)

    def process(self):
        requirement_status = {}

        for ctx in self.contexts:
            admissions_path = ctx["paths"].get("admissions")
            if not admissions_path:
                continue

            year = ctx["year"]
            admissions_df = pd.read_csv(admissions_path)

            for adm_col, (req_type, _) in self.adm_requirements.items():
                if adm_col not in admissions_df.columns:
                    continue

                for college_id, code in zip(admissions_df[UNITID_COLUMN], admissions_df[adm_col]):
                    if pd.isna(code):
                        continue

                    code = int(code)
                    if code == REQUIRED_CODE:
                        status = "required"
                    elif code == CONSIDERED_CODE:
                        status = "optional"
                    else:
                        continue

                    key = (college_id, req_type)
                    prev = requirement_status.get(key)

                    if prev:
                        prev_status, prev_year = prev
                        if status == "optional" and prev_status == "required":
                            continue
                        if status == prev_status and prev_year > year:
                            continue

                    requirement_status[key] = (status, year)

        req_types = sorted({v[0] for v in self.adm_requirements.values()})
        type_to_details = {req_type: desc for _, (req_type, desc) in self.adm_requirements.items()}

        requirements_df = pd.DataFrame({
            "id": range(1, len(req_types) + 1),
            "requirement_type": req_types,
            "details": [type_to_details[r] for r in req_types],
        })

        req_type_to_id = dict(zip(requirements_df["requirement_type"], requirements_df["id"]))

        map_records = [
            {
                "college_id": college_id,
                "requirement_id": req_type_to_id[req_type],
                "is_optional": status != "required",
                "additional_notes": None,
            }
            for (college_id, req_type), (status, _) in requirement_status.items()
        ]
        map_df = pd.DataFrame(map_records)

        self.output_requirements.parent.mkdir(parents=True, exist_ok=True)
        requirements_df.to_csv(self.output_requirements, index=False)

        self.output_map.parent.mkdir(parents=True, exist_ok=True)
        map_df.to_csv(self.output_map, index=False)

        return requirements_df, map_df


def process_requirements(
    contexts: list,
    adm_requirements: dict,
    output_requirements: Path,
    output_map: Path,
):
    processor = RequirementsProcessor(contexts, adm_requirements, output_requirements, output_map)
    return processor.process()
