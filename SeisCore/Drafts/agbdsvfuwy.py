import os
import numpy as np

from SeisCore import BinaryFile


folder='/media/michael/Data/TEMP/files'
file='HF_0013_2020-08-03_00-00-00_K07.xx'
out_name='HF_0013_2020-08-03_00-00-00_K07_modified.xx'

bin_data=BinaryFile()
bin_data.path=os.path.join(folder,file)
bin_data.resample_frequency=1000
bin_data.use_avg_values=False

with open(os.path.join(folder, out_name), 'wb') as f:
    header=bin_data.main_header
    header.dt=0.001
    f.write(header.get_binary_format())
    bin_data.signals.astype(np.int32).tofile(f)
