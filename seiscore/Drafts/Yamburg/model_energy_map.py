import numpy as np

from seiscore.functions.Spectrum import average_spectrum
from seiscore.functions.Spectrum import nakamura_spectrum
from seiscore.functions.Energy import spectrum_energy
from seiscore.plotting.Plotting import plot_graph


def get_avg_spectrums(signals, frequency, avg_sp_params):
    smooth_avg_specs = None
    for index in range(signals.shape[1]):
        s_avg_spec = average_spectrum(signal=signals[:, index],
                                      frequency=frequency,
                                      window=avg_sp_params['window'],
                                      offset=avg_sp_params['offset'],
                                      median_filter=avg_sp_params['med_filter'],
                                      marmett_filter=avg_sp_params[
                                          'marmett_filter'])
        if smooth_avg_specs is None:
            smooth_avg_specs=s_avg_spec
        else:
            smooth_avg_specs=np.column_stack(
                (smooth_avg_specs, s_avg_spec[:,1]))
    return smooth_avg_specs


signal_file = r'/media/michael/Data/TEMP/signal_test.dat'
coords_file = r'/media/michael/Data/TEMP/Points_coords.dat'
output_folder = r'/media/michael/Data/TEMP'
output_file_path = r'/media/michael/Data/TEMP/nakamura_energy.dat'
t_start = 5.1
freq_limits = [(17, 17.5)]

avg_spec_params=dict()
avg_spec_params['window']=8192
avg_spec_params['offset']=2048
avg_spec_params['med_filter']=7
avg_spec_params['marmett_filter']=7
avg_spec_params['f_min']=1
avg_spec_params['f_max']=25

signal_data = np.loadtxt(signal_file, delimiter='\t', skiprows=1)
# signal_data = signal_data[:, ::3]
signal_data[:, 0] = signal_data[:, 0] / 1000
signal_data = signal_data[signal_data[:, 0] > t_start]

frequency = 1 / (signal_data[1, 0] - signal_data[0, 0])

with open(signal_file, 'r') as handle:
    header = handle.readline()

header = header.split('\t')
header = header[1:][::3]

sensor_numbers = list()
for item in header:
    item = item[3:]
    t = item.split('_')
    number = int(t[0])
    sensor_numbers.append(number)

coords_data = dict()
with open(coords_file, 'r') as handle:
    for index, line in enumerate(handle):
        if index == 0:
            continue
        t = line.strip().split('\t')
        number = int(t[0])
        x, y = [float(q) for q in t[1:]]
        coords_data[number] = (x, y)

result = np.zeros(shape=(0, 3 + len(freq_limits)))
for index in range(len(sensor_numbers)):
    signal = signal_data[:, 1 + 3*index:1+3*(index+1)]
    x, y = coords_data[sensor_numbers[index]]
    # sp = spectrum(signal=signal, frequency=frequency)
    avg_sp=get_avg_spectrums(signals=signal, frequency=frequency,
                             avg_sp_params=avg_spec_params)
    sp=nakamura_spectrum(components_spectrum_data=avg_sp,
                         components_order='XYZ', spectrum_type='HV')
    t = [sensor_numbers[index], x, y]
    for lim in freq_limits:
        e = spectrum_energy(spectrum_data=sp, f_min=lim[0], f_max=lim[1])
        t.append(e)
    result = np.vstack((result, t))

    # sp = sp[sp[:, 0] <= 20]
    # label_value = f'Average spectrum Sensor {sensor_numbers[index]}'
    # plot_graph(x_data=sp[:, 0], y_data=sp[:, 1], label=label_value,
    #            output_folder=output_folder, output_name=label_value,
    #            x_label='Frequency', y_label='Amplitude')

header = ['Point', 'x', 'y']
for lim in freq_limits:
    p = f'E_{lim[0]}-{lim[1]}'
    header.append(p)
header = '\t'.join(header)

for i in range(len(freq_limits)):
    e=result[:,3+i]
    e=(e-np.min(e))/(np.max(e)-np.min(e))
    result[:, 3 + i] = e

np.savetxt(output_file_path, result, fmt='%f', delimiter='\t', header=header,
           comments='')
