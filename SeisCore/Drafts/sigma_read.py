from SeisCore.BinaryFile.BinaryFile import _binary_read
import struct

file = r'/media/michael/Data/Projects/GRP/DemkinskoeDeposit/Demkinskoe_4772' \
       r'-4783/DefectedBinary/HF_0012_2019-07-30_08-30-33_sigma003_sigma003.bin'

bin_data = open(file, 'rb')
ch_count = _binary_read(bin_data, 12, 'I', 1)
version = _binary_read(bin_data,0,'I',1)
resolution = _binary_read(bin_data,0,'I',1)
frequency = _binary_read(bin_data, 0, 'I', 1)
# name=_binary_read(bin_data, 0, 's',12)
latitude=_binary_read(bin_data, 12, 's',8)
longitude=_binary_read(bin_data,0, 's', 9)
start_date=_binary_read(bin_data,3,'I',1)
start_time=_binary_read(bin_data,0,'I',1)
print(frequency, latitude, longitude, start_date, start_time)
