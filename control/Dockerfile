FROM resin/rpi-raspbian:latest
LABEL maintainer="Sergei Silnov <po@kumekay.com>"

RUN apt-get update && apt-get install -y \
    python \
    python-dev \
    python-pip \
    build-essential \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

COPY . /app

WORKDIR /app

RUN pipenv install

# Define default command
CMD ["pipenv", "run", "python", "/app/control/core.py"] 