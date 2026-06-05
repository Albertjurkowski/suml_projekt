FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m model.train

EXPOSE 8501 8000

CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port 8000 & streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"]
