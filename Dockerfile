FROM ghcr.io/artcode-kazan/python:3.8.12

RUN apt-get install gcc

ENV PACKAGE_DIR=/package
RUN mkdir $PACKAGE_DIR
COPY . $PACKAGE_DIR

RUN cd $PACKAGE_DIR && poetry install --only main

ENV CYTHON_DIR=$PACKAGE_DIR/seiscore/binaryfile/resampling
RUN cd $CYTHON_DIR && python3.8 setup.py build_ext --inplace
RUN cd $CYTHON_DIR && rm -f setup.py

RUN cd $PACKAGE_DIR && python3.8 setup.py install

ENTRYPOINT ["python3.8"]