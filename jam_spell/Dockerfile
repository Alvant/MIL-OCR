FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install git -y \
    python3 \
    python3-pip \
    cmake \
    locales \
    && apt-get clean \
    && apt-get autoremove

RUN locale-gen en_US.UTF-8

ADD . /home/app
WORKDIR /home/app

RUN git clone https://github.com/bakwc/JamSpell.git && \
    cd JamSpell && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make

EXPOSE 80
CMD ["./JamSpell/build/web_server/web_server en.bin localhost 80"]