# Use official Python slim image
FROM python:3.10-slim

# Set environment variable to disable interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies required for Playwright Chromium
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdbus-1-3 libxcomposite1 \
    libxdamage1 libxrandr2 libxss1 libasound2 libxshmfence1 \
    libgbm1 libgtk-3-0 libx11-xcb1 xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright and its browsers
RUN playwright install --with-deps

# Copy all code
COPY . .

# Set port for Railway (default 8080)
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run the app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
