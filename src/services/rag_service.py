from src.services.sanitizer import DataSanitizerService
from src.services.pdf_loader import PDFProcessorService
from src.repositories.gemini_rag_engine import GeminiRAGEngineService
from src.repositories.pinecone_store import PineconeManagerService
from src.config import Config
from fastapi import File,UploadFile
from concurrent.futures import ThreadPoolExecutor, as_completed
    
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
        )
        
    def uploadPDF(self, namespace: str, file: UploadFile = File(...)):
        if file.filename is None:
            raise ValueError("Not found .pdf file")
        if not file.filename.endswith(".pdf"):
            raise ValueError("Avilable for .pdf only")
        try:
            chunks, _ = self.pdf_loader.process_pdf(file)
            text_to_embed = [c["text"] for c in chunks]
            embeddings = self.rag_engine.get_embeddings(text_to_embed)
            self.vector_db.upsert_vectors(chunks, embeddings, namespace)
        except Exception as e:
            raise RuntimeError(f"Failed uploadPDF: {str(e)}")
        
    def askQuestion(self, question: str, namespace: str, top_k:int =4)->str:
        ask_prompt = "ถามคำถามเกี่ยวกับ PDF นี้... "+question
        try:
            query_vector = self.rag_engine.get_single_embedding(ask_prompt)
            matching_chunks = self.vector_db.query_similar_chunks(query_vector,namespace, top_k)
            answer = self.rag_engine.answer_question(ask_prompt, matching_chunks)
            return answer
        except Exception as e:
            raise RuntimeError(f"Failed askQuestion: {str(e)}")
        
    def deleteVectorStoreNamespace(self, namespace: str):
        try:
            self.vector_db.delete_namespace(namespace)
        except Exception as e:
            raise RuntimeError(f"Error deleteVectorStoreNamespace: {str(e)}")
        
    def deleteVectorStoreSource(self, namespace: str, source: str):
            try:
                self.vector_db.delete_namespace_source(namespace, source)
            except Exception as e:
                raise RuntimeError(f"Error deleteVectorStoreSource: {str(e)}")
        
    def dbConnection(self)->bool:
            try:
                self.vector_db.check_connection()
                return True
            except Exception as e:
                raise RuntimeError(f"Failed askQuestion: {str(e)}")
        
    def getAllSourceAndNamespace(self):
        try:
            namespaces = self.vector_db.get_all_namespaces()
            if not namespaces:
                return {}
            
            results = {}
            workers = min(len(namespaces), 20)
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_ns = {
                    executor.submit(self.vector_db.get_uploaded_namespace_pdfs, ns): ns
                    for ns in namespaces
                }
                
                for future in as_completed(future_to_ns):
                    ns = future_to_ns[future]
                    try:
                        sources = future.result()
                        results[ns]=sources
                    except Exception as e:
                        print(f"Error fetching sources for namespace '{ns}': {e}")
                        results[ns] = set()
            return results
        except Exception as e:
            raise RuntimeError(f"Error getAllSourceAndNamespace: {str(e)}")