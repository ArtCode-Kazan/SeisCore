import numpy as np


path = '/media/michael/Michael1/Yamburg_2020/9192_St100_P100_blank_den_xyz_50x50x50_zeros.dat'
out_path = '/media/michael/Data/TEMP/9192.dat'
data = np.loadtxt(path, skiprows=1, delimiter='\t')
data = data[data[:, 5] > 0]

data[:, 0] = np.round(data[:, 0], 3)
data[:, 1:5] = np.round(data[:, 1:5], 1)

data = data[data[:, 0].argsort()]
data = data[:, [0, 1, 2, 3, 5]]

times = set()
result = np.zeros(shape=(0, data.shape[1]))
for line in data:
    if line[0] not in times:
        result = np.vstack((result, line))
        times.add(line[0])
    else:
        continue

header = ['Time', 'x', 'y', 'z', 'density']
fmt = ['%.3f']+['%.1f'] * 3 + ['%i']
header = '\t'.join(header)
fmt = '\t'.join(fmt)
np.savetxt(out_path, result, fmt, '\t', header=header, comments='')
