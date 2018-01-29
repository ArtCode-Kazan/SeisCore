import random


def rgb_for_matlib(rgb):
    """
    Функция преобразования цветов каналов RGB  в hex-формат
    :param rgb: кортеж со значениями каналов RGB
    :return: значение цвета в формате hex
    """
    hex_val = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    return hex_val


def random_hex_colors_generators(color_count):
    """
    Функция для генерации случайного набора цветов в формате html (hex)
    :param color_count: количество цветов, которое нужно получить
    :return: список цветов в формате html (hex)

    """
    line_colors_list = list()
    for i in range(color_count):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = rgb_for_matlib((r, g, b))
        if color not in line_colors_list:
            line_colors_list.append(color)
    line_colors_list.sort()
    return line_colors_list
