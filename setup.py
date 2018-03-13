from setuptools import setup
from setuptools import find_packages


setup(name='SeisCore',
      version='0.0.16',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      zip=False,
      install_requires=['numpy', 'scipy', 'pywavelets', 'matplotlib'])
