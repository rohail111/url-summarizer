FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

COPY pyproject.toml README.md ./
COPY url_summarizer ./url_summarizer
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD uvicorn url_summarizer.api.app:app --host 0.0.0.0 --port ${PORT}
