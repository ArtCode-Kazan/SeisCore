import numpy as np
from seiscore.functions.Spectrum import spectrum, nakamura_spectrum
from seiscore.functions.Energy import spectrum_energy

signal_file = r'/media/michael/Data/Projects/Yamburg/Modeling/ModelPreparing' \
              r'/Well_30302/CompleteModeling/signal_test.dat'
coords_file = r'/media/michael/Data/Projects/Yamburg/Modeling/ModelPreparing' \
              r'/Well_30302/CompleteModeling/Points_coords.dat'
export_file = r'/media/michael/Data/Projects/Yamburg/Modeling/ModelPreparing' \
              r'/Well_30302/CompleteModeling/ClusterDataSrc.dat'
t_min = 8
selection_size = 50

signal_data = np.loadtxt(signal_file, skiprows=1, delimiter='\t')
signal_data[:, 0] = signal_data[:, 0] / 1000
signal_data = signal_data[signal_data[:, 0] >= t_min]

frequency = 1 / (signal_data[1, 0] - signal_data[0, 0])
with open(signal_file, 'r') as handle:
    header = handle.readline()

header = header.split('\t')
header = header[1:][::3]

sensor_numbers = list()
for item in header:
    item = item[3:]
    t = item.split('_')
    # number = int(t[0])
    number = int(t[1])
    sensor_numbers.append(number)

# sensor_numbers=sensor_numbers[:selection_size]

coords_data = dict()
with open(coords_file, 'r') as handle:
    for index, line in enumerate(handle):
        if index == 0:
            continue
        t = line.strip().split('\t')
        number = int(t[0])
        x, y = [float(q) for q in t[1:]]
        coords_data[number] = (x, y)


f_intervals = [[4, 4.32], [28,30]]
intervals_count = len(f_intervals)
point_count = len(sensor_numbers)

result = None
freq_array = None
for index in range(point_count):
    signal = signal_data[:, 1 + 3 * index:1 + 3 * (index + 1)]
    x, y = coords_data[sensor_numbers[index]]

    sp_x = spectrum(signal=signal[:, 0], frequency=frequency)
    sp_y = spectrum(signal=signal[:, 1], frequency=frequency)
    sp_z = spectrum(signal=signal[:, 2], frequency=frequency)

    join_sp_data = np.zeros(shape=(sp_x.shape[0], 5))
    join_sp_data[:, :2] = sp_x
    join_sp_data[:, 2] = sp_y[:, 1]
    join_sp_data[:, 3] = sp_z[:, 1]

    nak_sp = nakamura_spectrum(components_spectrum_data=join_sp_data,
                               components_order='XYZ', spectrum_type='VH')
    if result is None:
        result = np.zeros(shape=(point_count, sp_x.shape[0], 4))
        freq_array = sp_x[:, 0]

    result[index, :, 0] = sp_x[:, 1]
    result[index, :, 1] = sp_y[:, 1]
    result[index, :, 2] = sp_z[:, 1]
    result[index, :, 3] = nak_sp[:, 1]

matrix = np.zeros(shape=(point_count, intervals_count * 2 + 3))
header = ['Point', 'x', 'y']
for i in range(point_count):
    num = sensor_numbers[i]
    if num>100:
        num=num%100
    x, y = coords_data[num]
    for j, interval in enumerate(f_intervals):
        f_min, f_max = interval
        imin = np.argmax(freq_array >= f_min)
        imax = np.argmin(freq_array < f_max)

        sp_z = result[i, imin:imax, 2]
        sp = np.zeros(shape=(sp_z.shape[0], 2))
        sp[:, 0] = freq_array[imin:imax]
        sp[:, 1] = sp_z
        e_fourier = spectrum_energy(spectrum_data=sp)*1e8

        sp_nak = result[i, imin:imax, 3]
        sp = np.zeros(shape=(sp_nak.shape[0], 2))
        sp[:, 0] = freq_array[imin:imax]
        sp[:, 1] = sp_nak
        e_nak = spectrum_energy(sp)*1000

        matrix[i, 0] = num
        matrix[i, 1] = x
        matrix[i, 2] = y
        matrix[i, 3 + 2 * j] = e_fourier
        matrix[i, 4 + 2 * j] = e_nak
        if f'Ez_{f_min}-{f_max}' not in header:
            header += [f'Ez_{f_min}-{f_max}', f'VH_{f_min}-{f_max}']

# min_vals=np.min(matrix[:,3:], axis=0)
# max_vals=np.max(matrix[:,3:], axis=0)
# matrix[:,3:]=(matrix[:,3:]-min_vals)/(max_vals-min_vals)

header = '\t'.join(header)
np.savetxt(export_file, matrix, '%f', '\t', header=header, comments='')
