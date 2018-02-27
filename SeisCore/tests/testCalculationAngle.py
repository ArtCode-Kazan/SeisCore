import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import nodes,calc_angle


coords_file=r'D:\AppsBuilding\TestingData\where.txt'

x_central=417339
y_central=6229250
max_depth=1991
radius=200

data=np.loadtxt(fname=coords_file)
data[:,1]=data[:,1]-x_central
data[:,2]=data[:,2]-y_central


# выходной список
result = list()
# генерация координат узлов
nodes_data = nodes(radius=radius,count_nodes=1000)
# i и j используются только для того, чтобы избежать попадания в выходной
# список пар датчиков (1, 2) и (2,1). Добавится только один из них - (1, 2)
i = 0
for number_a, x_a, y_a in data:
    i += 1
    j = 0
    for number_b, x_b, y_b in data:
        j += 1
        if i < j:
            max_angle = -9999999
            for x_node, y_node in nodes_data:
                alpha=calc_angle(x_sensor1=x_a,
                                     y_sensor1=y_a,
                                     z_sensor1=0,
                                     x=x_node,
                                     y=y_node,
                                     z=max_depth,
                                     x_sensor2=x_b,
                                     y_sensor2=y_b,
                                     z_sensor2=0)
                if alpha>max_angle:
                        max_angle=alpha
            print(number_a,number_b,max_angle)
