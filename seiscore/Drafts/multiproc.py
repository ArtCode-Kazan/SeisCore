from multiprocessing import Pool
from multiprocessing import cpu_count
import numpy as np


def core(data, limits):
    result = 0
    for x in data[limits[0]:limits[1]]:
        result += x
    return result/data.shape[0]


arr = np.random.randint(-1000, 1000, 30000000)
for i in range(3):
    print(np.mean(arr[i*10000000: (i+1)*10000000]))

procs = Pool(cpu_count())
mapper = procs.map(core, [arr]*3, [(i*10000000, (i+1)*10000000) for i in range(3)])
print(mapper)
