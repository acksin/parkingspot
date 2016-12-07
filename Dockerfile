FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y ca-certificates git

RUN rm -rf /tmp/* /var/tmp/*

ENV ACKSIN_ENV production

COPY website /website
COPY parkingspot /parkingspot

EXPOSE 8081

ENTRYPOINT /parkingspot
