from src.api.services.sanitizer import DataSanitizerService
from src.api.services.pdf_loader import PDFProcessorService
from src.api.services.gemini_rag_engine import GeminiRAGEngineService
from src.api.services.pinecone_store import PineconeManagerService
from src.config import Config
from fastapi import File,UploadFile
    
class RAGService:
    def __init__(self):
        self.sanitizer = DataSanitizerService(
            custom_keywords=Config.CONFIGENTIAL_KEYWORDS
        )
        self.pdf_loader = PDFProcessorService(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.rag_engine = GeminiRAGEngineService(
            api_key=Config.GEMINI_API_KEY,
            embedding_model=Config.EMBEDDING_MODEL,
            llm_model=Config.LLM_MODEL,
            dimension=Config.PINECONE_DIMENSION
        )
        self.vector_db = PineconeManagerService(
            api_key=Config.PINECONE_API_KEY,
            index_name=Config.PINECONE_INDEX_NAME,
            dimension=Config.PINECONE_DIMENSION,
            namespace=Config.PINECONE_NAMESPACE
        )
        
    def uploadPDF(self, file: UploadFile = File(...)):
        if file.filename is None:
            raise ValueError("Not found .pdf file")
        if not file.filename.endswith(".pdf"):
            raise ValueError("Avilable for .pdf only")
        try:
            chunks, _ = self.pdf_loader.process_pdf(file)
            text_to_embed = [c["text"] for c in chunks]
            embeddings = self.rag_engine.get_embeddings(text_to_embed)
            self.vector_db.upsert_vectors(chunks, embeddings)
        except Exception as e:
            raise RuntimeError(f"Failed uploadPDF: {str(e)}")
        
    def askQuestion(self, question: str, top_k:int =4)->str:
        ask_prompt = "ถามคำถามเกี่ยวกับ PDF นี้... "+question
        try:
            query_vector = self.rag_engine.get_single_embedding(ask_prompt)
            matching_chunks = self.vector_db.query_similar_chunks(query_vector, top_k)
            answer = self.rag_engine.answer_question(ask_prompt, matching_chunks)
            return answer
        except Exception as e:
            raise RuntimeError(f"Failed askQuestion: {str(e)}")
        
    def deleteVectorStore(self, namespace: str):
        try:
            self.vector_db.delete_namespace(namespace)
        except Exception as e:
            raise RuntimeError(f"Failed askQuestion: {str(e)}")
        
    def dbConnection(self)->bool:
            try:
                self.vector_db.check_connection()
                return True
            except Exception as e:
                raise RuntimeError(f"Failed askQuestion: {str(e)}")