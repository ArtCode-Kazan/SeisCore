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
          'numpy==1.19.5',
          'scipy==1.5.4',
          'pywavelets==1.1.1',
          'matplotlib==3.3.4'],
      package_data={'Resampling': ['*.so']})
