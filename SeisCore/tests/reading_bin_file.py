from SeisCore.BinaryFile.BinaryFile import BinaryFile
from datetime import datetime, timedelta

file_path=r'E:\GRP\PashninskoeDeposit_2018\src\Points_1-10\563_PS03_3289_238\563_PS03_3289_238_180805.00'
rec_type='ZXY'
cur_dt_start=datetime(2018,8,5,13,32)
cur_dt_stop=cur_dt_start+timedelta(minutes=1, seconds=-1/1000)


bin_data=BinaryFile()
bin_data.path = file_path
bin_data.record_type = rec_type
bin_data.use_avg_values = True
read_dt_start = cur_dt_start + timedelta(
    seconds=-200 / 1000)
read_dt_stop = cur_dt_stop + timedelta(
    seconds=(100+200) / 1000)
bin_data.read_date_time_start = read_dt_start
bin_data.read_date_time_stop = read_dt_stop
x_index, y_index, z_index = bin_data.components_index
signals = bin_data.signals
z_signal = signals[:, z_index]
print(z_signal)