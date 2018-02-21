import numpy as np

from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import nodes,calc_time

nodes_data=nodes(radius=60, count_nodes=1000)
max_depth=230
velocity=2000
frequency=1000
            # поиск максимального и минимального времени задержки между
            # двумя датчиками от точек, находящихся на глубине
            # max_depth и в узлах квадрата и точками датчиков
min_delta_moments = 99999999
max_delta_moments = -9999999

x1=-190
y1=-70
x2=-190
y2=-10


for x_node, y_node in nodes_data:
    time_a = calc_time(x1=x1,
                       y1=y1,
                                    z1=0,
                                    x2=x_node,
                                    y2=y_node,
                                    z2=max_depth,
                                    velocity=velocity)
    time_b = calc_time(x1=x2,
                                       y1=y2,
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
    delta_moments = int(round(frequency * (time_b - time_a)))
    if delta_moments < min_delta_moments:
                        min_delta_moments = delta_moments
    if delta_moments > max_delta_moments:
                        max_delta_moments = delta_moments

print(min_delta_moments, max_delta_moments)


