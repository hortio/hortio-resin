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

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

WORKDIR /app

RUN pipenv install

COPY . /app

ENV FLASK_ENV=production

EXPOSE 5000

# Define default command
CMD ["pipenv", "run", "python", "api.py"] 