from seiscore import BinaryFile
from seiscore.binaryfile.resampling.wrap import resampling


path = '/media/michael/Data/TEMP/ReviseData/90021_2020-12-14_11-54-00.00'
b = BinaryFile(path, use_avg_values=True)
print(b.short_file_info)
print(b.short_file_info.formatted_duration)
z1 = b.read_signal('Z')

b.resample_frequency = 250
z2 = b.read_signal('Z')
pass