FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY templates ./templates

# ENV API_KEY=AIzaSyDhl9aVb4lDgplcd-3-E_9fJiJ_hxyVKks/

EXPOSE 5000
CMD ["python", "main.py"]

