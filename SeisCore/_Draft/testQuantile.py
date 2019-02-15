import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import quantilies
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import \
    moments_selection2,quantile_intervals

file_path=r'D:\Обмен\Result\Res\CorrelationData.dat'

data=np.loadtxt(file_path)

# вычисление значений квантилей для всех минут
# перевод массива корреляций в скаляр
all_correlation_data = np.reshape(data,
                                  newshape=data.shape[0]*data.shape[1])

# расчет квантилей для всех данных по всем минутам
general_quants=quantilies(data=all_correlation_data,procents=[95,96,97,98,99])

current_correlation_data=data[:,0]

quantile_intervals(data=current_correlation_data, quantile=general_quants[0])

# current_moment_selection = moments_selection2(
#         data=current_correlation_data, quantiles_value=general_quants)
