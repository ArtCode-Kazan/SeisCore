from SeisCore.BinaryFile.BinaryFile import BinaryFile
from datetime import datetime,timedelta


path=r'D:\AppsBuilding\TestingData\ReviseTesting\RV_2018-07-17_05A_129.xx'
path=r'D:\AppsBuilding\TestingData\VariationTesting\VR_2018-07-05_3034_232.00'
b=BinaryFile()
b.data_type='Variation'
b.path = path
b.record_type='ZXY'
print(b.read_date_time_start, b.read_date_time_stop)
b.split_file_by_date('d:/temp')
print(b.read_date_time_start, b.read_date_time_stop)

a=datetime(year=2018,month=10,day=5).date()
c=datetime(a+timedelta(days=10,hours=5))
print(c)


