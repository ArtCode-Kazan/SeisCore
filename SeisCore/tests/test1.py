import numpy as np

def reproject_coords(points_coords, x_central=0, y_central=0):
    """
    Функция перевода координат в условную СК
    :param points_coords: двухмерный массив numpy с координатами датчиков
    :param x_central: координата x центральной точки
    :param y_central: координата y центральной точки
    :return: список экземпляров класса GRPPoint c пересчитанными координатами
    """
    # пересчет координат
    result=np.empty(shape=(points_coords.shape[0],2),dtype=float)
    for i in range(points_coords.shape[0]):
      result[i,0]=points_coords[i,0] - x_central
      result[i,1]=points_coords[i,0] - y_central
    return result

a=np.array([[0,0],[10,10],[0,10]])
b=reproject_coords(a, x_central=10, y_central=10)
print(b)