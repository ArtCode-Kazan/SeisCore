from SeisCore.BinaryFile.BinaryFile import BinaryFile
import datetime
from pywt import Wavelet, dwt_max_level, wavedec, waverec
import numpy as np


path=r'/media/michael/Новый том/!!!Ямбург!!!!/YM_039_SigmaN006/YM_039_SigmaN006_2019-12-05_08-13-36.bin'
bin_data=BinaryFile()
bin_data.path=path
bin_data.use_avg_values=False
signals=bin_data.signals

export_path=r'/media/michael/Новый ' \
            r'том/!!!Ямбург!!!!/YM_039_SigmaN006/signals.dat'
np.savetxt(export_path,signals, '%i', delimiter='\t')




# bin_data.record_type='ZXY'
# bin_data.read_date_time_start=datetime.datetime(2019,7,13,1)
# bin_data.read_date_time_stop=datetime.datetime(2019,7,13,1,1)
# signal=bin_data.signals[:,0]
# print(signal.shape)
# wavelet_type = Wavelet('db5')
# max_levels_count = dwt_max_level(data_len=signal.shape[0],
#                                  filter_len=wavelet_type.dec_len)
# print(max_levels_count)
# result = wavedec(signal, 'db5', level=max_levels_count)
# print(len(result))

