from pydantic import BaseModel, Field

class RAGQuestionRequest(BaseModel):
    question: str = Field(default="สรุปบทความ")
    top_k: int = Field(default=3, ge=1, le=10, description="ค่าความใกล้เคียงของคำถามต่อคำตอบ") 
    namespace: str
    
class RAGQuestionResponse(BaseModel):
    answer: str

class HealthResponse(BaseModel):
    status: str
    pinecone_connected: bool
    
class DeleteVectorDBRequest(BaseModel):
    namespace: str = Field(examples=["pdf_docs_stock"], description="ชื่อ Namespace ที่ต้องการลบใน vector DB")
    
class DeleteVectorDBResponse(BaseModel):
    message: str
    namespace: str
     
class DeleteVectorDBSourceRequest(BaseModel):
    namespace: str = Field(examples=["pdf_docs_stock"], description="ชื่อ Namespace ที่ต้องการลบใน vector DB")
    source: str = Field(examples=["test.pdf"], description="PDF name")
    
class DeleteVectorDBSourceResponse(BaseModel):
    message: str
    namespace: str
    soruce: str