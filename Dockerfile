# Dockerfile

# --- Stage 1: Build/Dependency Stage ---
# Use a full Python image to install dependencies and download models
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies that might be needed for some libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install python packages
COPY requirements.txt .
# Use --no-cache-dir to keep the layer small
# Set a cache home for transformers so we can copy the model to the next stage
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV HF_HOME=/app/models
RUN pip install --no-cache-dir -r requirements.txt

# This command will download the models to the cache directory we specified
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')"


# --- Stage 2: Final/Runtime Stage ---
# Use a minimal python image for the final application
FROM python:3.9-slim

WORKDIR /app

# Copy the installed packages from the builder stage.
# This single command is enough to bring over all libraries, including the spaCy model.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the downloaded Hugging Face models
COPY --from=builder /app/models /root/.cache/huggingface

# The problematic line that caused the error has been REMOVED.

# Copy our application code
COPY main.py .
COPY input/ ./input/

# Define the entrypoint for the container
# This will run our script on the default input directory
ENTRYPOINT ["python", "main.py", "--input_dir", "input", "--output_dir", "output"]