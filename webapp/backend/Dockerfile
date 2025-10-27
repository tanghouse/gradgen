# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual env (we're in Docker)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden by Railway)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
