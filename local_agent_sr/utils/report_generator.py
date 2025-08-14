import os
import json
import shutil
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    """
    Generates all output files for the systematic review.
    """
    def __init__(self, output_dir: str):
        """
        Initializes the ReportGenerator.

        Args:
            output_dir (str): The directory where output files will be saved.
        """
        self.output_dir = os.path.join(output_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_screening_report(self, screening_results: List[Dict], filename: str = "screening_report.jsonl"):
        """Generates a JSONL file with the screening results."""
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            for item in screening_results:
                f.write(json.dumps(item) + '

    def generate_extraction_report(self, extraction_results: List[Dict], filename: str = "extraction.xlsx"):
        """Generates an Excel file with the extracted data."""
        path = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(extraction_results)
        df.to_excel(path, index=False)

    def generate_provenance_log(self, provenance_data: List[Dict], filename: str = "provenance.csv"):
        """Generates a CSV file with the provenance of extracted data."""
        path = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(provenance_data)
        df.to_csv(path, index=False)

    def generate_run_summary(self, summary_data: Dict[str, Any], filename: str = "run_summary.md"):
        """Generates a markdown file with the summary of the run."""
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            for key, value in summary_data.items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}

    def copy_included_papers(self, included_papers: List[str], source_dir: str):
        """Copies included papers to the 'included_papers' directory."""
        included_dir = os.path.join(self.output_dir, "included_papers")
        os.makedirs(included_dir, exist_ok=True)
        for paper_path in included_papers:
            try:
                shutil.copy(os.path.join(source_dir, paper_path), included_dir)
            except FileNotFoundError:
                print(f"Warning: File not found, could not copy {paper_path}")

