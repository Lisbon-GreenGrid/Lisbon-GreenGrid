# Multi-stage Dockerfile for NCDC Tree Inventory API
FROM python:3.11-slim as builder

WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

# Security: Don't run as root
RUN groupadd -r ncdc && useradd -r -g ncdc ncdc

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/ncdc/.local

# Copy application code
COPY api/ /app/

# Create directory for uploaded images
RUN mkdir -p /app/uploaded_images && chown -R ncdc:ncdc /app

# Set environment
ENV PATH=/home/ncdc/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER ncdc

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "api:app"]
