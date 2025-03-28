FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.network.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
