import os
import numpy as np
from SeisCore.Functions.MarmettFilter import marmett
from SeisCore.Functions.Spectrum import spectrum

folder=r'G:\Data\2019-01-29\20190129_124505_B800'
file='20190129_124505_B800.dat'

fpath=os.path.join(folder, file)

data=np.loadtxt(fpath, dtype=np.float, delimiter='\t')

signal=data[:, 0]

sp=spectrum(signal,200)

sp[:, 1] = marmett(sp[:, 1], 7)

np.savetxt(os.path.join(folder,'filter_sp_z.dat'),sp,'%f', '\t')
