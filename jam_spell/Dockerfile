FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip \
    python3-wheel \
    python3-virtualenv \
    swig3.0 \
    locales \
    build-essential \
    python-dev \
    python3-dev \
    g++-5 \
    gcc-5 \
    && apt-get clean \
    && apt-get autoremove

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 10
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 20
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 10
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 20
RUN update-alternatives --install /usr/bin/cc cc /usr/bin/gcc 30
RUN update-alternatives --set cc /usr/bin/gcc
RUN update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 30
RUN update-alternatives --set c++ /usr/bin/g++

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN locale-gen en_US.UTF-8
RUN pip install pika
RUN pip install jamspell
ADD . /home/app
WORKDIR /home/app
