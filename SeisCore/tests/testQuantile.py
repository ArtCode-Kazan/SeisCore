import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import quantilies,moments_selection


file_path=r'D:\AppsBuilding\TestingData\TestHydroFrac\Result\CorrelationData' \
          r'.dat'

data=np.loadtxt(file_path)

data=data[:,0]
quants=quantilies(data)
f=moments_selection(data)
for el in f:
    print(el)