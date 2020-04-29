from setuptools import setup
from setuptools import find_packages
setup(name='SeisCore',
      version='0.3.18',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      include_package_data=True,
      zip=False,
      install_requires=[
            'numpy==1.16.3',
            'scipy==1.2.1',
            'pywavelets==1.0.2',
            'matplotlib==2.1.1',
            'segyio==1.8.8'])
