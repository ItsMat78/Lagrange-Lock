# ---- Lagrange-Lock deployment image ----
# Runs phase_3/server.py (physics + PPO inference + static frontend).
FROM python:3.11-slim

# Numba needs a writable cache dir; keep it inside the container.
ENV NUMBA_CACHE_DIR=/tmp/numba_cache \
    PYTHONUNBUFFERED=1 \
    PORT=8081

WORKDIR /app

# Install deps first for better layer caching.
# CPU-only torch keeps the image ~1GB instead of ~3GB (no CUDA wheels).
COPY requirements-server.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements-server.txt

# Copy the code the server actually needs.
COPY phase_3/ ./phase_3/

EXPOSE 8081

# server.py reads $PORT and chdir's into phase_3 to serve the frontend.
CMD ["python", "phase_3/server.py"]
