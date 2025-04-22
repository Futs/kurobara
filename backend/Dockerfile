FROM python:3.12-slim

WORKDIR /app/

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]