from SeisCore.Functions.Spectrum import spectrum
import numpy as np


file=r'D:\TEMP\spectrums\57P_066_135_den_sig_Z_nTnWnN.dat'
data=np.loadtxt(file)
signal=data[:,1]

spec_a = spectrum(signal, 250)
spec_b = spectrum(signal[:signal.shape[0]//2], 250)
spec_c = spectrum(signal[signal.shape[0]//2:], 250)

np.savetxt(r'D:\TEMP\spectrums\full_a2.dat', spec_a, fmt='%f', delimiter='\t')
np.savetxt(r'D:\TEMP\spectrums\half_b2.dat', spec_b, fmt='%f', delimiter='\t')
np.savetxt(r'D:\TEMP\spectrums\half_c2.dat', spec_c, fmt='%f', delimiter='\t')

data=np.loadtxt(r'D:\TEMP\spectrums\full_a2.dat')
data=data[::2]
np.savetxt(r'D:\TEMP\spectrums\full_res2.dat', data, fmt='%f', delimiter='\t')



