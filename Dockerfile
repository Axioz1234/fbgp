FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    gnupg \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy files
COPY main.py ./

# Run Python script
CMD ["python3", "main.py"]
