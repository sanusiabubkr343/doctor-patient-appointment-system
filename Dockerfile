FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including PostgreSQL development packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        postgresql-client \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir alembic python-dotenv

EXPOSE 8000

WORKDIR /app

# Set entrypoint to run migrations and start the application
ENTRYPOINT ["sh", "-c"]
CMD ["alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
