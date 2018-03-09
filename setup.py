from setuptools import setup
from setuptools import find_packages
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True


setup(name='SeisCore',
      version='0.0.11',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      zip=False,
      include_package_data=True,
      distclass=BinaryDistribution,
      package_data={'HydroFracCore/CalcFunctions/CLibrary': [
       'CorrelationCalculation.cpython-36m-i386-linux-gnu.so']},
      install_requires=['numpy', 'scipy', 'pywavelets', 'matplotlib',
                        'Cython'])
