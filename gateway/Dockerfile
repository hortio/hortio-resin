FROM resin/rpi-raspbian:latest
LABEL maintainer="Sergei Silnov <po@kumekay.com>"

RUN apt-get update 
RUN apt-get install -y \
    openssh-client \
    --no-install-recommends

ENV GATEWAY_TARGET 127.0.0.1:80
ENV GATEWAY_HOST root@gw.kumekay.com
ENV GATEWAY_SSH_PORT 2222
ENV GATEWAY_PUBLIC_PORT 5001

CMD ssh -R ${GATEWAY_PUBLIC_PORT}:${GATEWAY_TARGET} -N ${GATEWAY_HOST} -p ${GATEWAY_SSH_PORT}
