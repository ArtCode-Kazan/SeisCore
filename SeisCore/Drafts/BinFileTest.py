from SeisCore.BinaryFile.BinaryFile import BinaryFile

bin_data=BinaryFile()
bin_data.path='/media/michael/Data/Projects/GRP/DemkinskoeDeposit' \
              '/Demkinskoe_4771/Binary/DM08_90043_530_2019-07-28_15-10-36.00'
bin_data.record_type='ZXY'
print(bin_data.datetime_start, bin_data.datetime_stop)
# bin_data.data_type='HydroFrac'
# bin_data.resample_frequency=250
# bin_data.use_avg_values=True
# signal=bin_data.signals
# print(signal[:20,2])
# print('Ok')