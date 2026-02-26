# Minimal base image without dev tools or docs
FROM python:3.12-slim

WORKDIR /app

# Copy deps first so pip install layer is cached when only source code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY keycrack/ keycrack/
COPY run_web.py .

EXPOSE 8000

CMD ["python", "run_web.py"]
