import numpy as np
from seiscore.functions.Filter import sl_filter


file=r'/home/michael/Документы/Projects/SpectrumModeling/signal_No_deposits.dat'
frequency=1000
long_window=1
short_window=0.1
data=np.loadtxt(file, delimiter='\t', skiprows=1, usecols=[0, 1])
signal=data[:, 1]

long_window=int(frequency*long_window)
short_window=int(frequency*short_window)

x_lta = np.linspace(0, long_window - 1, long_window)
x_sta = np.linspace(0, short_window - 1, short_window)

coeffs=np.zeros_like(signal)
for i in range(long_window, signal.shape[0] - short_window):
    lta_window = signal[i - long_window:i]
    lin_coeff = np.polyfit(x_lta, lta_window, 1)
    lta_window = lta_window - (lin_coeff[0] * x_lta + lin_coeff[1])
    lta = np.mean(np.abs(lta_window))

    sta_window = signal[i-short_window:i]
    lin_coeff = np.polyfit(x_sta, sta_window, 1)
    sta_window = sta_window - (lin_coeff[0] * x_sta + lin_coeff[1])
    sta = np.mean(np.abs(sta_window))

    if lta == 0:
        val = 0
    else:
        val = sta / lta
    coeffs[i] = val

res=np.zeros(shape=(signal.shape[0],3))
res[:,:2]=data
res[:,2]=coeffs
np.savetxt(r'/home/michael/Temp/sl.dat',res,header='time\tsignal\tsl',
           comments='')