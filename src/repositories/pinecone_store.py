from pinecone import Pinecone, ServerlessSpec
import uuid
import logging

logger = logging.getLogger(__name__)
class PineconeManagerService:
    def __init__(self, api_key: str, index_name: str, dimension: int =768):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension #ต้องเป็น 768
        self._ensure_index_exists()
        self.index=self.pc.Index(self.index_name)

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
    def upsert_vectors(self, chunks: list[dict], embeddings: list[list[float]], namespace: str="__default__"):
        vectors_to_upsert = []
        for i, (chunk, idx_embed) in enumerate(zip(chunks, embeddings)):
            vector_id = str(uuid.uuid4())
            chunk_meta = chunk.get("metadata", {})
            
            metadata = {
                "text": chunk["text"],
                "source": chunk_meta.get("source", "unknow"),
                "file_type": chunk_meta.get("file_type", "image")
            }
            
            if "page" in chunk_meta:
                metadata["page"] = chunk_meta["page"]
                
            vectors_to_upsert.append({
                "id": vector_id,
                "values": idx_embed,
                "metadata": metadata
            })
        
        self.index.upsert(
            vectors=vectors_to_upsert,
            namespace=namespace
        )
        
    # ค้นหา Chunk เนื้อหาใกล้เคียงที่สุด
    def query_similar_chunks(self, query_embedding: list[float],  namespace: str="__default__", top_k: int=4) -> tuple[list[dict], str]:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )
        matches = []
        for match in getattr(results, "matches", []):
            fileType =  match.metadata["file_type"]
            
            chunk = {
                "text":match.metadata["text"],
                "score":match.score,
                "file_type": fileType
            }
            
            if fileType == "pdf":
                chunk["page"] = int(match.metadata["page"])
            
            matches.append(chunk)
        return matches, fileType
    
    def query_text(self, query_embedding: list[float],  namespace: str="__default__", top_k: int=4) -> str:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )
        res_dict = getattr(results, "matches")
    
        contexts = [
            match["metadata"]["text"] 
            for match in res_dict.get("matches", []) 
            if "metadata" in match and "text" in match["metadata"]
        ]
        
        combined_context = "\n---\n".join(contexts)
        return combined_context
        
    def delete_namespace(self, namespace: str):
        self.index.delete(
            delete_all=True, 
            namespace=namespace
        )
        logger.info(f"Successfully deleated all vectors in namespace: {namespace}")
    
    def delete_namespace_source(self, namespace:str, source: str):
        self.index.delete(
            namespace=namespace,
            filter= {
                "source":{"$eq": source}
            }
        )
        logger.info(f"Successfully deleated all vectors in namespace: {namespace}")
                
    def get_all_namespaces(self) -> list[str]:
        index = self.pc.Index(self.index_name)
        stats = index.describe_index_stats()
        return list(stats.get("namespaces", {}).keys())
    
    def get_uploaded_namespace_pdfs(self, namespace: str)-> set[str]:
        if not namespace:
            return set()
        index = self.pc.Index(self.index_name)
        dummy_vector = [0.1] * self.dimension
        results = index.query(
            vector=dummy_vector,
            top_k=3,
            include_metadata=True,
            namespace=namespace
        )
        
        seen = set()

        for item in getattr(results, "matches", []):
            source = item["metadata"]["source"]
            if source not in seen:
                seen.add(source)
                
        return seen
    
