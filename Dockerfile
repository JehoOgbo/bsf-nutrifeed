# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies (needed for some python packages and healthchecks)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (Defaults)
ENV FLASK_APP=app.py
ENV DB_TYPE=mysql

# Start the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "api.v0.app:app"]
#CMD ["python3", "-m", "api.v0.app"]
