from SeisCore.BinaryFile.BinaryFile import BinaryFile
import datetime
from pywt import Wavelet, dwt_max_level, wavedec, waverec



path=r'/media/michael/Seagate Backup Plus ' \
     r'Drive/Lachel_2019/LachelProject/Binary/HF_0001_2019-07-13_00-00-00_90109_243.00'
bin_data=BinaryFile()
bin_data.path=path
bin_data.record_type='ZXY'
bin_data.read_date_time_start=datetime.datetime(2019,7,13,1)
bin_data.read_date_time_stop=datetime.datetime(2019,7,13,1,1)
signal=bin_data.signals[:,0]
print(signal.shape)
wavelet_type = Wavelet('db5')
max_levels_count = dwt_max_level(data_len=signal.shape[0],
                                 filter_len=wavelet_type.dec_len)
print(max_levels_count)
result = wavedec(signal, 'db5', level=max_levels_count)
print(len(result))

