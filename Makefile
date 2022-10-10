# Makefile only for UBUNTU 18.04


VERSION=1.0.0
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
	sudo apt-get -y upgrade
	sudo apt install -y software-properties-common gcc wget unzip
	sudo apt autoremove -y

	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt install -y python3.8 python3.8-dev python3.8-distutils

	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3.8 get-pip.py
	sudo python3.8 -m pip install --upgrade pip


package-install:
	sudo apt-get install -y gcc
	sudo python3.8 -m pip install Cython
	sudo python3.8 -m pip install numpy==1.22.0 scipy==1.6.3 \
    PyWavelets==1.1.1 matplotlib==3.4.2

	cd $(CYTHON_DIR) && python3.8 setup.py build_ext --inplace
	cd $(CYTHON_DIR) && rm -f setup.py

	python3.8 setup.py bdist_wheel
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seiscore-$(VERSION)-py3-none-any.whl
