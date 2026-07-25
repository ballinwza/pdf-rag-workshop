from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.api.models.rag_model import DeleteVectorDBRequest, DeleteVectorDBResponse,RAGQuestionRequest, RAGQuestionResponse, HealthResponse
from src.api.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])
rag_services = RAGService()

@router.get('/health', response_model=HealthResponse)
async def health_check():
    try:
        pinecone_ok = rag_services.dbConnection()
        return HealthResponse(
            status="ok",
            pinecone_connected=pinecone_ok
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        rag_services.uploadPDF(file)
        return {
            "message":"Document was upload successful !"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/question", response_model=RAGQuestionResponse)
async def rag_question(request: RAGQuestionRequest):
    try:
        answer = rag_services.askQuestion(request.question, request.top_k) 
        return RAGQuestionResponse(
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/namespace", 
    response_model=DeleteVectorDBRequest, 
    status_code=status.HTTP_200_OK
)
async def delete_by_namespace(payload: DeleteVectorDBRequest):
    if not payload.namespace or not payload.namespace.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Declare namespace"
        )
    try:
        rag_services.vector_db.delete_namespace(payload.namespace.strip())
        return DeleteVectorDBResponse(
            message=f"{payload.namespace} was deleted",
            namespace=payload.namespace
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error : {str(e)}"
        )