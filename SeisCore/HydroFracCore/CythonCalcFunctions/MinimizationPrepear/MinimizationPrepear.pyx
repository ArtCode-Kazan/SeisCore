import numpy as np
cimport numpy as np

def minimization_prep(int minute_number,
                      double min_correlation,
                      int window_size,
                      np.ndarray[np.int_t, ndim = 1] points,
                      np.ndarray[np.float_t, ndim = 2] bin_data,
                      np.ndarray[np.int_t, ndim = 1] moments,
                      np.ndarray[np.int_t, ndim = 2] delay_data):
    """
    Функци для подготовки данных к минимизации - выделение "шестерок"
    :param  minute_number: номер минуты для обработки
    :param  min_correlation: Минимальный порог корреляции для отборки
    "шестерок"
    :param  window_size: размер окна для расчета корреляций
    :param  points: одномерный numpy-массив с номерами точек для расчетов
    :param  bin_data: буферизованные данные для текущей минуты для всех
    точек, находящихся в массиве points. Номера колонок соответсвуют
    индексам номеров точек в points
    :param  moments: одномерный массив numpy с отобранными номерами отсчетов
    текущей минуты
    :param  delay_data: двухмерный массив с информацией о задержках. Массив
    состоит из 6 столбцов:
    столбец 1 - номер первой точки пары
    столбец 2 - номер второй точки пары
    столбец 3 - минимальная задержка между точками пары
    столбец 4 - максимальная задержка между точками пары
    столбец 5 - минимальная задержка между младшей точкой и базовой точкой
    столбец 6 - максимальная задержка между младшей точкой и базовой точкой
    --------------------------------------------------------------------------
    :return: функция возвращает одномерный массив (!!!), который следует
    подвергнуть reshape, чтобы разделить его на шесть столбцов:
    столбец 1 - номер минуты обработки
    столбец 2 - номер отобранного момента минуты
    столбец 3 - номер первой точки пары
    столбец 4 - номер второй точки пары
    столбец 5 - рассчитанная задержка
    столбец 6 - расчитанная максимальная корреляция

    """
    # помоментная обработка
    cdef:
        # итерационная переменная для обхода отобранных моментов
        int moment_i
        # итерационная переменная для обхода данных по задержкам
        int delay_i
        # номер первой и второй точки пары
        int point_a_number, point_b_number
        # минимальная и максимальная задержки между точками пары
        int moment_delay_ab_min, moment_delay_ab_max
        # минимальная и максимальная задержки между младшей точкой пары и
        # базовой точкой
        int moment_delay_base_min, moment_delay_base_max
        # номер колонки, в которой находится сигнал текущей точки
        int column_number
        # извлеченный из массива bin_data сигнал для первой точки пары
        np.ndarray[np.float_t, ndim = 1] signal_a
        # извлеченный из массива bin_data сигнал для второй точки пары
        np.ndarray[np.float_t, ndim = 1] signal_b
        # рассчитанное значение модуля максимальной корреляции
        double max_correlation
        # рассчиьтанное значение задержки
        int delta_moment
        # пределы для извлечения участка сигнала первой точки пары для
        # расчета корреляции
        int t1, t2
        # итеративные переменные для расчета корреляции
        int moment_j, j,moment_k, k
        # пределы для извлечения участка сигнала второй точки пары для
        # расчета корреляции
        int t3, t4
        # размер буфера извлечения сигналов
        int buffer_size = 200
        # промежуточные переменные для расчета значений корреляций
        double sum_a, sum_b, sum_ab, sum_q_a, sum_q_b, val, corr
        # результирующий массив, который будет возвращен после работы функции
        np.ndarray[np.float_t, ndim = 1] result

    result = np.empty(shape = 0, dtype = np.float)
    # первый уровень циклов - обход по отобранным моментам
    for moment_i in range(moments.shape[0]):
        # второй уровень циклов - обход по отобранным парам
        # геометрической выборки и их задержкам
        for delay_i in range(delay_data.shape[0]):
            point_a_number = delay_data[delay_i,0]
            point_b_number = delay_data[delay_i,1]
            moment_delay_ab_min = delay_data[delay_i,2]
            moment_delay_ab_max = delay_data[delay_i,3]
            moment_delay_base_min = delay_data[delay_i,4]
            moment_delay_base_max = delay_data[delay_i,5]

            # поиск сигнала первой точки пары
            column_number = np.where((points == point_a_number))[0][0]
            signal_a = bin_data[:, column_number]

            # поиск сигнала второй точки пары
            column_number = np.where((points == point_b_number))[0][0]
            signal_b = bin_data[:, column_number]

            # начальные значения расчета корреляции и задержки
            # корреляция считается по альтернативной формуле через суммы без
            # вычисления среднего см. ссылку
            # https://myslide.ru/documents_4/fb5049f5e3104927ac47a5009bfc8cc7/img11.jpg
            max_correlation = -9999
            delta_moment = -9999

            # пределы для третьего уровня циклов
            t1 = buffer_size + moments[moment_i] + moment_delay_base_min
            t2 = buffer_size + moments[moment_i] + moment_delay_base_max

            # третий уровень циклов
            for moment_j in range(t1, t2+1, 1):
                sum_a = sum_q_a = 0
                for j in range(window_size):
                    val = signal_a[moment_j+j]
                    sum_a += val
                    sum_q_a+= val*val

                # пределы для четвертого уровня циклов
                t3 = moment_j + moment_delay_ab_min
                t4 = moment_j + moment_delay_ab_max
                for moment_k in range(t3, t4+1, 1):
                    sum_b = sum_q_b = sum_ab=0
                    for k in range(window_size):
                        val = signal_b[moment_k + k]
                        sum_b += val
                        sum_q_b += val * val
                        sum_ab += val*signal_a[moment_j+k]

                    # вычисление корреляции
                    corr = (sum_ab * window_size - sum_a * sum_b) / ((sum_q_a * window_size - sum_a ** 2) * (sum_q_b * window_size - sum_b ** 2)) ** 0.5
                    # нахождение модуля корреляции
                    if corr < 0:
                        corr = -corr
                    # определение максимального значения корреляции и
                    # задежки
                    if corr > max_correlation:
                        max_correlation=corr
                        delta_moment = moment_k - moment_j
            # добавление результата в массив, если значение корреляции выше
            # или равна минимальному заданному порогу
            if min_correlation<=max_correlation:
                result = np.append(result, [minute_number, moments[moment_i],
                                            point_a_number, point_b_number,
                                            delta_moment, max_correlation])
    return result
