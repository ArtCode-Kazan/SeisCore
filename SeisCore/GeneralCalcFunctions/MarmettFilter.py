

def marmett(signal, order):
    """
    функция фильтра marmett
    :param signal: входной сигнал
    :param order: порядок фильтра
    :return: отфильтрованный сигнал (длина сигнала равна исходному)
    """
    for i in range(order):
        j = 1
        recalc = signal.copy()
        while j < signal.shape[0] - 1:
            recalc[j] = (signal[j - 1] + signal[j + 1]) / 4 + signal[j] / 2
            j += 1
        recalc[0] = (signal[0] + signal[1]) / 2
        recalc[-1] = (signal[-1] + signal[-2]) / 2
        signal = recalc.copy()
    return signal