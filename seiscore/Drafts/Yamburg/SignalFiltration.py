import os
from datetime import datetime

import numpy as np

import matplotlib.pyplot as plt

from seiscore import BinaryFile

from seiscore.functions.Filter import band_pass_filter
from seiscore.functions.Wavelet import detrend
from seiscore.functions.Spectrogram import create_spectrogram


a=np.random.randint(-1000, 1000, 1000)
fig, axes = plt.subplots(1, 1)
axes.plot(a)
plt.show()

folder='/media/michael/Data/TEMP/YamburgSIgnalAnalysis'
file='HF_0011_2019-12-14_06-25-59_K41_K41.00'
bin_data=BinaryFile()
bin_data.path=os.path.join(folder, file)
bin_data.read_date_time_start=datetime(2019,12,14,10)
bin_data.read_date_time_stop=datetime(2019,12,14,11)

z_signal=bin_data.signals[:,0]
create_spectrogram(z_signal, bin_data.resample_frequency, folder,
                   'origin_signal',0,50)

# filtered_signal=band_pass_filter(z_signal, bin_data.resample_frequency,
#                                  1, 500)
# filtered_signal=detrend(z_signal, bin_data.resample_frequency, 5)
filtered_signal=band_pass_filter(z_signal, bin_data.resample_frequency,
                                 1, 500)

create_spectrogram(filtered_signal, bin_data.resample_frequency, folder,
                   'filtered',0,50)

fig, axes = plt.subplots(2, 1)
axes[0].plot(z_signal)
axes[1].plot(filtered_signal)
plt.show()
plt.savefig(os.path.join(folder,'graph.png'), dpi=96)
