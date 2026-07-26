from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.api.models.rag_model import DeleteVectorDBRequest, DeleteVectorDBResponse,RAGQuestionRequest, RAGQuestionResponse, HealthResponse, DeleteVectorDBSourceResponse, DeleteVectorDBSourceRequest
from src.api.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])
rag_services = RAGService()

# GET
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
    
@router.get(
    "/namespaces",
    status_code=status.HTTP_200_OK
)
async def all_namespace():
    try:
        namespaces= rag_services.getAllSourceAndNamespace()
        return {
            "namespace":namespaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST
@router.post(
    "/upload", 
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf(namespace:str, file: UploadFile = File(...)):
    try:
        rag_services.uploadPDF(namespace,file)
        return {
            "message":"Document was upload successful !"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/question", response_model=RAGQuestionResponse)
async def rag_question(request: RAGQuestionRequest):
    try:
        answer = rag_services.askQuestion(request.question,request.namespace, request.top_k) 
        return RAGQuestionResponse(
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DELETE
@router.delete(
    "/delete/namespace", 
    response_model=DeleteVectorDBResponse, 
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

@router.delete(
    "/delete/source", 
    response_model=DeleteVectorDBSourceResponse, 
    status_code=status.HTTP_200_OK
)        
async def delete_by_namespace_sorce(payload: DeleteVectorDBSourceRequest):
    if not payload.namespace or not payload.namespace.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Declare namespace"
        )
    try:
        rag_services.vector_db.delete_namespace_source(payload.namespace.strip(), payload.source.strip())
        return DeleteVectorDBResponse(
            message=f"{payload.namespace} was deleted",
            namespace=payload.namespace
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error : {str(e)}"
        )