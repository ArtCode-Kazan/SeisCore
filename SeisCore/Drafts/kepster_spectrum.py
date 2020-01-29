from SeisCore.Functions.Spectrum import spectrum
import numpy as np


signal = np.loadtxt(r'/home/michael/Документы/AppsBuilding/DevitoPackage'
                    r'/drafts/source_meander_1Hz_h=3900_newQ3.dat',
                    skiprows=1)
signal=signal[signal[:,0]>5100]


freq = 1 / (signal[1, 0] - signal[0, 0]) * 1000
signal = signal[:, 3]

# signal=np.random.randint(-1000,1000,10000)

spectrum_data = spectrum(signal=signal, frequency=freq)

dt_fict = spectrum_data[1, 0] - spectrum_data[0, 0]
frec_fict = 1 / dt_fict

kepster_spectrum = spectrum(signal=spectrum_data[:, 1], frequency=frec_fict)
np.savetxt('kepster_empty.dat', kepster_spectrum, delimiter='\t')
