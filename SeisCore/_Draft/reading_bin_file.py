from SeisCore.BinaryFile.BinaryFile import BinaryFile
from datetime import datetime, timedelta
from SeisCore.Functions.Spectrogram import create_spectrogram


file_path=r'E:\GRP\Well_100_2015\src\UGM100-1_TC_61\2015_12_06_04_00_21_B8_00_ca0061.xx'
rec_type='ZXY'
cur_dt_start=datetime(2015,12,6,19,30)
cur_dt_stop=cur_dt_start+timedelta(minutes=1, seconds=-1/1000)


bin_data=BinaryFile()
bin_data.path = file_path
bin_data.record_type = rec_type
bin_data.use_avg_values = True
bin_data.resample_frequency = 250
read_dt_start = cur_dt_start
# read_dt_stop = cur_dt_stop + timedelta(
#     seconds=(100+200) / 1000)
bin_data.read_date_time_start = read_dt_start
#bin_data.read_date_time_stop = read_dt_stop
x_index, y_index, z_index = bin_data.components_index
signals = bin_data.signals
z_signal = signals[:, z_index]
print(bin_data.datetime_start)
print(bin_data.datetime_stop)
create_spectrogram(signal_data=z_signal, frequency=250,
                   output_folder=r'E:\GRP\Well_100_2015\src\UGM100-1_TC_61',
                   output_name='qww',min_frequency=0, max_frequency=100)
