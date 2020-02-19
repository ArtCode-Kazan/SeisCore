import os
import numpy as np
from datetime import datetime
from SeisCore.Functions.Spectrum import average_spectrum
from SeisCore.Functions.Energy import spectrum_energy


def get_avg_spectrums(files_list, frequency, avg_sp_params):
    signals = None
    for path in files_list:
        signal = np.loadtxt(path, delimiter=' ')[:, 1]
        if signals is None:
            signals = signal
        else:
            signals = np.column_stack((signals, signal))

    smooth_avg_specs = None
    for index in range(signals.shape[1]):
        s_avg_spec = average_spectrum(signal=signals[:, index],
                                      frequency=frequency,
                                      window=avg_sp_params['window'],
                                      offset=avg_sp_params['offset'],
                                      med_filter=avg_sp_params['med_filter'],
                                      marmett_filter=avg_sp_params[
                                          'marmett_filter'])
        if smooth_avg_specs is None:
            smooth_avg_specs=s_avg_spec
        else:
            smooth_avg_specs=np.column_stack(
                (smooth_avg_specs, s_avg_spec[:,1]))
    return smooth_avg_specs


def get_energy(avg_spectrum_data, f_min, f_max):
    z_energy = spectrum_energy(spectrum_data=avg_spectrum_data[:, [0, 3]],
                               f_min=f_min, f_max=f_max)
    return z_energy


# root_folder=r'/media/michael/Data/TEMP/input_data'
root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling/EnergyAnalysis' \
            r'/30302/30302_matlab'
signal_frequency=250

# coord file
coords_file=r'/media/michael/Data/Projects/Yamburg/Modeling/EnergyAnalysis' \
            r'/30302/30302_PointsCoords.dat'

# output_root_folder=r'/media/michael/Data/TEMP/output_data'
output_root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling' \
                   r'/EnergyAnalysis/30302/30302_matlab_output'

output_file_name='Energy_data_2-3&3-4&18.3-19.4Hz.dat'

avg_spec_params=dict()
avg_spec_params['window']=8192
avg_spec_params['offset']=2048
avg_spec_params['med_filter']=7
avg_spec_params['marmett_filter']=7
avg_spec_params['f_min']=1
avg_spec_params['f_max']=25

energy_params=dict()
# energy_params['f_intervals']=[[i*0.5, (i+1)*0.5] for i in range(50)]
energy_params['f_intervals']=[[2,3], [3,4], [18.3,19.4]]

coords_data=dict()
with open(coords_file,'r') as handle:
    for index, line in enumerate(handle):
        if index==0:
            continue
        t=line.strip().split('\t')
        number=int(t[0])
        x,y=[float(q) for q in t[1:]]
        coords_data[number] = (x, y)

points_list=os.listdir(root_folder)
energy_point_file_lines=list()
for point in points_list:
    t1 = datetime.now()
    t=point.split('_')
    point_number=int(t[1])
    point_date=t[3]
    point_coords=coords_data[point_number]
    point_folder=os.path.join(root_folder,point)
    processing_types=os.listdir(point_folder)
    for proc_type in processing_types:
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

            spectrum_data=get_avg_spectrums(files_list=ordered_paths,
                                            frequency=signal_frequency,
                                            avg_sp_params=avg_spec_params)

            for interval in energy_params['f_intervals']:
                f_min, f_max = interval
                z_energy=get_energy(avg_spectrum_data=spectrum_data,
                                    f_min=f_min, f_max=f_max)
                interval = str(f_min)+'-'+str(f_max)
                t = [point_number, point_coords[0], point_coords[1],
                     interval, point_date, proc_type, detrend_type, z_energy]
                t=[str(q) for q in t]
                line='\t'.join(t)+'\n'
                energy_point_file_lines.append(line)

    t2 = datetime.now()
    dt=(t2-t1).total_seconds()
    print(f'Point {point} done. Time: {dt} sec')

with open(os.path.join(output_root_folder,output_file_name),
          'w') as handle:
    header=['Point', 'x', 'y', 'Interval', 'Date', 'Proc', 'Type', 'Energy']
    header='\t'.join(header)+'\n'
    handle.write(header)
    for line in energy_point_file_lines:
        handle.write(line)
