# Dockerfile for StudyBot Streamlit Application

# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/chroma_db

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check (will use PORT env var)
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8501}/_stcore/health

# Run Streamlit app (PORT will be set by Render)
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
