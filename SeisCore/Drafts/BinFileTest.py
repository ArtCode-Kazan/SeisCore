from SeisCore.BinaryFile.BinaryFile import BinaryFile

bin_data=BinaryFile()
bin_data.path='/media/michael/Data/Projects/GRP/DemkinskoeDeposit' \
              '/Demkinskoe_4772-4783/Binary/HF_0011_2019-08-08_17-36-24_90036_529.00'
bin_data.record_type='ZXY'
print(bin_data.datetime_start, bin_data.datetime_stop)
print(bin_data.longitude, bin_data.latitude)
# bin_data.data_type='HydroFrac'
# bin_data.resample_frequency=250
# bin_data.use_avg_values=True
# signal=bin_data.signals
# print(signal[:20,2])
# print('Ok')