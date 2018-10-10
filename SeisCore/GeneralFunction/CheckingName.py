import re


def checking_name(value):
    """
    Функция для проверки корректности имени файла/папки на допустимые
    символы. Допустимыми является строка SS_000..._000..._000...
    (две латинские буквы_числа_числа)
    :param value: строка
    :return: True - если все верно, False - если имя неверно
    """
    pattern = '^[A-Z]{2,2}_[0-9]+[A-Z]*_[0-9]+[A-Z]*_[0-9]+[A-Z]*$'
    if not re.match(pattern, value):
        return False
    else:
        return True
