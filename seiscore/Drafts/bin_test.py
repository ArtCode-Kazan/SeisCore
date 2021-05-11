from seiscore.binaryfile.BinaryFile import BinaryFile
import numpy as np
import os
import mmap
from datetime import timedelta
from datetime import datetime

from seiscore.binaryfile.cpython.Resampling.Execute import Resampling


path='/media/michael/Data/Projects/HydroFracturing/Rossikhin_1R/Binary/HF_0003_2020-02-21_00-00-00_3393_254.00'
# with open(path, 'rb') as f, mmap.mmap(f.fileno(), length=0,
#                                       access=mmap.ACCESS_READ) as mm:
#      data=np.ndarray(1000, buffer=mm, dtype=np.int32, offset=340, strides=12).copy()
bin_data = BinaryFile(path, use_avg_values=False)
# bin_data.read_date_time_stop = bin_data.datetime_start + timedelta(
#     hours=1)
# # bin_data.resample_frequency = 250
# signal=bin_data.read_signal('Z')
# resample_size=signal.shape[0]//4
#
# # arr=np.zeros(shape=resample_size, dtype=np.int)
# # for i, x in enumerate(int(sum(signal[x*4: (x+1)*4])/4) for x in range(resample_size)):
# #      arr[i]=x
# #
# t0=datetime.now()
# arr1 = np.array([int(sum(signal[x*4: (x+1)*4])/4) for x in range(
#     resample_size)], dtype=np.int)
# t1=datetime.now()
# print((t1-t0).total_seconds())
#
# arr2 = Resampling.resampling(signal, 4)
# t2=datetime.now()
# print((t2-t1).total_seconds())
#
#
print(bin_data.datetime_start)
print(bin_data.datetime_stop)
print(bin_data.file_header)
