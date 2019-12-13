import os
from datetime import timedelta

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.Functions.Spectrum import average_spectrum
from SeisCore.Plotting.Plotting import plot_average_spectrum


root_folder=r'/media/michael/Seagate Backup Plus Drive/DemkinskoeDeposit/Demkinskoe_4771/Binary'
export_folder=r'/media/michael/Seagate Backup Plus Drive/DemkinskoeDeposit/Demkinskoe_4771/Binary'
window_size=8192
overlap_size=4093
median_param=7
marmett_param=7
time_step_minutes=60
components=['X','Y','Z']
f_min=1
f_max=10


# ----------------------- Don't touch ---------------------------------------
for root, folders, files in os.walk(root_folder):
    for file in files:
        name, extension=file.split('.')
        if extension not in ['00','xx','bin']:
            continue

        bin_data=BinaryFile()
        bin_data.path=os.path.join(root, file)
        bin_data.use_avg_values=False
        i=0
        while True:
            left_time_lim=bin_data.datetime_start+timedelta(minutes=i*time_step_minutes)
            if left_time_lim>bin_data.datetime_stop:
                break
            right_time_lim = bin_data.datetime_start + timedelta(minutes=(i+1) * time_step_minutes)
            if right_time_lim>bin_data.datetime_stop:
                right_time_lim=bin_data.datetime_stop

            bin_data.read_date_time_start=left_time_lim
            bin_data.read_date_time_stop=right_time_lim

            signal_data=bin_data.ordered_signal_by_components
            for component in components:
                signal=signal_data[:, 'XYZ'.index(component)]
                smooth_av_spec=average_spectrum(signal=signal,
                                         frequency=bin_data.signal_frequency,
                                         window=window_size,
                                         overlap=overlap_size,
                                         med_filter=median_param,
                                         marmett_filter=marmett_param)
                no_smooth_av_spectrum=average_spectrum(signal=signal,
                                         frequency=bin_data.signal_frequency,
                                         window=window_size,
                                         overlap=overlap_size,
                                         med_filter=None, marmett_filter=None)

                exp_folder=os.path.join(export_folder, name,
                                        f'{component}-Component')
                date_fmt='%Y-%m-%d-%H-%M-%S'
                export_name=f'{name}-{left_time_lim.strftime(date_fmt)}'

                if not os.path.exists(exp_folder):
                    os.makedirs(exp_folder)
                plot_average_spectrum(frequency=smooth_av_spec[:,0],
                                      spectrum_begin_amplitudes=no_smooth_av_spectrum[:,1],
                                      spectrum_smooth_amplitudes=smooth_av_spec[:,1],
                                      f_min=f_min, f_max=f_max,
                                      output_folder=exp_folder,
                                      output_name=export_name)

            i += 1
        print(f'File {file} done ')
