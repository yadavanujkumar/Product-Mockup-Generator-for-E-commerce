# Docker configuration for AI Product Mockup Generator
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p generated_mockups temp_uploads

# Expose ports
EXPOSE 8501 8000

# Default command (Streamlit app)
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
