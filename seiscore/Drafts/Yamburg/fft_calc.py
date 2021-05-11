import numpy as np
from numpy.fft import rfft, rfftfreq
from seiscore.functions.Spectrum import spectrum


def freqs(n,d):
    val = 1.0 / (n * d)
    N = n // 2 + 1
    res = np.arange(0, N, dtype=int)
    return res* val


def dft(x):
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-2j * np.pi * k * n / N)
    # a1 = np.cos(2*np.pi/N*1*1)
    # b1 = -np.sin(2*np.pi/N*1*1)
    res = np.dot(M, x)
    # print(k[1],n[1], N, M[1,1], a1, b1)
    return res
#
#
# file=r'/media/michael/Data/TEMP/quiet.dat'
# freq=250
# signal=np.loadtxt(file, delimiter='\t')[:20000,1]
# f=freqs(signal.shape[0], 1./freq)
#
# fft_vals=dft(signal)
# fft_vals=fft_vals[:fft_vals.shape[0]//2+1]
#
# amp=2 * abs(fft_vals) / signal.shape[0]
#
# res=np.zeros(shape=(f.shape[0], 2))
# res[:,0]=f
# res[:,1]=amp
#
# sp=spectrum(signal=signal, frequency=freq)
#
#
# #
# #
# #
# # f2=rfftfreq(1000000, 1./freq)
# pass
# # a=dft(signal)
# # print(a)
# # pass


k=0
n=6
for i in range(n):
    for j in range(i,n):
        index=int((2*n-i+1)*i/2)+j-i
        ix=int((2*n+1-((2*n+1)**2-8*index)**0.5)/2)
        jx=ix+index-int((2*n-ix+1)/2*ix)
        print(i,j, index-k, i-ix, j-jx)
        k+=1
