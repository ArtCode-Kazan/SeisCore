import math
import numpy as np
import datetime


def get_by_first(first_pt, l):
    """
    Функция, которая по списку first_pt, в котором номера двух датчиков
    находит их максимальную и минимальную задержку
    :param first_pt: список для пары датчиков
    :param l: список задержек во времени прихода сигналов (в тактах) для каждой пары датчиков (maxminVector)
    :return: Возвращает список вида [Tmin, Tmax]
    """
    return [p[1] for p in l if p[0] == first_pt][0]


def main_correlation_process(tauBetween):
    sort_res = [[10, 11, 0.9], [100, 101, 0.85], [113, 114, 0.8]]
    max_corr_pos = [sort_res[0][0]]
    for i in range(1, len(sort_res)):
        for c in max_corr_pos:
            if math.fabs(c - sort_res[i][0]) < tauBetween:
                break
        else:
            max_corr_pos.append(sort_res[i][0])
    print(max_corr_pos)

main_correlation_process(50)
