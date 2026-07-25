import streamlit as st
from src.config import Config
from src.api.services.pdf_loader import PDFProcessorService
from src.api.services.pinecone_store import PineconeManagerService
from src.api.services.gemini_rag_engine import GeminiRAGEngineService

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

st.set_page_config(page_title="PDF RAG & Summarizer", page_icon="📚", layout="wide")

@st.cache_resource
def init_services():
    rag_engine = GeminiRAGEngineService(
        api_key=Config.GEMINI_API_KEY,
        embedding_model=Config.EMBEDDING_MODEL,
        llm_model=Config.LLM_MODEL,
        dimension=Config.PINECONE_DIMENSION
    )
    vector_store = PineconeManagerService(
        api_key=Config.PINECONE_API_KEY,
        index_name=Config.PINECONE_INDEX_NAME,
        dimension=Config.PINECONE_DIMENSION,
        namespace=Config.PINECONE_NAMESPACE
    )
    pdf_processor = PDFProcessorService()
    return rag_engine, vector_store, pdf_processor

try:
    rag_engine, vector_store, pdf_processor = init_services()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลด Config หรือสร้าง Connection: {e}")
    st.stop()

st.title("📚 PDF RAG Summarizer & Chat")
st.caption("สรุปเนื้อหาและค้นหาข้อมูลในเอกสาร PDF ด้วย Gemini & Pinecone")

# Sidebar for PDF Upload
with st.sidebar:
    st.header("📄 อัปโหลดเอกสาร")
    uploaded_file = st.file_uploader("เลือกไฟล์ PDF", type=["pdf"])
    
    if uploaded_file and st.button("ประมวลผล PDF"):
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            st.error(f"❌ ขนาดไฟล์ใหญ่เกินไป! กรุณาอัปโหลดไฟล์ขนาดไม่เกิน {MAX_FILE_SIZE_MB} MB (ไฟล์ของคุณขนาด {uploaded_file.size / (1024*1024):.2f} MB)")
        else:
            st.success("✅ อัปโหลดไฟล์สำเร็จ!")
        
            with st.spinner("กำลังอ่านไฟล์และบันทึกลง Pinecone..."):
                # 1. Read & Chunk
                chunks, full_text = pdf_processor.process_pdf(uploaded_file)
                st.session_state["full_text"] = full_text
                
                # 2. Get Embeddings & Upsert
                texts_to_embed = [c["text"] for c in chunks]
                embeddings = rag_engine.get_embeddings(texts_to_embed)
                vector_store.upsert_vectors(chunks, embeddings)
                
                st.session_state["pdf_processed"] = True
                st.success(f"บันทึกข้อมูล {len(chunks)} Chunks เรียบร้อยแล้ว!")

# Main Tabs
tab1, tab2 = st.tabs(["💬 ถาม-ตอบ (RAG)", "📝 สรุปเอกสาร (Summary)"])

# Tab 1: Chat RAG
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("ถามคำถามเกี่ยวกับ PDF นี้..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("กำลังค้นหาข้อมูลใน Pinecone และสร้างคำตอบ..."):
                # 1. Convert Query to Vector
                query_vector = rag_engine.get_single_embedding(prompt)
                
                # 2. Query Pinecone
                matching_chunks = vector_store.query_similar_chunks(query_vector, top_k=4)
                
                # 3. Generate Answer from Gemini
                answer = rag_engine.answer_question(prompt, matching_chunks)
                st.markdown(answer)
                

        st.session_state.messages.append({"role": "assistant", "content": answer})

# Tab 2: Summarization
with tab2:
    if st.button("สรุปเนื้อหา PDF ทั้งหมด ใช้กับเอกสารที่เพิ่ง Upload เสร็จสิ้นเท่านั้น"):
        full_text = st.session_state.get("full_text")
        if full_text:
            with st.spinner("Gemini กำลังอ่านและสรุปเนื้อหา..."):
                summary = rag_engine.summarize_text(full_text)
                st.markdown("### 📌 สรุปภาพรวมเอกสาร")
                st.markdown(summary)
        else:
            st.warning("กรุณาอัปโหลดและกด 'ประมวลผล PDF' ที่ Sidebar ก่อนครับ")