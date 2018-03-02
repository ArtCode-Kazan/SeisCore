import matplotlib.pyplot as plt
plt.plot([1,2,3,4])
plt.show()

# from SeisCore.GeneralPlottingFunctions.histogram import histogram
#
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
# import numpy as np
#
# data=[1,2,3,4,5,6,3,1,3,3,3,3,34,4,4,44,5,6,7,8,9,11,1,1,1,1,1,1,5]
# bin_size=3
#
# #histogram(data,3,'yhftyf')
#
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
