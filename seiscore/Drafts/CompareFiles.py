from seiscore.binaryfile.BinaryFile import BinaryFile
import numpy as np


origin_file=r'/home/michael/Загрузки/K42/YM_027_K42_2019-11-30_09-49.00'
test_file=r'/home/michael/Загрузки/K42/parts/file.00'

origin_bin=BinaryFile()
origin_bin.path=origin_file
origin_bin.use_avg_values=False
print(origin_bin.discrete_amount, origin_bin.signals.shape[0])

test_bin=BinaryFile()
test_bin.path=test_file
test_bin.use_avg_values=False

for i in range(3):
    diff=np.abs(origin_bin.signals[:,i]-test_bin.signals[:,i])
    print(np.max(diff))

