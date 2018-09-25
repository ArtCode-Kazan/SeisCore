from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.GeneralCalcFunctions.Spectrogram import create_spectrogram
import numpy as np

f = BinaryFile()
f.path = r'D:\AppsBuilding\TestingData\VariationTesting\VR_2018-07-01_066_135.xx'
f.record_type = 'ZXY'
f.resample_frequency = 250
f.start_moment=0
f.end_moment=3600*f.signal_frequency

q=f.signals
print(f.discrete_amount,f.signal_frequency)

create_spectrogram(signal_data=q[:,0],frequency=f.resample_frequency,
                   output_folder='d:/temp',output_name='fast4',
                   min_frequency=0,
                   max_frequency=1000,time_start=100)