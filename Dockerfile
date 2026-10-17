FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-deps -e .
COPY . .
ENV PYTHONPATH=src
EXPOSE 8000
CMD ["uvicorn","lean_retrieval.service:app","--host","0.0.0.0","--port","8000"]
