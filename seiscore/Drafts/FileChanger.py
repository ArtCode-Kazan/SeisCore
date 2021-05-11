import os
import numpy as np

from seiscore.binaryfile.BinaryFile import BinaryFile


files=os.listdir('/media/michael/Transcend/1')

export_folder='/media/michael/Data/TEMP'
for file in files:
    if file in os.listdir(export_folder):
        continue
    path=os.path.join('/media/michael/Transcend/1',file)
    bin_data=BinaryFile()
    bin_data.path=path
    signals=bin_data.signals

    main_header=bin_data.main_header
    bin_main_h=main_header.get_binary_format()

    ch_header = [bin_data.get_channel_header(channel_index=0),
                 bin_data.get_channel_header(channel_index=1),
                 bin_data.get_channel_header(channel_index=2)]

    bin_channels = [x.get_binary_format() for x in ch_header]

    export_path=os.path.join(export_folder,file)
    with open(export_path, 'wb') as handle:
        handle.write(bin_main_h)
        handle.write(bin_channels[0])
        handle.write(bin_channels[1])
        handle.write(bin_channels[2])
        signals.astype(np.int32).tofile(handle)
    print(f'File {file} done')
