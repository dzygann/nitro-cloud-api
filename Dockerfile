FROM public.ecr.aws/amazonlinux/amazonlinux:2

# Install python for running the server and net-tools for modifying network config
RUN amazon-linux-extras install aws-nitro-enclaves-cli -y
RUN yum install python3 iproute aws-nitro-enclaves-cli-devel -y

COPY requirements.txt ./
RUN pip3 install -r /requirements.txt


WORKDIR /app

COPY bootstrap.sh ./
COPY app.py ./

RUN chmod +x /app/bootstrap.sh

CMD ["/app/bootstrap.sh"]