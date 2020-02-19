from SeisCore.Functions.Spectrum import spectrum
import numpy as np


signal = np.loadtxt(r'/media/michael/Data/Projects/Yamburg/Modeling/'
                    r'ModelPreparing/Well_1056/'
                    r'source_meander_1Hz_h=3900_BottomKp=50.dat',
                    skiprows=1)
signal=signal[signal[:,0]>5100]

spectrum=np.fft.fft(signal[:,0])
ceps=np.fft.ifft(np.log(np.abs(spectrum))).real

pass




# freq = 1 / (signal[1, 0] - signal[0, 0]) * 1000
# signal = signal[:, 3]
#
# # signal=np.random.randint(-1000,1000,10000)
#
# spectrum_data = spectrum(signal=signal, frequency=freq)
#
# dt_fict = spectrum_data[1, 0] - spectrum_data[0, 0]
# frec_fict = 1 / dt_fict
#
# kepster_spectrum = spectrum(signal=spectrum_data[:, 1], frequency=frec_fict)
# np.savetxt('kepster_empty.dat', kepster_spectrum, delimiter='\t')
