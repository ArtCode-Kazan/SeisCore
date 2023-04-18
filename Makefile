IMAGE_NAME=seiscore
VERSION=1.0.1
DOCKER_USERNAME=artcode-kazan

CYTHON_DIR=$(CURDIR)/seiscore/binaryfile/resampling

create-image:
	docker build -t $(IMAGE_NAME):$(VERSION) .
	docker build -t ghcr.io/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(VERSION) .


upload-image:
	. ~/.profile && \
	echo $(CR_PAT) | docker login ghcr.io -u $(DOCKER_USERNAME) --password-stdin
	docker push ghcr.io/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(VERSION)


install-python:
	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
	sudo apt-get install -y libsqlite3-dev
	sudo apt autoremove -y

	wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tar.xz
	tar -xf Python-3.8.12.tar.xz
	cd Python-3.8.12 && ./configure --enable-optimizations
	cd Python-3.8.12 && make -j 4
	cd Python-3.8.12 && make altinstall
	rm -rf Python-3.8.12.tar.xz Python-3.8.12

	wget https://bootstrap.pypa.io/get-pip.py
	python3.8 get-pip.py && sudo python3.8 -m pip install --upgrade pip
	rm -f get-pip.py
	sudo python3.8 -m pip install poetry


install-dependencies:
	sudo apt-get install -y gcc
	sudo poetry install --no-root


create-build:
	cd $(CYTHON_DIR) && python3.8 setup.py build_ext --inplace
	cd $(CYTHON_DIR) && mv setup.py setup.pytmp

	python3.8 setup.py bdist_wheel

	cd $(CYTHON_DIR) && mv setup.pytmp setup.py
	rm -rf build && rm -rf seiscore.egg-info


install:
	make install-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seiscore-$(VERSION)-py3-none-any.whl


uninstall:
	sudo python3.8 -m pip uninstall -y seiscore


update:
	make uninstall
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seiscore-$(VERSION)-py3-none-any.whl
