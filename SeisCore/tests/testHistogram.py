from SeisCore.GeneralPlottingFunctions.histogram import histogram

from SeisCore.HydroFracCore.PlottingFunctions.histograms import \
    histogram_moments_delay

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

data = [[(1, 2), (-81, -81)], [(1, 3), (-20, -20)], [(1, 4), (5, 5)],
        [(1, 5), (-20, -20)], [(1, 6), (-81, -81)], [(2, 3), (61, 61)],
        [(2, 4), (86, 86)], [(2, 5), (61, 61)], [(2, 6), (0, 0)],
        [(3, 4), (26, 26)], [(3, 5), (1, 1)], [(3, 6), (-61, -61)],
        [(4, 5), (-25, -25)], [(4, 6), (-86, -86)], [(5, 6), (-61, -61)]]

histogram_moments_delay(data, 'text')

# # расчет количества бинов
# bin_count=int((np.max(data)-np.min(data))//bin_size)
# # бинирование данных
# hist, bins = np.histogram(data, bins=bin_count)
#
# # создание бланка графика
# fig = plt.figure()
#
# # размер плота в дюймах
# fig.set_size_inches(7, 5)
# # разрешение отображения графика
# fig.dpi = 96
# # подготовка осей
# axes = fig.add_subplot(111)
#
# # расстановка делений по оси x
# # значение одного интервала равно размеру бина
# axes.xaxis.set_major_locator(ticker.MultipleLocator(bin_size))
# # планируется 10 интервалов
# dy_size=np.max(hist)/10
# axes.yaxis.set_major_locator(ticker.MultipleLocator(dy_size))
#
# # расчет ширины столбца
# width = 1 * (bins[1] - bins[0])
# # расчет положения столбца по x
# center = (bins[:-1] + bins[1:]) / 2
# # построение гистограммы
# axes.bar(center, hist, align='center', width=width,edgecolor= 'black')
# # подпись гистограммы
# axes.set_title('dgdg')
# # отображение гистограммы
# plt.show()
