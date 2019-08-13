import os
import numpy as np

from SeisCore.MSICore.CalcFunctions.Wavelett import detrend
from SeisCore.BinaryFile.BinaryFile import BinaryFile

folder='/media/michael/Садыков_РР/mihael'

for root, folders, files in os.walk(folder):
    for file in files:
        name, extension = file.split('.')
        if extension not in ('00', 'xx'):
            continue
        print(name)
        bin_data=BinaryFile()
        bin_data.path=os.path.join(root,file)
        bin_data.record_type='ZXY'
        signals=bin_data.ordered_signal_by_components

        main_header=bin_data.main_header
        channel_header_a = bin_data.get_channel_header(channel_index=0)
        channel_header_b = bin_data.get_channel_header(channel_index=1)
        channel_header_c = bin_data.get_channel_header(channel_index=2)

        for i in range(3):
            detrend_signal=detrend(signal=signals[:, i],
                                  frequency=bin_data.signal_frequency,
                                  edge_frequency=2)
            signals[:, i]=detrend_signal[:signals[:, i].shape[0]]

        output_file_path=os.path.join(root,name+'_detrend.'+bin_data.extension)
        output_file=open(output_file_path,'wb')
        output_file.write(main_header.get_binary_format())
        output_file.write(channel_header_a.get_binary_format())
        output_file.write(channel_header_b.get_binary_format())
        output_file.write(channel_header_c.get_binary_format())
        signals.astype(np.int32).tofile(output_file_path)

        print(f'file {name} done')


