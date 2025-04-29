FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run Alembic migrations and start FastAPI app
CMD /bin/sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

