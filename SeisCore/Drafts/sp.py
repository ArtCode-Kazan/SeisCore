from SeisCore.BinaryFile.BinaryFile import BinaryFile

path=r'/media/michael/LinuxHome/07261007u90037.00'
bin_data=BinaryFile()
bin_data.path=path
bin_data.record_type='ZXY'
print(bin_data.check_correct())
print(bin_data.datetime_start)
print(bin_data.datetime_stop)
print()