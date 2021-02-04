import segyio
import numpy as np
from SeisCore.Functions.Spectrum import spectrum


file=r'/media/michael/Data/Projects/Yamburg/2020/PriorData/6_ВСП/ВСП_Ямбургская_ПО-502/Матер., резул/yamb502_1_z_VPI.sgy'
depths=dict()

out_data=np.zeros(shape=(6000, 1))
out_data=np.linspace(0, 6, 6000)
depth=list()
j=0
with segyio.open(file,ignore_geometry = True) as handle:
    trace_count = handle.tracecount
    for i in range(trace_count):
        trace_header=handle.header[i]
        source_x=trace_header[segyio.TraceField.SourceX]
        if source_x not in depths:
            depths[source_x]=1
        else:
            depths[source_x]+=1

        if depths[source_x]==1:
            out_data = np.column_stack((out_data, handle.trace[i]))

header = ['Time']+['H='+str(x) for x in depths.keys()]
header = '\t'.join(header)
np.savetxt(r'/home/michael/Temp/z_traces.dat', out_data, '%f','\t',
           header=header, comments='')

spectrum_data=None
for i in range(len(depths.keys())):
    signal=out_data[:,i+1]
    sp_data=spectrum(signal,1000)
    if spectrum_data is None:
        spectrum_data=sp_data
    else:
        spectrum_data=np.column_stack((spectrum_data,sp_data[:,1]))

spectrum_data=spectrum_data[spectrum_data[:,0]<=100]

header = ['Freq'] + ['H=' + str(x) for x in depths.keys()]
header = '\t'.join(header)
np.savetxt(r'/home/michael/Temp/z_spectrum.dat', spectrum_data, '%f','\t',
           header=header, comments='')

min_depth=min(depths.keys())
step_size=20
slope_data=np.zeros(shape=(0,3))
for i in range(len(depths.keys())-1):
    top=min_depth+i*step_size
    bottom=top+step_size
    top_amplitude=spectrum_data[:,len(depths.keys())-i]
    bottom_amplitude=spectrum_data[:,len(depths.keys())-i-1]

    curve_data=np.log(top_amplitude/bottom_amplitude)
    x_data=spectrum_data[:,0]
    coeffs=np.polyfit(x_data,curve_data,1)
    slope_data=np.vstack((slope_data,(top, bottom, coeffs[0])))

np.savetxt(r'/home/michael/Temp/z_slope.dat', slope_data, '%f','\t',
           header='Top\tBottom\tSlope', comments='')
print(slope_data)