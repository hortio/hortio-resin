FROM resin/rpi-raspbian:latest
LABEL maintainer="Sergei Silnov <po@kumekay.com>"

RUN apt-get update 
RUN apt-get install -y \
    python \
    python-dev \
    python-pip \
    python-smbus \
    build-essential \
    --no-install-recommends

RUN pip install pipenv

COPY . /app

WORKDIR /app

RUN pipenv install

# Define default command
CMD ["pipenv", "run", "python", "/app/control/core.py"] 