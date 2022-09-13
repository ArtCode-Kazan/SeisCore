FROM debian:bullseye-slim

RUN apt-get update
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
RUN apt-get install -y libsqlite3-dev

RUN wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tar.xz
RUN tar -xf Python-3.8.12.tar.xz
RUN cd Python-3.8.12 && ./configure --enable-optimizations
RUN cd Python-3.8.12 && make -j 4
RUN cd Python-3.8.12 && make altinstall
RUN python3.8 -m pip install --upgrade pip

RUN apt-get install gcc
RUN python3.8 -m pip install Cython
RUN python3.8 -m pip install numpy==1.22.0 scipy==1.6.3 \
    PyWavelets==1.1.1 matplotlib==3.4.2

ENV PACKAGE_DIR=/package
ENV CYTHON_DIR=$PACKAGE_DIR/seiscore/binaryfile/resampling

RUN mkdir $PACKAGE_DIR
COPY . $PACKAGE_DIR

RUN cd $CYTHON_DIR && python3.8 setup.py build_ext --inplace
RUN cd $CYTHON_DIR && rm -f setup.py

RUN cd $PACKAGE_DIR && python3.8 setup.py install

ENTRYPOINT ["python3.8"]