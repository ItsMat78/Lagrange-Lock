# ---- Lagrange-Lock deployment image ----
# Runs phase_3/server.py (physics + PPO inference + static frontend).
FROM python:3.11-slim

# Numba needs a writable cache dir; keep it inside the container.
ENV NUMBA_CACHE_DIR=/tmp/numba_cache \
    PYTHONUNBUFFERED=1 \
    PORT=8081

WORKDIR /app

# Install deps first for better layer caching.
# Torch: on x86_64 the default PyPI wheel bundles CUDA (~2GB+), so pull the
# CPU-only build from PyTorch's index. On ARM64 (e.g. Oracle Ampere) the PyPI
# wheel is already CPU-only, and the cpu index has no aarch64 wheel — so use PyPI.
COPY requirements-server.txt .
RUN ARCH="$(uname -m)" \
 && if [ "$ARCH" = "x86_64" ]; then \
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu; \
    else \
        pip install --no-cache-dir torch; \
    fi \
 && pip install --no-cache-dir -r requirements-server.txt

# Copy the code the server actually needs.
COPY phase_3/ ./phase_3/

EXPOSE 8081

# server.py reads $PORT and chdir's into phase_3 to serve the frontend.
CMD ["python", "phase_3/server.py"]
