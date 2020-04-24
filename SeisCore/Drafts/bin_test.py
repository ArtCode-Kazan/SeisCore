from SeisCore.BinaryFile.BinaryFile import BinaryFile


bin_data=BinaryFile()
bin_data.path='/media/michael/Seagate Backup Plus ' \
              'Drive/Baytuganskoe_1518/Binary_Bad/HF_0011_2020-02-13_06-52-07_SigmaN008_SigmaN008.bin'
print(bin_data.record_type)
a=bin_data.signals
print(a.shape)
# bin_data.resample_frequency=500
# a=bin_data.signals
# print(a.shape)

print(bin_data.datetime_start)
print(bin_data.datetime_stop)