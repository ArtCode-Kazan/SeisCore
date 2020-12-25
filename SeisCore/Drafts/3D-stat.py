import numpy as np


def get_median(voxel: np.array, window_size, window_center):
    """
    :param voxel: трехмерная voxi-модель исследуемого параметра
    :param window_size: трехмерное окно с размерами, указанными в виде
    количесва ячеек
    :param window_center: центр окна, указанный в виде индекса ячейки
    :return: медиана значений в выбранном окне
    """
    ix, iy, iz = window_center
    wx, wy, wz = window_size
    # размер модели в ячейках
    nx, ny, nz = voxel.shape

    # вычисление пределов для извлечения куска, соотвествующего заданному окну
    ix_min=0 if ix-wx//2<0 else ix-wx//2
    ix_max=nx if ix+wx//2>nx else ix+wx//2

    iy_min = 0 if iy - wy // 2 < 0 else iy - wy // 2
    iy_max = ny if iy + wy // 2 > ny else iy + wy // 2

    iz_min = 0 if iz - wz // 2 < 0 else iz - wz // 2
    iz_max = nz if iz + wz // 2 > nx else iz + wz // 2

    selection_part=voxel[ix_min:ix_max,iy_min:iy_max, iz_min:iz_max]
    return np.median(selection_part)


# создание рандомной модели с размерами nx=100, ny=200, nz=300 ячеек
nx, ny, nz = 100,200,300
arr=np.random.randint(-1000,1000,size=(nx,ny, nz))

# расчет медианы в окне c координатами x=20, y=10, z=30 и размерами dx=5,
# dy=6, dz=10
window_center=(20,10,30)
window_size=(5,6,10)
print(get_median(arr,window_size, window_center))
