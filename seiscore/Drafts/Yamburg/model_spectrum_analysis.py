import os
import numpy as np
from datetime import datetime
from seiscore.functions.Spectrum import average_spectrum
from seiscore.functions.Energy import spectrum_energy
from seiscore.functions.Spectrum import nakamura_spectrum


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


def join(intervals):
    """
    Метод для объединения интервалов
    :param intervals: список из кортежей интервалов (все интервалы ЗАКРЫТЫЕ!!!)
    :return: список из объединенных интервалов и его длины
    """
    # сортировка списка по левым границам интервалов по возрастанию
    intervals.sort(key=lambda x: x[0])
    while True:
        start_length = len(intervals)
        for index, value in enumerate(intervals):
            if index != len(intervals) - 1:
                a, b = intervals[index]
                c, d = intervals[index + 1]
                # максимальное расстояние между интервалами - 1 дискрета
                if c - b <= 1:
                    intervals[index] = (min(a, c), max(b, d))
                    del intervals[index + 1]
        end_length = len(intervals)
        # проверка изменился ли список с последней итерации объединения
        # если объединений не было, прерывание цикла объединения
        if start_length == end_length:
            break
    # подсчет суммарной длины объединенных интервалов
    sum_length = 0
    for a, b in intervals:
        sum_length += b-a+1
    return intervals


# root_folder=r'/media/michael/Data/TEMP/input_data'
root_folder=r'/media/michael/Data/TEMP'
# output_root_folder=r'/media/michael/Data/TEMP/output_data'
output_root_folder=r'/media/michael/Data/TEMP'
signal_file=r'/media/michael/Data/TEMP/signal_test.dat'
output_file_name='NakamuraSpectrums.dat'
t_start=10

avg_spec_params=dict()
avg_spec_params['window']=8192
avg_spec_params['offset']=2048
avg_spec_params['med_filter']=7
avg_spec_params['marmett_filter']=7


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

result_array=None
for index, point in enumerate(sensor_numbers):
    sp_data=get_avg_spectrums(signals=signal_data[:,1+3*index:1+3*(index+1)],
                              frequency=frequency, avg_sp_params=avg_spec_params)

    z_spectrum = nakamura_spectrum(
        components_spectrum_data=sp_data,
        components_order='XYZ', spectrum_type='HV')

    # z_spectrum=z_spectrum[(z_spectrum[:,0]>=5)*(z_spectrum[:,0]<=25)]
    z_spectrum[:,1]=(z_spectrum[:,1]-np.min(z_spectrum[:,1])) / \
                    (np.max(z_spectrum[:,1])-np.min(z_spectrum[:,1]))
    if result_array is None:
        result_array=z_spectrum
    else:
        result_array=np.column_stack((result_array, z_spectrum[:, 1]))
    header.append(f'Num-{point}')
    t2 = datetime.now()

np.savetxt(os.path.join(output_root_folder,output_file_name), result_array,
           '%f', '\t', header='\t'.join(header), comments='')

main_group=[17, 22, 21, 20, 25, 30,209,207,208,229,230,228,253,252,187,188,
            271,272]
second_group=list()
for item in sensor_numbers:
    if item not in main_group:
        second_group.append(item)

point_groups=[main_group, second_group]

sum_curves_array=np.zeros(shape=(result_array.shape[0], len(point_groups)+1))
sum_curves_array[:,0]=result_array[:,0]
header=['Freq']
for index, group in enumerate(point_groups):
    indexes=[sensor_numbers.index(item)+1 for item in group]
    curve=np.median(result_array[:,indexes], axis=1)
    sum_curves_array[:, index+1]=curve
    header.append(f'Group_{index+1}')
np.savetxt(os.path.join(output_root_folder,'SumCurves.dat'), sum_curves_array,
           '%f', '\t', header='\t'.join(header), comments='')

parametric_array=np.zeros(shape=sum_curves_array.shape[0])
for index,item in enumerate(sum_curves_array):
    ratio=item[1]/item[2]
    if ratio>=2:
        parametric_array[index]=1

intervals=list()
for index in range(sum_curves_array.shape[0]-1):
    left=parametric_array[index]
    right=parametric_array[index+1]
    if left==1 and right==1:
        intervals.append([sum_curves_array[index,0],
                          sum_curves_array[index+1,0]])

join_intervals=join(intervals)
print(join_intervals)
pass









