import numpy as np
cimport numpy as np

int_DTYPE = np.int
float_DTYPE = np.float

ctypedef np.int_t int_DTYPE_t
ctypedef np.float_t float_DTYPE_t

def calc_correlation(np.ndarray[int_DTYPE_t, ndim=1] point_numbers,
                     int base_point_number,
                     np.ndarray[int_DTYPE_t, ndim=2] signals,
                     int frequency,
                     int moment_window,
                     int left_buffer,
                     list moment_delays):
    # Проверка, что базовая точка находится в массиве номеров точек
    if base_point_number not in point_numbers:
        return None

    # Проверка, что число столбцов массива с сигналами равно числу точек в
    # списке

    cdef int points_count = point_numbers.shape[0]
    cdef int signals_column_count = signals.shape[1]
    if points_count != signals_column_count:
        return None

    # поиск данных сигнала базового датчика
    cdef int column_number = np.where((point_numbers == base_point_number))[0][0]
    cdef np.ndarray[int_DTYPE_t, ndim=1] base_point_signal = signals[:, column_number]

    # Создание выходного массива с данными средних
    # максимальных квадратов корреляций
    cdef np.ndarray[float_DTYPE_t, ndim=1] result = np.empty(shape=0, dtype=float_DTYPE)

    # Обход производится по каждому отсчету базового датчика в течение одной
    #  минуты, начиная от начала минуты
    # НЕ ОТ СНАЧАЛА СИГНАЛА, а от начала минуты.
    # Так как извлеченный сигнал содержит буферы
    cdef float sum_correlation
    cdef int min_moment_delay
    cdef int max_moment_delay
    cdef int i
    cdef int point_number
    cdef np.ndarray[int_DTYPE_t, ndim=1] current_point_signal
    cdef float max_correlation
    cdef int current_delay
    cdef int left_edge
    cdef int right_edge
    cdef np.ndarray[int_DTYPE_t, ndim=1] signal_a
    cdef np.ndarray[int_DTYPE_t, ndim=1] signal_b
    cdef float corr
    cdef float avg_correlation
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
            min_moment_delay = -9999
            max_moment_delay = -9999
            for i in range(moment_delays):
                point_number = moment_delays[i,0]
                if point_number ==point:
                    min_moment_delay = moment_delays[i,1][0]
                    max_moment_delay = moment_delays[i,1][1]
                    break
            for point_number, delay in moment_delays:
                if point_number == point:
                    current_moment_delay = delay
                    break

            if min_moment_delay==-9999 or max_moment_delay == -9999:
                return None

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