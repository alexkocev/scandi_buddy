FROM python:3.10-slim

# Install system dependencies for Playwright and other libraries
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libgirepository1.0-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    wget \
    libnss3 \
    libxss1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    xauth \
    xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install google-cloud-storage


# Install Playwright and its browsers
RUN pip install playwright
RUN playwright install --with-deps

# Refresh font cache
RUN fc-cache -f -v

# Install Noto Emoji fonts for proper emoji rendering
RUN apt-get update && apt-get install -y \
    fonts-noto-color-emoji \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8080

# Streamlit defaults to running on port 8501
# Note: Use the host 0.0.0.0 to accept requests from outside the container
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
