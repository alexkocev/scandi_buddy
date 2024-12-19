FROM python:3.10-slim


# Install dependencies, including fonts
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libgirepository1.0-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install core fonts and Inter
RUN apt-get update && apt-get install -y \
fonts-liberation \
fonts-dejavu \
fonts-noto-color-emoji \
fonts-freefont-ttf \
wget \
&& apt-get clean && rm -rf /var/lib/apt/lists/*



# Refresh font cache
RUN fc-cache -f -v


# Install Noto Emoji fonts for proper emoji rendering
RUN apt-get update && apt-get install -y \
    fonts-noto-color-emoji \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

    # RUN apt-get update && apt-get install -y fonts-liberation fonts-dejavu




# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Copy your requirements and install
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt



# Expose the default Streamlit port
EXPOSE 8080

# Streamlit defaults to running on port 8501
# Note: Use the host 0.0.0.0 to accept requests from outside the container
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]



# FROM python:3.10


# Copy your requirements and install
# COPY requirements.txt /app
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
# COPY . /app

# Expose the default Streamlit port
# EXPOSE 8080

# Streamlit defaults to running on port 8501
# Note: Use the host 0.0.0.0 to accept requests from outside the container
# CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
