from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf

from SeisCore.MSICore.CalcFunctions.PureSignal_experiment import pure_signal
from SeisCore.MSICore.CalcFunctions.PureSignal import pure_signal as ps0

import numpy as np

file_path = r'D:\AppsBuilding\TestingData\BinData\07120900u90007' \
            r'\07120900u90007.00'

coeff1=3*10**(-7)
coeff2=2000
window=8192
noverlap=256
f_min=0
f_max=10
df=0.5

data=rsf(file_path=file_path)

signal_x=data.signals[:,1]
signal_y=data.signals[:,2]
signal_z=data.signals[:,0]

# res=pure_signal(signal_x=signal_x,signal_y=signal_y,signal_z=signal_z,
#                 sensor_coeff=coeff1,registrator_coeff=coeff2,
#                 frequency=data.frequency,window=window,overlap=noverlap,
#                 f_min=f_min,f_max=f_max, df=df)

res2=ps0(signal=signal_x,sensor_coeff=coeff1,registrator_coeff=coeff2,
         frequency=data.frequency,window=window,overlap=noverlap,
         f_min=f_min,f_max=f_max, df=df, clipping_before=None,
         clipping_after=None)

write_array=np.empty((window,2),dtype=np.int32)
write_array[:, 0] = np.arange(res2[0],res2[1] + 1, 1)
write_array[:, 1] = signal_x[res2[0]:res2[1]+1]
np.savetxt('D:/TEMP/signal_x.dat',write_array)

res2=ps0(signal=signal_y,sensor_coeff=coeff1,registrator_coeff=coeff2,
         frequency=data.frequency,window=window,overlap=noverlap,
         f_min=f_min,f_max=f_max, df=df,clipping_before=None,
         clipping_after=None)

write_array[:, 1] = signal_x[res2[0]:res2[1]+1]
np.savetxt('D:/TEMP/signal_y.dat',write_array)

res2=ps0(signal=signal_z,sensor_coeff=coeff1,registrator_coeff=coeff2,
         frequency=data.frequency,window=window,overlap=noverlap,
         f_min=f_min,f_max=f_max, df=df,clipping_before=None,
         clipping_after=None)

write_array[:, 1] = signal_x[res2[0]:res2[1]+1]
np.savetxt('D:/TEMP/signal_z.dat',write_array)


