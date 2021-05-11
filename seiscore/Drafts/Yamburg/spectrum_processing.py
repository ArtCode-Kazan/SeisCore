import os
import numpy as np
from datetime import datetime
from seiscore.functions.Spectrum import average_spectrum
from seiscore.functions.Spectrum import cepstral_spectrum_from_spectrum
from seiscore.functions.Spectrum import nakamura_spectrum

from seiscore.plotting.Plotting import plot_average_spectrum


def proc_file(src_file_name, detrend_type, proc_type,
              files_list, frequency,
              avg_sp_params, cepster_params, nak_sp_params,
              output_path):
    # print(f'Processing: {src_file_name}')
    signals=None
    for path in files_list:
        signal = np.loadtxt(path, delimiter=' ')[:,1]
        if str(np.max(signal))=='nan':
            print('Bad signal')
            return

        if signals is None:
            signals = signal
        else:
            signals=np.column_stack((signals, signal))

    no_smooth_avg_specs=None
    smooth_avg_specs=None
    for index in range(signals.shape[1]):
        ns_avg_spec = average_spectrum(signal=signals[:, index],
                                       frequency=frequency,
                                       window=avg_sp_params['window'],
                                       offset=avg_sp_params['offset'],
                                       median_filter=None,
                                       marmett_filter=None)
        s_avg_spec=average_spectrum(signal=signals[:, index],
                                    frequency=frequency,
                                    window=avg_sp_params['window'],
                                    offset=avg_sp_params['offset'],
                                    median_filter=avg_sp_params['med_filter'],
                                    marmett_filter=avg_sp_params['marmett_filter'])
        if no_smooth_avg_specs is None:
            no_smooth_avg_specs=ns_avg_spec
            smooth_avg_specs=s_avg_spec
        else:
            no_smooth_avg_specs=np.column_stack(
                (no_smooth_avg_specs, ns_avg_spec[:,1]))
            smooth_avg_specs=np.column_stack(
                (smooth_avg_specs, s_avg_spec[:,1]))

    smooth_cep_specs=None
    no_smooth_cep_specs=None
    for i in range(signals.shape[1]):
        spectrum=np.zeros(shape=(no_smooth_avg_specs.shape[0],2))
        spectrum[:,0]=no_smooth_avg_specs[:,0]
        spectrum[:,1] = no_smooth_avg_specs[:, i+1]
        ns_cep_spec = cepstral_spectrum_from_spectrum(spectrum_data=spectrum)
        spectrum[:, 1] = smooth_avg_specs[:, i + 1]
        s_cep_spec = cepstral_spectrum_from_spectrum(spectrum_data=spectrum)
        if smooth_cep_specs is None:
            smooth_cep_specs=s_cep_spec
            no_smooth_cep_specs=ns_cep_spec
        else:
            smooth_cep_specs = np.column_stack(
                (smooth_cep_specs, s_cep_spec[:,1]))
            no_smooth_cep_specs = np.column_stack(
                (no_smooth_cep_specs, ns_cep_spec[:,1]))

    no_smooth_nak_spec=nakamura_spectrum(
        components_spectrum_data=no_smooth_avg_specs,
        components_order='XYZ', spectrum_type=nak_sp_params['type'])

    smooth_nak_spec = nakamura_spectrum(
        components_spectrum_data=smooth_avg_specs,
        components_order='XYZ', spectrum_type=nak_sp_params['type'])

    # export data
    out_folder=os.path.join(output_path, 'AverageSpectrums',
                            proc_type, detrend_type)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    file_name=f'{src_file_name}.sc'
    out_path=os.path.join(out_folder, file_name)
    np.savetxt(out_path,no_smooth_avg_specs, delimiter='\t',
               header='Frequency\tX\tY\tZ', comments='')

    file_name = f'{src_file_name}.ssc'
    out_path = os.path.join(out_folder, file_name)
    np.savetxt(out_path, smooth_avg_specs, delimiter='\t',
               header='Frequency\tX\tY\tZ', comments='')

    for index, component in enumerate('XYZ'):
        plot_average_spectrum(
            frequency=smooth_avg_specs[:,0],
            spectrum_begin_amplitudes=no_smooth_avg_specs[:,index+1],
            spectrum_smooth_amplitudes=smooth_avg_specs[:, index+1],
            f_min=avg_sp_params['f_min'],
            f_max=avg_sp_params['f_max'],
            output_folder=out_folder,
            output_name=f'{src_file_name}_Component_{component}')

    out_folder = os.path.join(output_path, 'CepsterSpectrums',
                              proc_type, detrend_type)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    file_name = f'{src_file_name}.cep'
    out_path = os.path.join(out_folder, file_name)
    np.savetxt(out_path, no_smooth_cep_specs, delimiter='\t',
               header='Time\tX\tY\tZ', comments='')

    file_name = f'{src_file_name}.scep'
    out_path = os.path.join(out_folder, file_name)
    np.savetxt(out_path, smooth_cep_specs, delimiter='\t',
               header='Time\tX\tY\tZ', comments='')

    for index, component in enumerate('XYZ'):
        plot_average_spectrum(
            frequency=smooth_cep_specs[:,0],
            spectrum_begin_amplitudes=no_smooth_cep_specs[:,index+1],
            spectrum_smooth_amplitudes=smooth_cep_specs[:, index+1],
            f_min=cepster_params['t_min'],
            f_max=cepster_params['t_max'],
            output_folder=out_folder,
            output_name=f'Cepster_{src_file_name}_Component_{component}')

    out_folder = os.path.join(output_path, 'NakamuraSpectrum',
                              proc_type, detrend_type)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    file_name = f'{nak_sp_params["type"]}_{src_file_name}.nak'
    out_path = os.path.join(out_folder, file_name)
    np.savetxt(out_path, no_smooth_nak_spec, delimiter='\t',
               header='Freq\tAmplitude', comments='')

    file_name = f'{nak_sp_params["type"]}_{src_file_name}.snak'
    out_path = os.path.join(out_folder, file_name)
    np.savetxt(out_path, smooth_nak_spec, delimiter='\t',
               header='Freq\tAmplitude', comments='')

    plot_average_spectrum(
        frequency=smooth_nak_spec[:,0],
        spectrum_begin_amplitudes=no_smooth_nak_spec[:,1],
        spectrum_smooth_amplitudes=smooth_nak_spec[:, 1],
        f_min=nak_sp_params['f_min'],
        f_max=nak_sp_params['f_max'],
        output_folder=out_folder,
        output_name=f'{nak_sp_params["type"]}_{src_file_name}')


# root_folder=r'/media/michael/Data/TEMP/input_data'
root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling/EnergyAnalysis' \
            r'/1056/1056_matlab'
signal_frequency=250

# output_root_folder=r'/media/michael/Data/TEMP/output_data'
output_root_folder=r'/media/michael/Data/Projects/Yamburg/Modeling' \
                   r'/EnergyAnalysis/1056/1056_matlab_output'

avg_spec_params=dict()
avg_spec_params['window']=8192
avg_spec_params['offset']=2048
avg_spec_params['med_filter']=7
avg_spec_params['marmett_filter']=7
avg_spec_params['f_min']=1
avg_spec_params['f_max']=25

cepster_params=dict()
cepster_params['t_min']=0.2
cepster_params['t_max']=3

nak_sp_params=dict()
nak_sp_params['type']='HV'
nak_sp_params['f_min']=1
nak_sp_params['f_max']=None

points_list=os.listdir(root_folder)
for point in points_list:
    t1 = datetime.now()
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

            proc_file(src_file_name=point, detrend_type=detrend_type,
                      proc_type=proc_type,
                      files_list=ordered_paths,
                      frequency=signal_frequency,
                      avg_sp_params=avg_spec_params,
                      cepster_params=cepster_params,
                      nak_sp_params=nak_sp_params,
                      output_path=output_root_folder)

    t2 = datetime.now()
    dt=(t2-t1).total_seconds()
    print(f'Point {point} done. Time: {dt} sec')
