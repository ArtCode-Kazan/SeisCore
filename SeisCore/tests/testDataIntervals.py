import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import moments_selection

file_path = r'/home/michael/Documents/AppsBuildings/Work/TestingData/2Minsumres100.txt'

data=np.loadtxt(file_path)

res= moments_selection(data, procents=[95, 96, 97, 98,99], epsilon=0)

for el in res:
    print(el)