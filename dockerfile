FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# ENV API_KEY=AIzaSyABaZT80ukPbyZgcww2sPyTw1cWtnvwhVU

# Expose the application port
EXPOSE 5000

# Correct CMD syntax (needs a space after CMD)
CMD ["python3", "main.py"]
