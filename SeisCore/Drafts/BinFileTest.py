from SeisCore.BinaryFile.BinaryFile import BinaryFile
import numpy as np
from datetime import datetime, timedelta


def sl_filter_a(signal, frequency, order=3, long_window=1.0,
                short_window=0.1):
    """
    Function for sta/lta filtration
    :param signal: one-dimension array os signal
    :param frequency: signal frequency
    :param order: filter order
    :param long_window: long window size (seconds)
    :param short_window: short window size (seconds)
    :return: filtered signal (one-dimension array)
    """
    long_window=int(frequency*long_window)
    short_window=int(frequency*short_window)

    for j in range(order):
        left_lim = j * long_window
        coeffs=np.zeros_like(signal)
        for i in range(left_lim + long_window,
                       signal.shape[0] - short_window):
            lta_window = signal[i - long_window:i]
            lta = np.mean(np.abs(lta_window))

            sta_window = signal[i-short_window:i]
            sta = np.mean(np.abs(sta_window))

            if lta == 0:
                val = 0
            else:
                val = sta / lta
            coeffs[i] = val

        coeffs = (coeffs - np.min(coeffs)) / (np.max(coeffs) - np.min(coeffs))
        signal = signal * coeffs
    return signal


def sl_filter_b(signal, frequency, order=3, long_window=1.0,
                short_window=0.1):
    """
    Function for sta/lta filtration
    :param signal: one-dimension array os signal
    :param frequency: signal frequency
    :param order: filter order
    :param long_window: long window size (seconds)
    :param short_window: short window size (seconds)
    :return: filtered signal (one-dimension array)
    """
    long_window=int(frequency*long_window)
    short_window=int(frequency*short_window)

    for j in range(order):
        left_lim = j * long_window
        coeffs=np.zeros_like(signal)
        lta_sum=0
        sta_sum=0
        for i in range(left_lim + long_window,
                       signal.shape[0] - short_window):
            lta_window = signal[i - long_window:i]
            sta_window = signal[i - short_window:i]
            if i==0:
                lta_sum=np.sum(np.abs(lta_window))
                sta_sum=np.sum(np.abs(sta_window))
            else:
                lta_sum = lta_sum-np.abs(signal[i - long_window-1]) + \
                        np.abs(lta_window[i-1])
                sta_sum = sta_sum-np.abs(signal[i - short_window-1]) + \
                        np.abs(signal[i-1])

            lta = lta_sum/long_window
            sta = sta_sum/short_window

            if lta == 0:
                val = 0
            else:
                val = sta / lta
            coeffs[i] = val

        coeffs = (coeffs - np.min(coeffs)) / (np.max(coeffs) - np.min(coeffs))
        signal = signal * coeffs
    return signal


def check_function(signal, frequency, order=3, long_window=1.0,
                   short_window=0.1):
    #signal=np.abs(signal)

    long_window = int(frequency * long_window)
    short_window = int(frequency * short_window)

    for j in range(order):
        left_lim = (j+1) * long_window
        lta_sum_b = 0
        sta_sum_b = 0
        for i in range(left_lim, signal.shape[0]):
            lta_window = signal[i - long_window:i]
            sta_window = signal[i - short_window:i]
            if i == left_lim:
                lta_sum_b = np.sum(np.abs(lta_window))
                sta_sum_b = np.sum(np.abs(sta_window))
                print('equal')
            else:
                lta_sum_b = lta_sum_b - np.abs(signal[i - long_window - 1])\
                            + np.abs(signal[i - 1])
                sta_sum_b = sta_sum_b - np.abs(signal[i - short_window - 1])\
                            + np.abs(signal[i - 1])

            lta_sum_a = np.sum(np.abs(lta_window))
            sta_sum_a = np.sum(np.abs(sta_window))

            if lta_sum_a!=lta_sum_b:
                print('Error lta')

            if sta_sum_a!=sta_sum_b:
                print('Error sta')


            # lta_b = lta_sum_b / long_window
            # sta_b = sta_sum_b / short_window
            #
            # lta_a = np.mean(np.abs(lta_window))
            # sta_a = np.mean(np.abs(sta_window))
            # print('DOne')


bin_data=BinaryFile()
bin_data.path='/media/michael/Data/Projects/GRP/DemkinskoeDeposit' \
              '/Demkinskoe_4771/Binary/HF_0001_2019-07-28_07-40-24_065_127.xx'
bin_data.record_type='ZXY'

bin_data.read_date_time_start=datetime(2019,7,28,8,0,0)+timedelta(
    seconds=-1*3)
bin_data.read_date_time_stop=datetime(2019,7,28,8,0,2)

print(bin_data.discrete_amount)
print((bin_data.signals.shape))
exit(0)


bin_data.read_date_time_start=datetime(2019,7,28,8,0,0)+timedelta(
    seconds=-1*3)
bin_data.read_date_time_stop=datetime(2019,7,28,8,0,2)

signal=bin_data.signals[:,0]

check_function(signal=signal, frequency=1000, order=3, long_window=0.5,
               short_window=0.05)

# sfa=sl_filter_a(signal,100,1,1,0.05)
# sfb=sl_filter_b(signal,100,1,1,0.05)
#
# print(np.max(np.abs(sfa-sfb)))
#
#
# print(bin_data.datetime_start, bin_data.datetime_stop)
# print(bin_data.longitude, bin_data.latitude)
# print(bin_data.signals.shape)
#
#

# bin_data.data_type='HydroFrac'
# bin_data.resample_frequency=250
# bin_data.use_avg_values=True
# signal=bin_data.signals
# print(signal[:20,2])
# print('Ok')