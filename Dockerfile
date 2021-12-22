FROM python:3.8-slim

ENV APP_DIR=/app

RUN mkdir $APP_DIR

COPY . $APP_DIR

RUN apt-get update && apt-get -y install make
RUN cd $APP_DIR && make run

ENTRYPOINT ["bash"]