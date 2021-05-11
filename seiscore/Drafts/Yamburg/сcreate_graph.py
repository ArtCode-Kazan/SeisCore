import os
from datetime import datetime

import matplotlib.pyplot as plt

from seiscore import BinaryFile

from seiscore.functions.Filter import band_pass_filter
from seiscore.functions.Wavelet import detrend


folder='/media/michael/Data/TEMP/YamburgSIgnalAnalysis'
file='HF_0011_2019-12-14_06-25-59_K41_K41.00'
bin_data=BinaryFile()
bin_data.path=os.path.join(folder, file)
bin_data.read_date_time_start=datetime(2019,12,14,10)
bin_data.read_date_time_stop=datetime(2019,12,14,11)
bin_data.use_avg_values=True

z_signal=bin_data.signals[:,0]

filtered_signal=band_pass_filter(z_signal.copy(), bin_data.resample_frequency,
                                 1, 500)

detrend_signal=detrend(z_signal.copy(), bin_data.resample_frequency,10)

fig, axes = plt.subplots(3, 1)
axes[0].plot(z_signal)
axes[1].plot(filtered_signal)
axes[2].plot(detrend_signal)
plt.show()
