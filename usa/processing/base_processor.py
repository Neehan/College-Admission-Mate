from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class BaseProcessor(ABC):
    """Base class for all IPEDS data processors."""

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)
        self.result_df = None

    @abstractmethod
    def load_data(self):
        """Load source data files."""
        pass

    @abstractmethod
    def transform(self):
        """Transform loaded data. Must set self.result_df."""
        pass

    def validate(self):
        """Validate output data against schema constraints. Override in subclass if needed."""
        pass

    def save(self):
        """Save result_df to output_path."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_df.to_csv(self.output_path, index=False)

    def process(self):
        """Execute full processing pipeline."""
        self.load_data()
        self.transform()
        self.validate()
        self.save()
        return self.result_df


class SingleFileProcessor(BaseProcessor):
    """Processor for single CSV input."""

    def __init__(self, input_path: Path, output_path: Path):
        super().__init__(output_path)
        self.input_path = Path(input_path)
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.input_path)


class MultiFileProcessor(BaseProcessor):
    """Processor for multiple CSV inputs."""

    def __init__(self, input_paths: dict, output_path: Path):
        super().__init__(output_path)
        self.input_paths = {k: Path(v) for k, v in input_paths.items()}
        self.data = {}

    def load_data(self):
        for key, path in self.input_paths.items():
            self.data[key] = pd.read_csv(path)


class YearlyProcessor(BaseProcessor):
    """Processor with academic_year parameter."""

    def __init__(self, input_path: Path, academic_year: int, output_path: Path):
        super().__init__(output_path)
        self.input_path = Path(input_path)
        self.academic_year = academic_year
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.input_path)
