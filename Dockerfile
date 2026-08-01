FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --upgrade pip==26.1.2 \
    && python -m pip install --no-cache-dir -r requirements.lock
COPY . .
RUN python -m pip install --no-cache-dir --no-deps .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
