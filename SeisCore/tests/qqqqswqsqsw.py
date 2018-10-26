from SeisCore.BinaryFile.BinaryFile import BinaryFile

path=r'D:\AppsBuilding\TestingData\ReviseTesting\RV_2018-07-17_05A_129.xx'

b=BinaryFile()
b.path = path
print(b.main_header.station_name)
