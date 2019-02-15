import os
import numpy as np

work_directory=r'/home/michael/Documents/AppsBuildings/Work/TestingData/GRP/Test/'

points_numbers=[1,2,7,8,9,11,16,17,19,20,21]
base_point=1
moment_delays=[(2,(-1,1)),
(7,(3,24)),
(8,(-1,12)),
(9,(-1,14))	,
(11,(-1,14)),
(16,(25,61)),
(17,(24,59)),
(19,(16,47)),
(20,(15,46)),
(21,(24,59))]

left_buffer=200
window_size=100
right_buffer=200+window_size
frequency=1000

signals=np.empty(shape=0, dtype=float)

for el in points_numbers:
    file_path=os.path.join(work_directory,str(el)+'.txt')
    left_edge=0
    right_edge=60*frequency+left_buffer+right_buffer
    sig=np.loadtxt(fname=file_path, dtype=float)
    signals=np.append(signals,sig[:right_edge])
    print(el)

columns=len(points_numbers)
rows=signals.shape[0]//columns
signals=np.reshape(a=signals,newshape=(rows,columns))
print(signals.shape)


