import re


def checking_name(value):
    """
    Функция для проверки корректности имени файла/папки на допустимые
    символы. Допустимыми является латиница, цифры, тире и нижнее подчеркивание
    :param value: строка
    :return: True - если все верно, False - если имя неверно
    """
    if not re.match('[a-zA-Z0-9-_]*$', value):
        return False
    else:
        return True