FROM python:3.11-slim

# Prevent python buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]