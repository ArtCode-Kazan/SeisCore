import numpy as np

file_path=r'/home/michael/Documents/AppsBuildings/Work/TestingData/2Minsumres100.txt'

data=np.loadtxt(file_path)

def quantilies(data,procents=[95,96,97,98]):
    result=list()
    for procent in procents:
        current_quantile=np.percentile(data,procent)
        result.append(current_quantile)
    print(result)

quantilies(data)
