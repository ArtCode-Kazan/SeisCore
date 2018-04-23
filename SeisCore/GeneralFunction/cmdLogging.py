from datetime import datetime


def print_message(text, level):
    """
    Функция для логирования собьытий в командной строке
    :param text: текст сообщения
    :param level: уровень сообщения
    :return: void
    """
    current_time = datetime.now()
    text = ' ' * 4 * level + text
    print('{} {}'.format(current_time, text))
