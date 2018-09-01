FROM resin/rpi-raspbian:latest
LABEL maintainer="Sergei Silnov <po@kumekay.com>"

RUN apt-get update && apt-get install -y \
    python \
    python-pip \
    git \
    build-essential \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

RUN mkdir /app

WORKDIR /app

RUN git clone https://github.com/hortio/hortio-control-rpi.git /app && git checkout 7c99e771babb3f8addc5ba70edab4977a68dd50d

RUN pipenv install

# Define default command
CMD ["pipenv", "run", "python", "/app/control/core.py"] 