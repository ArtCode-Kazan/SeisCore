import numpy as np
from SeisCore.GeneralCalcFunctions.BandPassFilter import band_pass_filter

signal=np.loadtxt(fname=r'/home/michael/Documents/AppsBuildings/Work'
                           r'/TestingData/TestingHydroFrac/Result/begin_data'
                           r'.dat')

frequency=1000
f_min=10
f_max=100

res=band_pass_filter(signal,1000,5,50)

np.savetxt(r'/home/michael/Documents/AppsBuildings/Work'
                           r'/TestingData/TestingHydroFrac/Result/filtered_data'
                           r'.dat',res)

# W = fftfreq(signal.size, d=1.0/frequency)
# f_signal = fft(signal)
#
# a=f_signal
#
# # If our original signal time was in seconds, this is now in Hz
# cut_f_signal = f_signal.copy()
# cut_f_signal[(W<f_min)+(W>f_max)] = 0
#
# b=cut_f_signal
#
# cut_signal = ifft(cut_f_signal)
#
# import pylab as plt
# plt.subplot(121)
# plt.plot(W,a)
# plt.subplot(122)
# plt.plot(W,b)
# plt.show()
