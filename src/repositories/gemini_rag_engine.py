from google import genai
from google.genai import types

class GeminiRAGEngineService:
    def __init__(self, api_key: str, embedding_model: str, llm_model: str, dimension:int=768):
        # 🟢 ต้องส่ง api_key เป็น string เข้า genai.Client
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.dimension = dimension
        
    # แปลงรายการ Text Chunks เป็น Embedding Vector
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dimension
                )
            )
            if response.embeddings and len(response.embeddings) > 0:
                embeddings.append(response.embeddings[0].values)
            else:
                # กรณี Error/ไม่มี Embedding ให้ใส่ List ว่าง หรือปรับตามต้องการ
                embeddings.append([0.0] * 768)
        return embeddings
    
    # แปลงคำถาม Query เป็น Embedding
    def get_single_embedding(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dimension
            )
        )
        
        if response.embeddings and response.embeddings[0].values is not None:
            return response.embeddings[0].values
        raise ValueError("ไม่สามารถสร้าง Embedding จากข้อความนี้ได้")
    
    # สรุปเนื้อหา PDF ทั้งหมดด้วย Gemini
    def summarize_text(self, full_text:str) -> str:
        prompt = f"""คุณคือผู้เชี่ยวชาญด้านการสรุปเอกสาร กรุณาสรุปเนื้อหาสำคัญของเอกสารนี้ให้อ่านง่าย ชัดเจน 
แบ่งเป็นหัวข้อสำคัญ และ Highlight ประเด็นหลักให้ครบถ้วน:

--- เนื้อหาเอกสาร ---
{full_text[:1000]}  # จำกัดความยาวป้องกัน Token เกิน
"""
        response = self.client.models.generate_content(
            model=self.llm_model,
            contents=prompt
        )

        return response.text or "ไม่สามารถสร้างข้อความสรุปได้"
    
    # ตอบคำถามอิงตาม Context จาก Pinecone
    def answer_question(self, query:str, context_chunks: list[dict]) -> str:
        context_str = "\n\n".join([f"[หน้าที่ {c['page']}]: {c['text']}"  for c in context_chunks ])
        prompt = f"""
        คุณเป็นผู้ช่วยตอบคำถามอิงจากเอกสารที่กำหนดให้เท่านั้น กรุณาตอบคำถามโดยใช้ข้อมูลจาก Context ด้านล่างนี้ หากไม่มีข้อมูลใน Context ให้ระบุว่า "ไม่พบข้อมูลดังกล่าวในเอกสาร" อย่างสุภาพ

Context:
{context_str}

คำถาม: {query}
คำตอบ (โปรดอ้างอิงเลขหน้าหากเป็นไปได้):
"""

        response = self.client.models.generate_content(
            model=self.llm_model,
            contents=prompt
        )
        return response.text or "ไม่สามารถสร้างคำตอบได้"
    
    