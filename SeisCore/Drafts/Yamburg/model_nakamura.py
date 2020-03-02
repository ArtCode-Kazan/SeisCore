import os
import numpy as np

from SeisCore.Functions.Spectrum import spectrum
from SeisCore.Functions.Spectrum import nakamura_spectrum


root_folder= r'/media/michael/Data/Projects/Yamburg/Modeling/ModelPreparing/Well_30302'
model_files = [
    ('niokom', 'Niokom_anomaly.dat'),
    ('senoman', 'Senoman_anomaly.dat'),
    ('quarter', 'Q_anomaly.dat'),
    ('empty', 'source_meander_1Hz_h=3900_Bottom_Kp=0.dat')
]
t_min = 8

join_signals=None
for item in model_files:
    alias, f_name = item
    path=os.path.join(root_folder, f_name)
    data=np.loadtxt(path, delimiter='\t', skiprows=1)
    if join_signals is None:
        join_signals=data
    else:
        join_signals=np.column_stack((join_signals, data[:,1:]))

join_signals[:,0]=join_signals[:,0]/1000
join_signals=join_signals[join_signals[:,0]>=t_min]

freq=1/(join_signals[1,0]-join_signals[0,0])

nakamura_data=None
header=['Freq']
for index, item in enumerate(model_files):
    alias, _ = item
    sig=join_signals[:,1+3*index:4+3*index]
    sp_x=spectrum(signal=sig[:, 0], frequency=freq)
    sp_y=spectrum(signal=sig[:, 1], frequency=freq)
    sp_z=spectrum(signal=sig[:, 2], frequency=freq)

    join_sp=np.zeros(shape=(sp_x.shape[0], 4))
    join_sp[:,:2]=sp_x
    join_sp[:,2]=sp_y[:,1]
    join_sp[:,3]=sp_z[:,1]

    nak_sp=nakamura_spectrum(components_spectrum_data=join_sp,
                             components_order='XYZ', spectrum_type='VH')
    if nakamura_data is None:
        nakamura_data=nak_sp
    else:
        nakamura_data = np.column_stack((nakamura_data, nak_sp[:,1]))
    header.append(alias)
np.savetxt(os.path.join(root_folder,'ModelNacamura.dat'), nakamura_data,
           delimiter='\t', header='\t'.join(header), comments='')
