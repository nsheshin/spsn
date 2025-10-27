# FROM python:3.10-slim
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime
WORKDIR /app

COPY requirements.txt .
RUN pip install uv && \
    uv pip install --no-cache --upgrade --system -r requirements.txt

RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; \
    HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-base')"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--access-log"]