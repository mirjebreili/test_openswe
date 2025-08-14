import typer
import os
import logging
from local_agent_sr.agents.llm_manager import LLMManager
from local_agent_sr.agents.document_processor import DocumentProcessor
from local_agent_sr.agents.screening_agent import ScreeningAgent
from local_agent_sr.agents.extraction_agent import ExtractionAgent
from local_agent_sr.utils.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = typer.Typer()

@app.command()
def run_all(
    root: str = typer.Option(..., "--root", help="Root folder of papers to process."),
    model: str = typer.Option("llama3.1:8b", "--model", help="Ollama model to use."),
    output_dir: str = typer.Option("output", "--output-dir", help="Directory to save output files."),
):
    """
    Run the full systematic review process: ingest, screen, extract, and report.
    """
    # Initialize managers and agents
    llm_manager = LLMManager(model)
    doc_processor = DocumentProcessor(llm_manager.context_length)
    screening_agent = ScreeningAgent(llm_manager, "local_agent_sr/configs/inclusion_criteria.yaml")
    extraction_agent = ExtractionAgent(llm_manager, "local_agent_sr/configs/data_extraction.yaml")
    report_generator = ReportGenerator(output_dir)

    # Process each document
    all_screening_results = []
    all_extraction_results = []
    included_papers = []

    for filename in os.listdir(root):
        if filename.endswith(('.pdf', '.txt')):
            file_path = os.path.join(root, filename)
            logging.info(f"Processing {file_path}...")
            
            # Ingest and chunk
            chunks = doc_processor.process_document(file_path)
            if not chunks:
                continue

            # Screen
            screening_result = screening_agent.screen_document(chunks)
            all_screening_results.append({"paper": filename, **screening_result})
            
            # Extract if included
            if screening_result["decision"] == "Include":
                included_papers.append(filename)
                extraction_result = extraction_agent.extract_data(chunks)
                all_extraction_results.append({"paper": filename, **extraction_result})

    # Generate reports
    report_generator.generate_screening_report(all_screening_results)
    if all_extraction_results:
        report_generator.generate_extraction_report(all_extraction_results)
    report_generator.copy_included_papers(included_papers, root)
    
    logging.info("Systematic review process completed.")

if __name__ == "__main__":
    app()

