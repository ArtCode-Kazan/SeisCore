from setuptools import setup
from setuptools import find_packages


setup(name='seiscore',
      version='0.5.0',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      include_package_data=True,
      zip=False,
      install_requires=[
          'numpy==1.20.3',
          'scipy==1.6.3',
          'pywavelets==1.1.1',
          'matplotlib==3.4.2'],
      package_data={'seiscore': ['binaryfile/resampling/*.so']})
