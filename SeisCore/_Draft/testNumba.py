import numpy as np

a=np.array([[0,1],[1,2],[2,3]])

b=np.array([1,1])
if b in a:
    print('ok')
else:
    print('No')