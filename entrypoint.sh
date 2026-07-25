#!/bin/bash

# รัน FastAPI เป็น Background Process (Port 8000)
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# รัน Streamlit เป็น Foreground Process (Port 8501)
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# รอให้ทั้งสอง process ทำงาน
wait -n

# ถ้า process ใด process หนึ่งดับ ให้ exit เพื่อให้ Docker รู้ว่ามีปัญหา
exit $?