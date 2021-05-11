import segyio
import numpy as np
from seiscore.functions.Spectrum import spectrum


file = '/media/michael/Data/Projects/Yamburg/2020/PriorData/6_ВСП/ВСП_' \
       'Харвутинская_ПО-256/OBRAB_256/Seltr/W256sp0XYZ.sgy'
time_start_sec, time_stop_sec = 0, 5.4
frequency = 1000
depth_space = 10

export_file_path = '/media/michael/Data/Projects/Yamburg/2020/Modeling' \
                   '/ModelBuilding/Well_VSP256/Z_PV_0.dat'

duration = time_stop_sec - time_start_sec
out_data=np.linspace(time_start_sec, time_stop_sec, int(duration * frequency))
depth_list=list()
with segyio.open(file,ignore_geometry=True) as handle:
    trace_count = handle.tracecount // 3
    for i in range(trace_count):
        out_data = np.column_stack((out_data, handle.trace[2 + 3 * i]))
        depth_list.append(depth_space * (trace_count - 1 - i))

header = ['Time']+[f'H={x}' for x in depth_list]
header = '\t'.join(header)
np.savetxt(export_file_path, out_data, '%f', '\t', header=header, comments='')

#
# spectrum_data=None
# for i in range(len(depths.keys())):
#     signal=out_data[:,i+1]
#     sp_data=spectrum(signal,1000)
#     if spectrum_data is None:
#         spectrum_data=sp_data
#     else:
#         spectrum_data=np.column_stack((spectrum_data,sp_data[:,1]))
#
# spectrum_data=spectrum_data[spectrum_data[:,0]<=100]
#
# header = ['Freq'] + ['H=' + str(x) for x in depths.keys()]
# header = '\t'.join(header)
# np.savetxt(r'/home/michael/Temp/z_spectrum.dat', spectrum_data, '%f','\t',
#            header=header, comments='')
#
# min_depth=min(depths.keys())
# step_size=20
# slope_data=np.zeros(shape=(0,3))
# for i in range(len(depths.keys())-1):
#     top=min_depth+i*step_size
#     bottom=top+step_size
#     top_amplitude=spectrum_data[:,len(depths.keys())-i]
#     bottom_amplitude=spectrum_data[:,len(depths.keys())-i-1]
#
#     curve_data=np.log(top_amplitude/bottom_amplitude)
#     x_data=spectrum_data[:,0]
#     coeffs=np.polyfit(x_data,curve_data,1)
#     slope_data=np.vstack((slope_data,(top, bottom, coeffs[0])))
#
# np.savetxt(r'/home/michael/Temp/z_slope.dat', slope_data, '%f','\t',
#            header='Top\tBottom\tSlope', comments='')
# print(slope_data)