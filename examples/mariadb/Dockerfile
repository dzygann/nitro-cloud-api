FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8


RUN apt-get update -y
RUN apt-get install mariadb-server -y

# Move this line into the entrypoint.sh, otherwise the db isn't started
#RUN service mariadb start

RUN mkdir database_connector

WORKDIR /database_connector

COPY database.py .



#RUN sed -i -e "s/^bind\-address/#bind\-address/g" /etc/mysql/mariadb.conf.d/50-server.cnf
#RUN sed -i -e "s/^#general_log/general_log/g" /etc/mysql/mariadb.conf.d/50-server.cnf
#RUN sed -i -e "s/^query_cache_limit\ .*/query_cache_limit\ =\ 0M/g" /etc/mysql/mariadb.conf.d/50-server.cnf
#RUN sed -i -e "s/^query_cache_size\ .*/query_cache_size\ =\ 0M/g" /etc/mysql/mariadb.conf.d/50-server.cnf
#RUN sed -i -e "s/^#log_error/log_error/g" /etc/mysql/mariadb.conf.d/50-server.cnf

EXPOSE 80 3306




CMD ["echo", "Hello Denis!"]