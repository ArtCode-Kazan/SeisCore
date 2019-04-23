from SeisCore.BinaryFile.BinaryFile import BinaryFile

bin_data=BinaryFile()
bin_data.path='/home/michael/Temp/SKV46(C)_90109_700.00'
bin_data.resample_frequency=100
bin_data.record_type='XYZ'
bin_data.use_avg_values=True
print(bin_data.signals[:5])