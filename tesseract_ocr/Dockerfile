FROM ubuntu:18.04
RUN apt-get update \
    && apt-get install tesseract-ocr -y \
    python3 \
    python3-pip \
    && apt-get clean \
    && apt-get autoremove

ADD . /home/app
WORKDIR /home/app

EXPOSE 80
CMD ["whereis tesseract"]