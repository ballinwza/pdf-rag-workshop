import io
from PIL import Image
from fastapi import UploadFile
from src.repositories.gemini_rag_engine import GeminiRAGEngineService
from src.config import Config

class ImageLoader:
    def __init__(self):
        self.rag_engine = GeminiRAGEngineService(
            api_key=Config.GEMINI_API_KEY,
            embedding_model=Config.EMBEDDING_MODEL,
            llm_model=Config.LLM_MODEL,
            dimension=Config.PINECONE_DIMENSION
        )
        
    def process_image(self, file: UploadFile) -> tuple[list[dict], str]:
        image_bytes = file.file.read()
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = "อ่านข้อความภาษาไทยและตัวเลขทั้งหมดในภาพนี้ให้ออกมาเป็นข้อความที่ถูกต้อง ห้ามเดาหรือพิมพ์ผิด"
        
        extracted_text = self.rag_engine.generate_content_image(img, prompt)
        if not extracted_text:
            raise ValueError(f"Not found text from image")
                       
                    
        if not extracted_text:
            extracted_text = ""
                    
        chunks = [
            {
                "text": extracted_text,
                "metadata": {
                    "source": file.filename,
                    "file_type": "image",
                }
            }
        ]
        
        return chunks, extracted_text