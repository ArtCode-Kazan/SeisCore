from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy


extentions=['Energy','Filter','NormingSignal','Spectrogram','Spectrum']

for el in extentions:
    setup(
        cmdclass = {'build_ext': build_ext},
        ext_modules = [Extension(el, ["{}.pyx".format(el)],
                                 include_dirs=[numpy.get_include()])]
)