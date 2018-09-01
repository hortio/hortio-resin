FROM resin/rpi-raspbian:latest
LABEL maintainer="Sergei Silnov <po@kumekay.com>"

RUN apt-get update && apt-get install -y \
    python \
    python-pip \
    git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

RUN git clone https://github.com/hortio/hortio-control-rpi.git /app

WORKDIR /app

RUN git checkout vdnh

RUN pipenv install

# Define default command
CMD ["pipenv", "run", "python", "/app/control/core.py"] 