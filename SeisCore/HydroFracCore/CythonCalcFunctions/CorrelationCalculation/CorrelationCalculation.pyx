import numpy as np
cimport numpy as np

def calc_correlation(np.ndarray[np.int_t, ndim=1] point_numbers,
                     int base_point_number,
                     np.ndarray[np.float_t, ndim=2] signals,
                     int frequency,
                     int moment_window,
                     int left_buffer,
                     list moment_delays):
    # Функция для вычисления среднего максимального квадрата корреляции
    #:param point_numbers: одномерный массив numpy номеров точек
    #:param base_point_number: номер базового датчика
    #:param signals: собранные в массив numpy буферизованные сигналы точек.
    # Каждый столбец массива соответствует номеру точки из списка point_numbers
    #:param frequency: частота записи сигнала
    #:param moment_window: размер окна анализа в отсчетах
    #:param left_buffer: размер левого буфера
    #:param moment_delays: временные задержки точек относительно базовой точки
    #в виде списка
    #              (номер точки, [минимальная задержка, максимальная задержка])
    #,
    #              (point1,[min1,max1]),
    #              (point2,[min2,max2]),...
    #:return: одномерный список numpy со значениями корреляций

    # Проверка, что базовая точка находится в массиве номеров точек
    if base_point_number not in point_numbers:
        print("Базовый датчик отсутствует в списке точек")
        print("Обработка прервана")
        return None

    # Проверка, что число столбцов массива с сигналами равно числу точек в
    # списке
    cdef int signals_column_count = signals.shape[1]
    cdef int points_count = point_numbers.shape[0]
    if points_count != signals_column_count:
        print("Количество сигналов в массиве не совпадает с количеством точек")
        print("Обработка прервана")
        return None

    # поиск данных сигнала базового датчика
    column_number = np.where((point_numbers == base_point_number))[0][0]
    cdef np.ndarray[np.float_t, ndim = 1] base_point_signal = signals[:, column_number]

    # Объявление переменных перед работо главного цикла
    cdef:
        # Создание выходного массива с данными средних максимальных квадратов корреляций
        np.ndarray[np.float_t, ndim = 1] result = np.empty(shape=0, dtype=np.float)
        # сигнал для текущей точки
        np.ndarray[np.float_t, ndim = 1] current_point_signal
        # среднее значение корреляции
        double avg_correlation
        # сумма квадратов корреляций
        double sum_correlation
        # максимальное значение корреляции
        double max_correlation
        # текущее значение корреляции
        double corr
        # сумма элементов сигнала a
        double sum_a
        # сумма элементов сигнала b
        double sum_b
        # сумма квадратов элементов сигнала a
        double sumsq_a
        # сумма квадратов элементов сигнала b
        double sumsq_b
        # сумма произведений пар элементов сигналов a и b
        double sum_a_b
        double val
        # текущий момент для обработки
        int base_moment
        # текущая задержка
        int current_delay
        # минимальная задержка
        int min_moment_delay
        # максимальная задержка
        int max_moment_delay
        # итерационные переменные
        int i,n

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
            min_moment_delay = -9999
            max_moment_delay = -9999
            for i in range(len(moment_delays)):
                point_number = moment_delays[i][0]
                if point_number == point:
                    min_moment_delay = moment_delays[i][1][0]
                    max_moment_delay = moment_delays[i][1][1]
                    break

            # Если задержки для текущей пары не найдены, то функция преращает
            # работу
            if min_moment_delay == -9999 or max_moment_delay == -9999:
                print("Не найдены задержки для датчика")
                print("Обработка прервана")
                return None

            # поиск сигнала для текущей точки
            column_number = np.where((point_numbers == point))[0][0]
            current_point_signal = signals[:, column_number]

            # расчет максимальной корреляции для текущего датчика
            max_correlation = -9999

            # корреляция считается по альтернативной формуле через суммы без
            # вычисления среднего см. ссылку
            # https://myslide.ru/documents_4/fb5049f5e3104927ac47a5009bfc8cc7
            # /img11.jpg


            # нахождение сумм для базового сигнала
            sum_a = sumsq_a = 0
            n = moment_window
            for i in range(n):
                sum_a += base_point_signal[base_moment + i]
                sumsq_a += base_point_signal[base_moment + i] ** 2

            # теперь обход идет по задержкам
            for current_delay in \
                    range(min_moment_delay, max_moment_delay + 1, 1):
                # нахождение сумм для текущего сигнала
                sum_b = sumsq_b = sum_a_b = 0
                for i in range(n):
                    val = current_point_signal[base_moment + current_delay + i]
                    sum_b += val 
                    sumsq_b += val * val
                    # сумма произведений
                    sum_a_b += base_point_signal[base_moment + i] * val
                # вычисление корреляции
                corr = (sum_a_b * n - sum_a * sum_b) / ((sumsq_a * n - sum_a**2) * (sumsq_b * n - sum_b**2)) ** 0.5
                # нахождение модуля корреляции
                if corr < 0:
                    corr = -corr

                # Отборка максимальной корреляции
                if corr > max_correlation:
                    max_correlation = corr

            # Возведение корреляции в квадрат
            max_correlation = max_correlation ** 2

            # Суммирование квадратов корреляции
            sum_correlation += max_correlation

        # Вычисление средней корреляции
        avg_correlation = sum_correlation / (len(point_numbers) - 1)
        # Добавление результата корреляции в результирующий массив
        result = np.append(result, [avg_correlation])

        if (base_moment - 200) % 1000 == 0:
            print(
                'Обработано {} тыс. записей'.format(
                    (base_moment - 200) // 1000))

    return result
