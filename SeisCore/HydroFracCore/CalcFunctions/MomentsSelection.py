# coding=utf-8
"""
Данный модуль содержит функции для первичной обработки данных ГРП - отбор
моментов событий на основе максимальных значений квадратов коэф-тов
кросскорреляции
"""

import numpy as np


def quantilies(data, procents=[95, 96, 97, 98, 99]):
    """
    Функция для вычисления квантилей (процентилей) по ряду данных
    :param data: одномерный массив numpy со значениями максимальных квадратов
    коэф-тов кросскорреляции
    :param procents: список с целыми числами - проценты, для которых нужно
    найти квантили.
    По умолчанию заданы проценты 95, 96, 97, 98
    :return: одномерный список со значениями квантилей
    """
    result = list()
    for procent in procents:
        current_quantile = np.percentile(data, procent)
        result.append(current_quantile)
    return result


def get_intervals(moments_numbers, epsilon=1):
    """
    Функция для представления номеров отсчетов сигналов (отсортированных)
    в виде интервалов. Например, [1,2,3,7,8,9] при epsilon=1 будет
    представлен в виде интервалов [1,3],[7,9]
    :param moments_numbers: отсортированный одномерный массив numpy
    с номерами отсчетов сигнала
    :param epsilon: допуск для склеивания текущего номера с предыдущим
    интервалом (по умолчанию=1 дискрета)
    :return: двухмерный массив numpy с границами интервалов
    (границы включительны!!!)
    """
    result = np.empty(shape=0, dtype=int)
    result = np.append(result, moments_numbers[0])
    for i in range(moments_numbers.shape[0] - 1):
        if moments_numbers[i + 1] - moments_numbers[i] > epsilon:
            result = np.append(result, moments_numbers[i])
            result = np.append(result, moments_numbers[i + 1])
    result = np.append(result, moments_numbers[-1])
    result = np.reshape(result, (result.shape[0] // 2, 2))
    return result


def quantile_intervals(data, quantile, epsilon=0):
    """
    Функция для получения интервалов индексов моментов, где значение
    корреляции больше или равно значению квантиля
    :param data: одномерный массив numpy со значениями максимальных
    квадратов коэф-тов кросскорреляции
    :param quantile: значение квантиля (НЕ ПРОЦЕНТ!, а значение)
    :param epsilon: допуск отклонения корреляции от квантиля
    :return: интервалы индексов моментов
    """
    selection_indexes = \
        np.where((abs(data - quantile) <= epsilon) + (data >= quantile))[0]
    result = get_intervals(selection_indexes)
    return result


def is_crossing_intervals(interval_a, interval_b):
    """
    Функция для проверки находится ли интервал A внутри интервала B
    :param interval_a: список с пределами интервала
    (интервал включительно с границами)
    :param interval_b: список с пределами интервала
    (интервал включительно с границами)
    :return: True - если находится, False - если нет
    """
    if (interval_b[0] <= interval_a[0]) and (
            interval_b[0] < interval_a[1]) and (
            interval_b[1] > interval_a[0]) and \
            (interval_b[1] >= interval_a[1]):
        return True
    else:
        return False


def intervals_intersection(intervals):
    """
    Функция для получения пересечений интервалов
    :param intervals: двухмерный массив numpy с интервалами
    :return: двухмерный отсеянный массив интервалов
    """
    # создание маски для удаления неподходящих элементов массива
    mask_to_delete = np.empty(shape=intervals.shape[0], dtype=bool)
    # изначально предполагается, что все элементы верные,
    # поэтому их удалять нельзя, поэтому начальное значение False
    mask_to_delete[:] = False

    # начинается перебор интервалов всех со всеми
    for i in range(intervals.shape[0]):
        # получение первого интервала
        interval_a = [intervals[i][0], intervals[i][1]]
        for j in range(intervals.shape[0]):
            # получение второго интервала
            interval_b = [intervals[j][0], intervals[j][1]]

            # если интервал A входит в интервал B, то интервал B помечается
            # на удаление, так как он шире, чем интервал A
            if is_crossing_intervals(interval_a, interval_b) and (i != j):
                mask_to_delete[j] = True

            # если интервал B входит в интервал A, то интервал A помечается
            # на удаление, так как он шире, чем интервал B
            if is_crossing_intervals(interval_b, interval_a) and (i != j):
                mask_to_delete[i] = True

    # очистка входного массива от неподходящих интервалов
    result_intervals = intervals[~mask_to_delete]

    return result_intervals


def max_value_index(data, interval=None):
    """
    Функция для поиска номера индекса максимального элемента массива в
    заданном интервале индексов элементов
    :param data: одномерный массив numpy со значениями максимальных квадратов
    коэф-тов кросскорреляции
    :param interval: интервал массива  в виде списка, где необходимо выполнить
     поиск (границы включительно!)
    По умолчанию None - выполняется поиск по всему массиву
    :return: номер индекса
    """
    if interval is None:
        result = np.where(data == np.max(data))
    else:
        result = np.where(data == np.max(data[interval[0]:interval[1] + 1]))
    return result


def moments_selection(data, procents=[95, 96, 97, 98, 99], epsilon=0):
    """
    Обобщенная функция для получения отсчетов сигналов
    :param data: одномерный массив numpy со значениями максимальных квадратов
    коэф-тов кросскорреляции
    :param procents: список из процентов для расчетов квантилей.
    По умолчанию [95, 96, 97, 98, 99]
    :param epsilon: допуск отклонения коэ-тов корреляции от значения квантиля
    при выборке
    :param minute_number: номер минуты для обработки. По умолчанию -9999
    :param export_folder: папка для экспорта результата в файл. о умолчанию
    - None - экспорт не производится
    :param export_file_name: имя файла для экспорта
    :return: одномерный numpy массив с номерами индексов отсчетов
    (нумерация идет от ноля)
    """
    # расчет квантилей
    quants = quantilies(data=data, procents=procents)

    # получение интервалов для всех квантилей
    base_intervals = np.empty(shape=0, dtype=int)
    for i in range(len(quants)):
        ins = quantile_intervals(data=data, quantile=quants[i],
                                 epsilon=epsilon)
        base_intervals = np.append(base_intervals, ins)

    # изменение формы массива
    column_count = 2
    row_count = base_intervals.shape[0] // column_count
    base_intervals = np.reshape(base_intervals, (row_count, column_count))

    # поиск пересечений интервалов
    intersections = intervals_intersection(base_intervals)

    # поиск индекса максимального элемента массива в выбранных
    # интервалах пересечений
    result = np.empty(shape=0, dtype=int)
    for interval in intersections:
        left_edge = interval[0]
        # +1, чтобы получить полуоткрытый интервал
        right_edge = interval[1] + 1
        index_with_max_value = max_value_index(data, interval=[left_edge,
                                                               right_edge])
        result = np.append(result, index_with_max_value)
    result = np.sort(result)
    return result
