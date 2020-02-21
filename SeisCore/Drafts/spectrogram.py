from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.Functions.Spectrogram import create_spectrogram
from datetime import timedelta


bin_file=r'/media/michael/77E9-B4C6/YM_002_K14_2019-12-08_04-30-40.xx'
bin_data=BinaryFile()
bin_data.path=bin_file
bin_data.resample_frequency=250
bin_data.read_date_time_start=bin_data.datetime_start+timedelta(minutes=30)
bin_data.read_date_time_stop=bin_data.datetime_start+timedelta(minutes=60)
signal_z=bin_data.signals[:,0]

create_spectrogram(signal_z,250,'/media/michael/77E9-B4C6','test2',1,30,0)