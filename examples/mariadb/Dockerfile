FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8


RUN apt-get update -y
RUN apt-get install mariadb-server -y

RUN mkdir database_connector

WORKDIR /database_connector

COPY database.py .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 80 3306

CMD["/database_connector/entrypoint.sh"]