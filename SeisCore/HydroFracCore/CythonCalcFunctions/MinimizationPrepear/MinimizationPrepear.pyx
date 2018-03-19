import numpy as np
cimport numpy as np

def minimization_prep(int minute_number,
                      int window_size,
                      np.ndarray[np.int_t, ndim = 1] points,
                      np.ndarray[np.float_t, ndim = 2] bin_data,
                      np.ndarray[np.int_t, ndim = 1] moments,
                      np.ndarray[np.int_t, ndim = 2] delay_data):
    # помоментная обработка
    cdef:
        int moment
        int delay_i
        int point_a_number, point_b_number
        int moment_delay_ab_min, moment_delay_ab_max
        int moment_delay_base_min, moment_delay_base_max
        int column_number
        np.ndarray[np.float_t, ndim = 1] signal_a
        np.ndarray[np.float_t, ndim = 1] signal_b
        double max_correlation
        int delta_moment
        int moment_i
        int t1, t2
        int moment_j, j
        int moment_k, k
        int t3, t4
        int buffer_size = 200
        double sum_a, sum_b, sum_ab, sum_q_a, sum_q_b, val, corr
        np.ndarray[np.float_t, ndim = 1] result

    result = np.empty(shape = 0, dtype = np.float)
    for moment_i in range(moments.shape[0]):
        # цикл по отобранным парам геометрической выборки
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

            max_correlation = -9999
            delta_moment = -9999
            t1 = buffer_size + moments[moment_i] + moment_delay_base_min
            t2 = buffer_size + moments[moment_i] + moment_delay_base_max

            for moment_j in range(t1, t2+1, 1):

                sum_a = sum_q_a = 0
                for j in range(window_size):
                    val = signal_a[moment_j+j]
                    sum_a += val
                    sum_q_a+= val*val

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
                        # определение максимального значения корреляции
                        if corr > max_correlation:
                            max_correlation=corr
                            delta_moment = moment_j - moment_i
            result = np.append(result, [minute_number, moments[moment_i],
                                        point_a_number, point_b_number,
                                        delta_moment, max_correlation])
    return result