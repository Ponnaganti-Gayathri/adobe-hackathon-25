# Dockerfile

# --- Stage 1: Build/Dependency Stage ---
FROM python:3.9-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV HF_HOME=/app/models
RUN pip install --no-cache-dir -r requirements.txt

# This command will download the models to the cache directory we specified
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')"


# --- Stage 2: Final/Runtime Stage ---
FROM python:3.9-slim

WORKDIR /app

# Copy the installed packages and models from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app/models /root/.cache/huggingface
COPY --from=builder /usr/local/lib/python3.9/site-packages/en_core_web_sm-3.7.1 /usr/local/lib/python3.9/site-packages/en_core_web_sm

# Copy our application code
COPY main.py .
COPY input/ ./input/

# Define the entrypoint for the container
ENTRYPOINT ["python", "main.py", "--input_dir", "input", "--output_dir", "output"]