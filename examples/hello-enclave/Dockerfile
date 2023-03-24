FROM amazonlinux

RUN yum install python3 gcc net-tools -y

WORKDIR /app

COPY libnsm.so ./

COPY hello-enclave.py ./
COPY traffic_forwarder.py ./
COPY bootstrap.sh ./

RUN chmod +x bootstrap.sh
CMD ["/app/bootstrap.sh"]