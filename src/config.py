import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pdf-rag-gemini")
    PINECONE_DIMENSION=768
    PINECONE_NAMESPACE="trading"
    
    EMBEDDING_MODEL = "gemini-embedding-001"
    LLM_MODEL = "gemini-3.5-flash-lite"
    
    CONFIGENTIAL_KEYWORDS=["ไอเหี้ย", "อนันต์ อัศวโภคิน"]