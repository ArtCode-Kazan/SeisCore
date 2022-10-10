from setuptools import setup
from setuptools import find_packages


setup(
    name='seiscore',
    version='1.0.0',
    description='Package for processing of microseismic data',
    author='Michael Chernov',
    author_email='mihail.tchernov@yandex.ru',
    license='MIT',

    packages=find_packages(),
    include_package_data=True,
    zip=False,
    install_requires=[
        'numpy==1.22.0',
        'scipy==1.6.3',
        'pywavelets==1.1.1',
        'matplotlib==3.4.2'
    ],
    package_data={'seiscore': ['binaryfile/resampling/*.so']}
)
