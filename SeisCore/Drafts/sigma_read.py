from SeisCore.BinaryFile.BinaryFile import BinaryFile
import struct
import numpy as np

file = r'/media/michael/MAHCYP32GB/190907_55207_Sigma№002/190907_55207_Sigma№002.bin'

bin_data=BinaryFile()
bin_data.path=file
bin_data.use_avg_values=False
signal=bin_data.signals
np.savetxt(r'/media/michael/MAHCYP32GB/190907_55207_Sigma№002/signal.dat',
           signal, '%i', '\t', header='Z\tX\tY', comments='')
input()
#
# bin_data = open(file, 'rb')
# ch_count = _binary_read(bin_data, 12, 'I', 1)
# version = _binary_read(bin_data,0,'I',1)
# resolution = _binary_read(bin_data,0,'I',1)
# frequency = _binary_read(bin_data, 0, 'I', 1)
# # name=_binary_read(bin_data, 0, 's',12)
# latitude=_binary_read(bin_data, 12, 's',8)
# longitude=_binary_read(bin_data,0, 's', 9)
# start_date=_binary_read(bin_data,3,'I',1)
# start_time=_binary_read(bin_data,0,'I',1)
# print(frequency, latitude, longitude, start_date, start_time)
