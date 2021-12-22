CUR_DIR = $(CURDIR)
CYTHON_FOLDER = $(CUR_DIR)/"seiscore/binaryfile/resampling"

.PHONY: run

seiscore-uninstall:
	pip uninstall -y seiscore

requirements-install:
	pip install -r requirements.txt

cython-preparing:
	apt-get -y install gcc
	pip install Cython
	cd $(CYTHON_FOLDER) && rm -rf *.so *.c

cython-compile:
	cd $(CYTHON_FOLDER) && python setup.py build_ext --inplace
	cd $(CYTHON_FOLDER) && rm -f setup.py

seiscore-install:
	python setup.py install

cython-clean:
	apt-get -y remove --purge make gcc
	pip uninstall -y Cython

clean:
	rm -rf $(APP_DIR)

run: seiscore-uninstall requirements-install cython-preparing cython-compile seiscore-install cython-clean clean
