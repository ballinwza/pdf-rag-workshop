run:
	streamlit run app.py

init:
	pip-compile requirements.in && pip-compile requirements-dev.in && pip-sync requirements-dev.txt

before-init:
	pip install pip-tools

run-api:
	uvicorn main:app --reload