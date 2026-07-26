from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.api.services.sanitizer import DataSanitizerService
from src.config import Config

class PDFProcessorService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int =200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        confidential_keywords = getattr(Config, "CONFIGENTIAL_KEYWORDS", [])
        self.sanitizer = DataSanitizerService(custom_keywords=confidential_keywords)
        
    def process_pdf(self, pdf_file) -> tuple[list[dict], str]:
        reader = PdfReader(pdf_file.file)
        chunks_data = []
        full_text_pages = []

        full_text_pages = []
        for page_num, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            
            # Sanitization
            sanitized_page_text = self.sanitizer.sanitize(raw_text)
            
            full_text_pages.append(sanitized_page_text)
            
            # แบ่ง Chunk แยกตามหน้าที่เก็บ Metadata
            page_chunks = self.text_splitter.split_text(sanitized_page_text)
            for chunk in page_chunks:
                chunks_data.append({
                    "text": chunk,
                    "metadata": {
                        "page": page_num,
                        "source": getattr(pdf_file, "filename", "unknown.pdf")
                    }
                })
        return chunks_data, "\n".join(full_text_pages)