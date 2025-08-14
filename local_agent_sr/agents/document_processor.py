import os
import logging
from pypdf import PdfReader
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentProcessor:
    """
    Parses and chunks documents from various formats.
    """
    def __init__(self, context_length: int):
        """
        Initializes the DocumentProcessor.

        Args:
            context_length (int): The context length of the LLM.
        """
        self.context_length = context_length
        self.chunk_size = int(context_length * 0.7)
        self.overlap = int(self.chunk_size * 0.15)

    def _parse_pdf(self, file_path: str) -> str:
        """Parses a PDF file and returns its text content with page markers."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for i, page in enumerate(reader.pages):
                text += f"[PAGE {i+1}]\n{page.extract_text()}\n"
            return text
        except Exception as e:
            logging.error(f"Error parsing PDF {file_path}: {e}")
            return ""

    def _parse_txt(self, file_path: str) -> str:
        """Parses a TXT file and returns its content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error parsing TXT {file_path}: {e}")
            return ""

    def _chunk_text(self, text: str, paper_id: str) -> List[Dict]:
        """Chunks the text into smaller pieces with overlap."""
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id_counter = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_content = text[start:end]
            chunks.append({
                "paper_id": paper_id,
                "chunk_id": chunk_id_counter,
                "content": chunk_content,
            })
            start += self.chunk_size - self.overlap
            chunk_id_counter += 1
        return chunks

    def process_document(self, file_path: str) -> List[Dict]:
        """Processes a single document, parsing and chunking it."""
        paper_id = os.path.basename(file_path)
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == '.pdf':
            text = self._parse_pdf(file_path)
        elif ext.lower() == '.txt':
            text = self._parse_txt(file_path)
        else:
