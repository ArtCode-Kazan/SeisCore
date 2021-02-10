import os

import numpy as np

from SeisCore.Functions.Spectrum import spectrum


root_folder = '/media/michael/Data/Projects/Yamburg/2020/Modeling/ModelBuilding/Well_VSP256'
signal_file = 'Z_PV_0_selection_traces.dat'
frequency = 1000
ratio_coeff = 1e5

export_spectrum_file = 'spectrum_Z_PV_0_selection_traces.dat'
export_ratio_file = 'ratio_Z_selection_traces.dat'

input_file = os.path.join(root_folder, signal_file)
with open(input_file, 'r') as f:
    depth_header = f.readline().rstrip().split('\t')[1:]

depth_list = [int(x.split('=')[1]) for x in depth_header]

data = np.loadtxt(input_file, skiprows=1, delimiter='\t',
                  usecols=[x+1 for x in range(len(depth_list))])
data = list(zip(depth_list, (data[:, x] * ratio_coeff for x in range(len(depth_list)))))
data.sort(key=lambda x: x[0])

depth, signal = data[0]
sp_result = spectrum(signal, frequency)
header=['Frequency', f'H={depth}']
for depth, signal in data[1:]:
    sp_val = spectrum(signal, frequency)
    sp_result = np.column_stack((sp_result, sp_val[:, 1]))
    header.append(f'H={depth}')

export_file = os.path.join(root_folder, export_spectrum_file)
np.savetxt(export_file, sp_result, '%f', '\t', header='\t'.join(header),
           comments='')

layers_count = len(depth_list) - 1
result_ratio = sp_result[:, 0]
for i in range(layers_count):
    top_sp_amplitude = sp_result[:, i + 1]
    bottom_sp_amplitude = sp_result[:, i + 2]
    ratio_val = np.log(bottom_sp_amplitude/top_sp_amplitude)
    result_ratio = np.column_stack((result_ratio, ratio_val))

layer_names = [f'Layer={data[x][0]}-{data[x + 1][0]}' for x in range(
    layers_count)]
header = ['Frequency'] + layer_names

export_file = os.path.join(root_folder, export_ratio_file)
np.savetxt(export_file, result_ratio, '%f', '\t', header='\t'.join(header),
           comments='')
