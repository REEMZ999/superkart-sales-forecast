# Python base image matching the training environment
FROM python:3.13-slim

# Working directory inside the container
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# Flask API listens on port 7860
EXPOSE 7860

# Serve the Flask app (object "superkart_api" in app.py) with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "120", "app:superkart_api"]
