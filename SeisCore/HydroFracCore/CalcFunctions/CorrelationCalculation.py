import numpy as np


def calc_correlation(point_numbers, base_point_number, signals, frequency,
                     moment_window, left_buffer, moment_delays):
    """
    Функция для вычисления среднего максимального квадрата корреляции
    :param point_numbers: одномерный массив numpy номеров точек
    :param base_point_number: номер базового датчика
    :param signals: собранные в массив numpy буферизованные сигналы точек.
    Каждый столбец массива соответствует номеру точки из списка point_numbers
    :param frequency: частота записи сигнала
    :param moment_window: размер окна анализа в отсчетах
    :param left_buffer: размер левого буфера
    :param moment_delays: временные задержки точек относительно базовой точки
    в виде списка
                  (номер точки, [минимальная задержка, максимальная задержка]),
                  (point1,[min1,max1]),
                  (point2,[min2,max2]),...
    :return: одномерный список numpy со значениями корреляций
    """
    # Проверка, что базовая точка находится в массиве номеров точек
    if base_point_number not in point_numbers:
        return None

    # Проверка, что число столбцов массива с сигналами равно числу точек в
    # списке
    if point_numbers.shape[0] != signals.shape[1]:
        return None

    # поиск данных сигнала базового датчика
    column_number = np.where((point_numbers == base_point_number))[0][0]
    base_point_signal = signals[:, column_number]

    # Создание выходного массива с данными средних
    # максимальных квадратов корреляций
    result = np.empty(shape=0, dtype=float)

    # Обход производится по каждому отсчету базового датчика в течение одной
    #  минуты, начиная от начала минуты
    # НЕ ОТ СНАЧАЛА СИГНАЛА, а от начала минуты.
    # Так как извлеченный сигнал содержит буферы
    for base_moment in range(left_buffer, 60 * frequency + left_buffer):
        # сумма квадратов коэф-тов корреляции для текущего отсчета
        sum_correlation = 0
        # второй цикл идет по всем точкам из списка
        for point in point_numbers:
            # если номер точки совпал с номером базовой точки, то цикл
            # пропускает ее
            if point == base_point_number:
                continue

            # поиск задержек для текущей точки относительно базовой точки
            current_moment_delay = None
            for point_number, delay in moment_delays:
                if point_number == point:
                    current_moment_delay = delay
                    break
            if current_moment_delay is None:
                return None

            # получение максимальной и минимальной текущей задержки
            min_moment_delay = current_moment_delay[0]
            max_moment_delay = current_moment_delay[1]

            # поиск сигнала для текущей точки
            column_number = np.where((point_numbers == point))[0][0]
            current_point_signal = signals[:, column_number]

            # расчет максимальной корреляции для текущего датчика
            max_correlation = -9999
            # обход цикла идет по задержкам
            for current_delay in \
                    range(min_moment_delay, max_moment_delay + 1, 1):
                # выборка сигнала с базовой точки
                left_edge = base_moment
                right_edge = base_moment + moment_window
                signal_a = base_point_signal[left_edge:right_edge]
                # выборка сигнала с текущей точки
                signal_b = current_point_signal[left_edge + current_delay:
                                                right_edge + current_delay]
                # Вычисление корреляции
                corr = abs(np.corrcoef(signal_a, signal_b)[0, 1])
                # Отборка максимальной корреляции
                if corr > max_correlation:
                    max_correlation = corr

            # Возведение корреляции в квадрат
            max_correlation = max_correlation ** 2

            # Суммирование корреляции
            sum_correlation += max_correlation

        # Вычисление средней корреляции
        avg_correlation = sum_correlation / (len(point_numbers) - 1)
        # Добавление результата корреляции в результирующий массив
        result = np.append(result, [avg_correlation])
    return result
