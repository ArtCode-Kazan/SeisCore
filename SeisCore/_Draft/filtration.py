from SeisCore.Functions.BandPassFilter import band_pass_filter
import numpy as np

signal_file=r'D:\TEMP\dat\LE10_90110_709(08290000)_Z.txt'
output_file=r'D:\TEMP\dat\LE10_90110_709(08290000)_Z_11-14Hz.txt'

signal=np.loadtxt(signal_file)

filter_signal=band_pass_filter(signal,1000,11,14)
np.savetxt(output_file,filter_signal,fmt='%i')



