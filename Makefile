VERSION="1.0.1"
CYTHON_DIR=$(CURDIR)/seiscore/binaryfile/resampling


create-image:
	docker build -t seiscore:$(VERSION) .
	docker build -t ghcr.io/mikkoartik/seiscore:$(VERSION) .


upload-image:
	docker push ghcr.io/mikkoartik/seiscore:$(VERSION)


load-image:
	docker pull ghcr.io/mikkoartik/seiscore:$(VERSION)


python-install:
	sudo apt-get update
	sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
	sudo apt-get install -y libsqlite3-dev

	wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tar.xz
	tar -xf Python-3.8.12.tar.xz
	cd Python-3.8.12 && ./configure --enable-optimizations
	cd Python-3.8.12 && make -j 4
	cd Python-3.8.12 && make altinstall
	python3.8 -m pip install --upgrade pip
	rm -rf Python-3.8.12.tar.xz Python-3.8.12


package-install:
	sudo apt-get install -y gcc
	python3.8 -m pip install Cython
	python3.8 -m pip install numpy==1.22.0 scipy==1.6.3 \
    PyWavelets==1.1.1 matplotlib==3.4.2

	cd $(CYTHON_DIR) && python3.8 setup.py build_ext --inplace
	cd $(CYTHON_DIR) && rm -f setup.py

	python3.8 setup.py install
