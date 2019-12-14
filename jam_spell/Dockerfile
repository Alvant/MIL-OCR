FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip \
    python3-wheel \
    python3-virtualenv \
    swig3.0 \
    locales --no-install-recommends\
    && apt-get clean \
    && apt-get autoremove

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN locale-gen en_US.UTF-8
RUN pip install pika
ADD . /home/app
WORKDIR /home/app

CMD ["python server.py"]