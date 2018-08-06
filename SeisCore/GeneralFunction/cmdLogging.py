from datetime import datetime


def print_message(text, level=0):
    """
    Функция для логирования собьытий в командной строке
    :param text: текст сообщения
    :param level: уровень сообщения
    :return: void
    """
    current_time = datetime.now()
    text = ' ' * 4 * level + text
    print('{} {}'.format(current_time, text))


def error_format(number, text):
    """
    Функция для вывода форматированного текста ошибки
    :param number: номер ошибки (целое число)
    :param text: текст ошибки
    :return: форматированный текст ошибки
    """
    if len(str(number)) < 3:
        number = '0' * (3 - len(str(number))) + str(number)
    else:
        number = str(number)
    result = 'Python Ex{} Error: {}'.format(number, text)
    return result
