import os
import numpy as np
from seiscore.binaryfile.BinaryFile import BinaryFile


root=r'/home/michael/Загрузки/K42/parts'
output_file_name='file.00'


file_statistics=list()
for file in os.listdir(root):
    path=os.path.join(root, file)
    bin_data=BinaryFile()
    bin_data.path=os.path.join(root, file)
    file_statistics.append((path, bin_data.datetime_start, bin_data.datetime_stop))
    print(bin_data.discrete_amount)

file_statistics=sorted(file_statistics,key=lambda x: x[1])
is_right=True
for i in range(len(file_statistics)-1):
    t_stop=file_statistics[i][2]
    t_start=file_statistics[i+1][1]
    dt = (t_start-t_stop).total_seconds()
    if dt!=0.001:
        is_right=False
        break

if not is_right:
    print('Different parts. The long time delay between signal parts')
    exit()

join_signal_data=np.zeros(shape=(0, 3), dtype=np.int32)
for item in file_statistics:
    bin_data=BinaryFile()
    bin_data.path=item[0]
    bin_data.use_avg_values=False
    join_signal_data=np.vstack((join_signal_data, bin_data.signals))
    print(bin_data.signals.shape[0], join_signal_data.shape[0])

with open(os.path.join(root, output_file_name), 'wb') as handle:
    first_binary=BinaryFile()
    first_binary.path=file_statistics[0][0]

    main_header=first_binary.main_header.get_binary_format()
    channel_headers_hole = np.array([0] * 54, dtype=np.int32)

    handle.write(main_header)
    channel_headers_hole.tofile(handle)
    join_signal_data.astype(np.int32).tofile(handle)








print(join_signal_data.shape)
#
#
# print(file_statistics)