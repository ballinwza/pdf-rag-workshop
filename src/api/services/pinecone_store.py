from pinecone import Pinecone, ServerlessSpec
import uuid
import logging

logger = logging.getLogger(__name__)
class PineconeManagerService:
    def __init__(self, api_key: str, index_name: str, dimension: int =768, namespace: str="__default__"):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension #ต้องเป็น 768
        self._ensure_index_exists()
        self.index=self.pc.Index(self.index_name)
        self.namespace=namespace
    
    # สร้าง auto index ถ้ายังไม่มีใน Pinecone     
    def _ensure_index_exists(self):
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension, 
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
    def check_connection(self):
        index = self.pc.Index(self.index_name)
        index.describe_index_stats()

    
    # นำ Vector และ Metadata ขึ้น Pinecone
    def upsert_vectors(self, chunks: list[dict], embeddings: list[list[float]]):
        vectors_to_upsert = []
        for i, (chunk, idx_embed) in enumerate(zip(chunks, embeddings)):
            vector_id = str(uuid.uuid4())
            vectors_to_upsert.append({
                "id": vector_id,
                "values": idx_embed,
                "metadata": {
                    "text": chunk["text"],
                    "page": chunk["metadata"]["page"],
                    "source": chunk["metadata"]["source"]
                }
            })
        
        self.index.upsert(
            vectors=vectors_to_upsert,
            namespace=self.namespace
        )
    
    # ค้นหา Chunk เนื้อหาใกล้เคียงที่สุด
    def query_similar_chunks(self, query_embedding: list[float], top_k: int=4) -> list[dict]:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace
        )
        matches = []
        for match in getattr(results, "matches", []):
            matches.append({
                "text":match.metadata["text"],
                "page":int(match.metadata["page"]),
                "score":match.score
            })
        return matches
    
    def delete_namespace(self, namespace: str):
        self.index.delete(delete_all=True, namespace=namespace)
        logger.info(f"Successfully deleated all vectors in namespace: {namespace}")
    