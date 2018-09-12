# Setup for Linux
from distutils.core import setup
# from distutils.extension import Extension
# from Cython.Distutils import build_ext
# import numpy
#
# setup(
#     cmdclass = {'build_ext': build_ext},
#     ext_modules = [Extension("SelectionMoments",
#                              ["Resampling.pyx"],
#                              include_dirs=[numpy.get_include()])]
# )

# Setup for Windows
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("Resampling",
                             ["Resampling.pyx"],
                             include_dirs=[numpy.get_include()])]
)