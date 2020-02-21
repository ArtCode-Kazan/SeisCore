import os
import numpy as np
from datetime import datetime
from SeisCore.Functions.Spectrum import cepstral_spectrum_from_signal


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
root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling/EnergyAnalysis' \
            r'/30302/30302_matlab'
signal_frequency=250

# output_root_folder=r'/media/michael/Data/TEMP/output_data'
output_root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling' \
                   r'/EnergyAnalysis/30302/30302_matlab_output'

output_file_name='CepstralSpectrums.dat'
p_type='split'
det_type='TnWN'

points_list=os.listdir(root_folder)

result_array=None
header=['Frequency']
energy_point_file_lines=list()
point_numbers=list()
for point in points_list:
    t1 = datetime.now()
    t=point.split('_')
    point_number=int(t[1])
    point_numbers.append(point_number)
    point_folder=os.path.join(root_folder,point)
    processing_types=os.listdir(point_folder)
    for proc_type in processing_types:
        if proc_type!=p_type:
            continue
        proc_folder=os.path.join(point_folder, proc_type)
        dat_files=list()
        detrend_types=list()
        for file in os.listdir(proc_folder):
            name, extension = file.split('.')
            if extension!='dat':
                continue
            t = name.split('_')
            detrend_type=t[-1]
            if detrend_type not in detrend_types:
                detrend_types.append(detrend_type)
            dat_files.append(file)

        for detrend_type in detrend_types:
            if detrend_type!=det_type:
                continue
            files=list()
            for fn in dat_files:
                name, extension = fn.split('.')
                t = name.split('_')
                if detrend_type==t[-1]:
                    files.append(fn)
            ordered_files=[None, None, None]
            for file in files:
                name, extension = file.split('.')
                t=name.split('_')
                component=t[-2]
                index='XYZ'.index(component)
                ordered_files[index]=file

            ordered_paths=list()
            for file in ordered_files:
                if file is None:
                    ordered_files.append(file)
                    continue
                path=os.path.join(proc_folder, file)
                ordered_paths.append(path)

            signal=np.loadtxt(ordered_paths[2], delimiter=' ')[:, 1]
            cep_data=cepstral_spectrum_from_signal(
                signal=signal, frequency=signal_frequency, using_log=False,
                freq_limits=(1, 25))
            cep_data=cep_data[cep_data[:,0]>=0.5]
            cep_data[:,1]=(cep_data[:,1]-np.min(cep_data[:,1])) / \
                            (np.max(cep_data[:,1])-np.min(cep_data[:,1]))
            if result_array is None:
                result_array=cep_data
            else:
                result_array=np.column_stack((result_array, cep_data[:, 1]))
            header.append(f'Num-{point_number}')
    t2 = datetime.now()
    dt=(t2-t1).total_seconds()
    print(f'Point {point} done. Time: {dt} sec')

np.savetxt(os.path.join(output_root_folder,output_file_name), result_array,
           '%f', '\t', header='\t'.join(header), comments='')

main_group=[17, 22, 21, 20, 25, 30]
second_group=list()
for item in point_numbers:
    if item not in main_group:
        second_group.append(item)

point_groups=[main_group, second_group]

sum_curves_array=np.zeros(shape=(result_array.shape[0], len(point_groups)+1))
sum_curves_array[:,0]=result_array[:,0]
header=['Freq']
for index, group in enumerate(point_groups):
    indexes=[point_numbers.index(item)+1 for item in group]
    curve=np.median(result_array[:,indexes], axis=1)
    sum_curves_array[:, index+1]=curve
    header.append(f'Group_{index+1}')
np.savetxt(os.path.join(output_root_folder,'SumCurvesCepstral.dat'),
           sum_curves_array, '%f', '\t', header='\t'.join(header),
           comments='')

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
