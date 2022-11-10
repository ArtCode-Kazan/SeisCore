VERSION=1.0.1
CYTHON_DIR=$(CURDIR)/seiscore/binaryfile/resampling


create-image:
	docker build -t seiscore:$(VERSION) .
	docker build -t ghcr.io/mikkoartik/seiscore:$(VERSION) .


upload-image:
	docker push ghcr.io/mikkoartik/seiscore:$(VERSION)


load-image:
	docker pull ghcr.io/mikkoartik/seiscore:$(VERSION)


install-python:
	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt install -y software-properties-common gcc wget unzip
	sudo apt autoremove -y

	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt install -y python3.8 python3.8-dev python3.8-distutils

	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3.8 get-pip.py
	sudo python3.8 -m pip install --upgrade pip


install-dependencies:
	sudo apt-get install -y gcc
	sudo python3.8 -m pip install Cython
	sudo python3.8 -m pip install numpy==1.22.0 scipy==1.6.3 \
	PyWavelets==1.1.1 matplotlib==3.4.2


after-build:
	rm -rf build && rm -rf seiscore.egg-info


create-build:
	cd $(CYTHON_DIR) && python3.8 setup.py build_ext --inplace
	cd $(CYTHON_DIR) && mv setup.py setup.pytmp

	python3.8 setup.py bdist_wheel

	cd $(CYTHON_DIR) && mv setup.pytmp setup.py
	make after-build


install:
ifeq (${python_version_major}, 3)
ifeq (${python_version_minor}, 8)
	@echo "Python version 3.8 installed"
else
	make install-python
endif
else
	make install-python
endif

	make install-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seiscore-$(VERSION)-py3-none-any.whl

	python3.8 aliases.py --install
	$(shell source ~/.bashrc)


uninstall:
	sudo python3.8 -m pip uninstall seiscore

	python3.8 aliases.py --remove
	$(shell source ~/.bashrc)


update:
	make uninstall
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seiscore-$(VERSION)-py3-none-any.whl
