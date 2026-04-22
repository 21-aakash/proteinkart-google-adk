# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory to app
WORKDIR /app

# Copy requirements from the root (since they are shared)
# Actually, I'll create a local requirements for the backend specifically
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Set environment variables defaults
ENV PORT=8000
ENV DB_PATH=/app/proteins.db

# Expose the port
EXPOSE 8000

# Run the backend
# Cloud Run provides the PORT env var; uvicorn will use it via os.getenv in server.py
# Or we can specify it here:
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
