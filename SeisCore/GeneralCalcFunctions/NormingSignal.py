
"""
Модуль для проведения операции нормировки сигнала

"""

def norming_signal(signal, sensor_coefficient, registrator_coefficient):
    """
    функция для "нормализации" полного сигнала
    :param signal: сигнал с вычтенным средним значением
    :param sensor_coefficient: коэфф-т сенсора
    :param registrator_coefficient: коэф-т регистратора
    :return: нормированный сигнал
    """
    signal = signal / sensor_coefficient * registrator_coefficient
    return signal
