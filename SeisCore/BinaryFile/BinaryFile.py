import os
import struct
from datetime import datetime
from datetime import timedelta
import numpy as np
import re
import uuid

from SeisCore.BinaryFile.Cython.Resampling.Execute import Resampling


def _generate_name():
    """
    Функция для генерации уникального имени
    :return:
    """
    return uuid.uuid4().hex


def _binary_read(bin_data, skipping_bytes, x_type, count):
    """
    Функция для чтения бинарной строки (любого типа)
    :param bin_data: открытый BIN-файл filedata = open(file_00, 'rb')
    :param skipping_bytes: Количество байт, которое следует пропустить от
    начала файла для полсдующего чтения
    :param x_type: тип данных
    :param count: количество данных(цифр, букв)
    :return: возвращает прочитанные данные
    """
    if x_type == 's':
        d_size = 1
    elif x_type == 'H':
        d_size = 2
    elif x_type == 'I':
        d_size = 4
    elif x_type in ['d', 'Q']:
        d_size = 8
    else:
        return None

    fmt = str(count) + x_type
    size = d_size * count

    bin_data.read(skipping_bytes)
    record = bin_data.read(size)
    if x_type == 's':
        result = struct.unpack(fmt, record)[0].decode('utf-8')
    else:
        result = struct.unpack(fmt, record)[0]
    return result


class MainHeader:
    """
    базовая структура главного заголовка файла
    """

    def __init__(self, device_type):
        # тип файла - служебное поле
        self.__device_type = device_type

    @property
    def _device_type(self):
        return self.__device_type

    # Общие поля для обоих типов приборов
    # количество каналов
    channel_count = None
    # текущая версия
    version = None
    # день записи
    day = None
    # месяц записи
    month = None
    # год записи
    year = None
    # название станции
    station_name = None
    # широта
    latitude = None
    # долгота
    longitude = None
    # Экслюзивные поля для каждого типа прибора
    if _device_type in ['Baikal7', 'Baikal7Part']:
        # шаг квантования сигнала по времени (в секундах) = 1/signal_frequency
        dt = None
        # зарезервировано системой
        reserved1 = None
        # зарезервировано системой
        reserved2 = None
        # разрядность АЦП
        digitsACP = None
        # зарезервировано системой
        reserved3 = None
        # частота дискретизации
        signal_frequency = None
        # зарезервировано системой
        reserved4 = None
        # неясное содержание
        to_low = None
        # неясное содержание
        to_high = None
        # зарезервировано системой
        reserved5 = None
        # зарезервировано системой
        reserved6 = None
        # время начала записи
        time_begin = None
        # зарезервировано системой
        reserved7 = None

    if _device_type == 'Baikal8':
        # шаг квантования сигнала по времени (в секундах) = 1/signal_frequency
        dt = None
        # Не используется, оставлено для совместимости с предыдущими версиями
        test_type = None
        # Не используется
        satellite_number = None
        # Не используется
        minutes_without_valid = None
        # Не используется
        synchronization_flag = None
        # Не используется
        digits = None
        # Не используется
        old_valid = None
        # Не используется
        version_bi = None
        # Не используется
        version_data = None
        # Не используется
        version_adsp = None
        # Не используется
        old_satellites = None
        # Не используется
        signal = None
        # Время начала файла, в секундах относительно начала дня
        # (см. поля year, month, day)
        time_first_point = None
        # Не используется
        deltas = None
        # Не используется
        old_time_begin = None
        # Не используется
        time_point_file = None
        # Не используется
        time_begin = None
        # Не используется
        synchro_point = None
        # Не используется
        reserved = None

    if _device_type == 'Sigma':
        resolution = None
        signal_frequency = None
        date_start=None
        time_start=None

    def check_correct(self):
        """
        свойство-геттер для проверки корректности класса
        :return:
        """
        errors = list()
        if self._device_type in ['Baikal7', 'Baikal7Part'] and \
                self.signal_frequency is None:
            errors.append('Отсутствует частота записи сигнала')

        if self._device_type == 'Baikal8':
            if self.dt is None:
                errors.append(
                    'Отсутствует шаг квантования сигнала по времени')
            if self.dt == 0:
                errors.append(
                    'Шаг квантования сигнала по времени равен нулю.')

        if self._device_type == 'Sigma' and self.signal_frequency is None:
            errors.append('Отсутствует частота записи сигнала')

        if self._device_type in ('Baikal7','Baikal8'):
            if self.day is None:
                errors.append('Отсутствует значение дня начала записи сигнала')
            if self.month is None:
                errors.append('Отсутствует значение месяца начала записи сигнала')
            if self.year is None:
                errors.append('Отсутствует значение года начала записи сигнала')

        if self.longitude is None:
            errors.append('Отсутствует значение долготы')
        if self.latitude is None:
            errors.append('Отсутствует значение широты')
        if self._device_type == 'Baikal7':
            if self.time_begin is None:
                errors.append('Отсутствует значение времени начала записи '
                              'сигнала')

        if self._device_type == 'Baikal8':
            if self.time_first_point is None:
                errors.append('Отсутствует значение времени начала записи '
                              'сигнала')

        if len(errors) > 0:
            error = '\n'.join(errors)
            return False, error
        else:
            return True, None

    @property
    def full_time_start(self):
        """
        Свойство-геттер для получения Даты+времени старта запуска прибора
        :return: datetime
        """
        is_correct = self.check_correct()
        if not is_correct:
            return None
        if self._device_type in ['Baikal7', 'Baikal7Part']:
            # получение времени в секундах, начиная от 1 января 1980 г 0:00:00
            seconds = self.time_begin / 256000000
            # точка отсчета времени в приборе 1 января 1980 г 0:00:00
            start_date = datetime(1980, 1, 1, 0, 0, 0)
            end_date = start_date + timedelta(seconds=seconds)
            return end_date
        elif self._device_type == 'Baikal8':
            # получение времени в секундах, начиная от начала новых суток
            seconds = self.time_first_point
            # точка отсчета времени в приборе
            year = self.year
            month = self.month
            day = self.day
            start_date = datetime(year, month, day, 0, 0, 0)
            end_date = start_date + timedelta(seconds=seconds)
            return end_date
        elif self._device_type == 'Sigma':
            date_src=str(self.date_start)
            time_src=str(self.time_start)
            if len(time_src)==5:
                time_src='0'+time_src
            year = 2000+int(date_src[:2])
            month = int(date_src[2:4])
            day = int(date_src[4:])
            hour = int(time_src[:2])
            minute=int(time_src[2:4])
            second=int(time_src[4:])
            return datetime(year, month, day, hour, minute, second)
        else:
            return None

    @property
    def frequency(self):
        """
        Свойство-геттер, возвращающее частоту дискретизации записи сигнала
        :return:
        """
        if self._device_type in ['Baikal7', 'Baikal7Part']:
            if self.dt is None or self.dt == 0:
                return self.signal_frequency
            else:
                return int(1 / self.dt)
        elif self._device_type == 'Baikal8':
            if self.dt is None or self.dt == 0:
                return None
            else:
                return int(1 / self.dt)
        elif self._device_type == 'Sigma':
            return self.signal_frequency
        else:
            return None

    def get_binary_format(self):
        """
        Метод, возвращающий заголовок файла в бинарном формате
        :return:
        """
        if self._device_type in ['Baikal7', 'Baikal7Part']:
            result = struct.pack('H', self.channel_count)
            result += struct.pack('H', self.reserved1)
            result += struct.pack('H', self.version)
            result += struct.pack('H', self.day)
            result += struct.pack('H', self.month)
            result += struct.pack('H', self.year)
            result += struct.pack('3H', self.reserved2, 0, 0)
            result += struct.pack('H', self.digitsACP)
            result += struct.pack('H', self.reserved3)
            result += struct.pack('H', self.signal_frequency)
            result += struct.pack('4H', self.reserved4, 0, 0, 0)
            result += struct.pack('16s', self.station_name.encode('utf-8'))
            result += struct.pack('d', self.dt)
            result += struct.pack('I', self.to_low)
            result += struct.pack('I', self.to_high)
            result += struct.pack('d', self.reserved5)
            result += struct.pack('d', self.latitude)
            result += struct.pack('d', self.longitude)
            result += struct.pack('2Q', self.reserved6, 0)
            result += struct.pack('Q', self.time_begin)
            result += struct.pack('4H', self.reserved7, 0, 0, 0)
        elif self._device_type == 'Baikal8':
            result = struct.pack('H', self.channel_count)
            result += struct.pack('H', self.test_type)
            result += struct.pack('H', self.version)
            result += struct.pack('H', self.day)
            result += struct.pack('H', self.month)
            result += struct.pack('H', self.year)
            result += struct.pack('H', self.satellite_number)
            result += struct.pack('H', self.minutes_without_valid)
            result += struct.pack('H', self.synchronization_flag)
            result += struct.pack('H', self.digits)
            result += struct.pack('H', self.old_valid)
            result += struct.pack('H', self.version_bi)
            result += struct.pack('H', self.version_data)
            result += struct.pack('H', self.version_adsp)
            result += struct.pack('H', self.old_satellites)
            result += struct.pack('H', self.signal)
            result += struct.pack('16s', self.station_name.encode('utf-8'))
            result += struct.pack('d', self.dt)
            result += struct.pack('d', self.time_first_point)
            result += struct.pack('d', self.deltas)
            result += struct.pack('d', self.latitude)
            result += struct.pack('d', self.longitude)
            result += struct.pack('Q', self.old_time_begin)
            result += struct.pack('Q', self.time_point_file)
            result += struct.pack('Q', self.time_begin)
            result += struct.pack('I', self.synchro_point)
            result += struct.pack('I', self.reserved)
        else:
            result = None
        return result


class ChannelHeader:
    """
    базовая структура заголовка канала. На данный момент нигде не используется
    """

    def __init__(self, device_type):
        # тип файла - служебное поле
        self.__device_type = device_type

    @property
    def _device_type(self):
        return self.__device_type

    # Общие поля для обоих типов приборов
    # номер канала
    phys_num = None
    # зарезервировано системой
    reserved = None
    # название канала
    channel_name = None
    # тип сенсора
    sensor_type = None
    # коэффициент
    coefficient = None
    # неясное содержание
    calcfreq = None
    # Эксклюзивные поля для каждого типа прибора
    if _device_type in ['Baikal7', 'Baikal7Part']:
        # неясное содержание
        adc_gain = None

    def get_binary_format(self):
        """
        Метод, возвращающий заголовк канала в бинарном виде
        :return:
        """
        if self._device_type in ['Baikal7', 'Baikal7Part']:
            result = struct.pack('H', self.phys_num)
            result += struct.pack('H', self.adc_gain)
            result += struct.pack('2H', self.reserved, 0)
            result += struct.pack('24s', self.channel_name.encode('utf-8'))
            result += struct.pack('24s', self.sensor_type.encode('utf-8'))
            result += struct.pack('d', self.coefficient)
            result += struct.pack('d', self.calcfreq)
        elif self._device_type == 'Baikal8':
            result = struct.pack('H', self.phys_num)
            result += struct.pack('3H', self.reserved, 0, 0)
            result += struct.pack('24s', self.channel_name.encode('utf-8'))
            result += struct.pack('24s', self.sensor_type.encode('utf-8'))
            result += struct.pack('d', self.coefficient)
            result += struct.pack('d', self.calcfreq)
        else:
            result = None
        return result


class BinaryFile:
    """
    Основной (главный) класс для работы с bin-файлами
    """

    def __init__(self):
        # путь к файлу (полный) - только для вывода текста ошибок
        self.__input_path = None
        # путь к файлу (полный)
        self.__path = None
        # тип данных
        self.__data_type = None
        # частота ресемплирования
        self.__resample_frequency = None
        # тип записи данных
        self.__record_type = None
        # boolean-параметр извлечения сигнала только даты записи
        self.__only_date_start_signal = False
        # boolean-параметр удаления среднего значения из каждого канала
        self.__use_avg_values = False
        # дата+время начала считывания сигнала
        self.__read_date_time_start = None
        # дата+время окончания считывания сигнала
        self.__read_date_time_stop = None

    @property
    def path(self):
        return self.__path

    def get_file_name_pattern(self):
        if self.data_type in ('Ordinal', 'Control', 'Well'):
            # example - PO_123B_123A_117
            pattern = '^[A-Z]{2,2}_[0-9]+[A-Z]*_[0-9]+[A-Z]*' \
                      '_[0-9]+[A-Z]*$'
        elif self.data_type == 'Variation':
            # example - VR_2018-06-30_123A_117
            pattern = '^VR_[0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_' \
                      '[0-9]+[A-Z]*_[0-9]+[A-Z]*$'
        elif self.data_type == 'Revise':
            # example - RV_2018-06-30_12_1117V
            pattern = '^RV_[0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_' \
                      '[0-9]+[A-Z]*_[0-9]+[A-Z]*$'
        elif self.data_type == 'HydroFrac':
            # example - HF_0151_2018-06-30_23-59-30_12_1117V
            pattern = '^HF_[0-9]{4,4}_[0-9]{4,4}-[0-9]{2,2}-' \
                      '[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-' \
                      '[0-9]{2,2}_[a-zA-Z0-9]+_[a-zA-Z0-9]+$'
        else:
            pattern = ''
        return pattern

    @path.setter
    def path(self, value):
        self.__input_path = value
        if len(value) != 0:
            if os.path.isfile(value):
                file_name = os.path.basename(value)
                t = file_name.split('.')
                if len(t) == 2:
                    name, extension = t
                    pattern = self.get_file_name_pattern()
                    if re.match(pattern, name):
                        self.__path = value

    @property
    def data_type(self):
        if self.__data_type is None:
            self.__data_type = 'NoDataType'
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        if value in ('HydroFrac', 'Revise', 'Variation', 'Ordinal', 'Control',
                     'Well'):
            self.__data_type = value
        else:
            self.__data_type = 'NoDataType'

    @property
    def resample_frequency(self):
        if self.__resample_frequency is None:
            if self.signal_frequency is not None:
                self.__resample_frequency = self.signal_frequency
                return self.__resample_frequency
            else:
                return None
        else:
            return self.__resample_frequency

    @resample_frequency.setter
    def resample_frequency(self, value):
        if isinstance(value, int):
            signal_freq = self.signal_frequency
            if signal_freq is not None:
                if signal_freq % value == 0:
                    self.__resample_frequency = value

    @property
    def use_avg_values(self):
        return self.__use_avg_values

    @use_avg_values.setter
    def use_avg_values(self, value):
        """
        Флаг - использовать ли вычитание среднего фона сигнала
        :param value: True/False
        :return:
        """
        if isinstance(value, bool):
            self.__use_avg_values = value

    @property
    def only_date_start_signal(self):
        return self.__only_date_start_signal

    @only_date_start_signal.setter
    def only_date_start_signal(self, value):
        """
        Флаг - сделать чтение части сигнала, относящегося к дате начала записи
        :param value:
        :return:
        """
        if isinstance(value, bool) and self.path is not None:
            self.__only_date_start_signal = value

    @property
    def read_date_time_start(self):
        if self.__read_date_time_start is None:
            self.__read_date_time_start = self.datetime_start
        return self.__read_date_time_start

    @read_date_time_start.setter
    def read_date_time_start(self, value):
        if self.only_date_start_signal:
            self.__read_date_time_start = self.datetime_start
        else:
            if isinstance(value, datetime) and self.path is not None:
                dt1 = (value - self.datetime_start).total_seconds()
                if dt1 >= 0:
                    self.__read_date_time_start = value
                else:
                    self.__read_date_time_start = self.datetime_start

    @property
    def read_date_time_stop(self):
        if self.__read_date_time_stop is None:
            self.__read_date_time_stop = self.datetime_stop
        return self.__read_date_time_stop

    @read_date_time_stop.setter
    def read_date_time_stop(self, value):
        if self.only_date_start_signal:
            date_time_in = self.datetime_start
            date_time_out = datetime(year=date_time_in.year,
                                     month=date_time_in.month,
                                     day=date_time_in.day) + \
                            timedelta(days=1, microseconds=-1)
            if self.datetime_stop <= date_time_out:
                self.__read_date_time_stop = self.datetime_stop
            else:
                self.__read_date_time_stop = date_time_out
        else:
            if isinstance(value, datetime) and self.path is not None:
                dt2 = (self.datetime_stop - value).total_seconds()
                if dt2 >= 0:
                    self.__read_date_time_stop = value
                else:
                    self.__read_date_time_stop = self.datetime_stop

    @property
    def start_moment(self):
        if self.path is None:
            return None
        dt = (self.read_date_time_start - self.datetime_start).total_seconds()
        return int(round(dt * self.signal_frequency))

    @property
    def end_moment(self):
        if self.path is None:
            return None
        dt = (self.read_date_time_stop - self.datetime_start).total_seconds()
        return int(round(dt * self.signal_frequency)+1)

    @property
    def device_type(self):
        if self.path is None:
            return None
        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        if extension=='00':
            return 'Baikal7'
        elif extension=='00part':
            return 'Baikal7Part'
        elif extension == 'xx':
            return 'Baikal8'
        elif extension == 'bin':
            return 'Sigma'
        else:
            return 'null'

    @property
    def main_header(self):
        # проверка пути к файлу
        if self.path is None:
            return None

        # чтение файла
        file_data = open(self.path, 'rb')
        # ----------------------------------------
        # объем главного заголовка 120 байт
        # ----------------------------------------
        # создание экземпляра класса MainHeader
        main_header = MainHeader(self.device_type)
        # парсинг заголовка в зависимости от типа файла
        if self.device_type in ['Baikal7', 'Baikal7Part']:
            main_header.channel_count = _binary_read(file_data, 0, 'H', 1)
            main_header.reserved1 = _binary_read(file_data, 0, 'H', 1)
            main_header.version = _binary_read(file_data, 0, 'H', 1)
            main_header.day = _binary_read(file_data, 0, 'H', 1)
            main_header.month = _binary_read(file_data, 0, 'H', 1)
            main_header.year = _binary_read(file_data, 0, 'H', 1)
            main_header.reserved2 = _binary_read(file_data, 0, 'H', 3)
            main_header.digitsACP = _binary_read(file_data, 0, 'H', 1)
            main_header.reserved3 = _binary_read(file_data, 0, 'H', 1)
            main_header.signal_frequency = _binary_read(file_data, 0, 'H', 1)
            main_header.reserved4 = _binary_read(file_data, 0, 'H', 4)
            main_header.station_name = _binary_read(file_data, 0, 's', 16)
            main_header.dt = _binary_read(file_data, 0, 'd', 1)
            main_header.to_low = _binary_read(file_data, 0, 'I', 1)
            main_header.to_high = _binary_read(file_data, 0, 'I', 1)
            main_header.reserved5 = _binary_read(file_data, 0, 'd', 1)
            main_header.latitude = _binary_read(file_data, 0, 'd', 1)
            main_header.longitude = _binary_read(file_data, 0, 'd', 1)
            main_header.reserved6 = _binary_read(file_data, 0, 'Q', 2)
            main_header.time_begin = _binary_read(file_data, 0, 'Q', 1)
            main_header.reserved7 = _binary_read(file_data, 0, 'H', 4)
        elif self.device_type == 'Baikal8':
            main_header.channel_count = _binary_read(file_data, 0, 'H', 1)
            main_header.test_type = _binary_read(file_data, 0, 'H', 1)
            main_header.version = _binary_read(file_data, 0, 'H', 1)
            main_header.day = _binary_read(file_data, 0, 'H', 1)
            main_header.month = _binary_read(file_data, 0, 'H', 1)
            main_header.year = _binary_read(file_data, 0, 'H', 1)
            main_header.satellite_number = _binary_read(file_data, 0, 'H', 1)
            main_header.minutes_without_valid = \
                _binary_read(file_data, 0, 'H', 1)
            main_header.synchronization_flag = \
                _binary_read(file_data, 0, 'H', 1)
            main_header.digits = _binary_read(file_data, 0, 'H', 1)
            main_header.old_valid = _binary_read(file_data, 0, 'H', 1)
            main_header.version_bi = _binary_read(file_data, 0, 'H', 1)
            main_header.version_data = _binary_read(file_data, 0, 'H', 1)
            main_header.version_adsp = _binary_read(file_data, 0, 'H', 1)
            main_header.old_satellites = _binary_read(file_data, 0, 'H', 1)
            main_header.signal = _binary_read(file_data, 0, 'H', 1)
            main_header.station_name = _binary_read(file_data, 0, 's', 16)
            main_header.dt = _binary_read(file_data, 0, 'd', 1)
            main_header.time_first_point = _binary_read(file_data, 0, 'd', 1)
            main_header.deltas = _binary_read(file_data, 0, 'd', 1)
            main_header.latitude = _binary_read(file_data, 0, 'd', 1)
            main_header.longitude = _binary_read(file_data, 0, 'd', 1)
            main_header.old_time_begin = _binary_read(file_data, 0, 'Q', 1)
            main_header.time_point_file = _binary_read(file_data, 0, 'Q', 1)
            main_header.time_begin = _binary_read(file_data, 0, 'Q', 1)
            main_header.synchro_point = _binary_read(file_data, 0, 'I', 1)
            main_header.reserved = _binary_read(file_data, 0, 'I', 1)
        elif self.device_type == 'Sigma':
            main_header.channel_count = _binary_read(file_data, 12, 'I', 1)
            main_header.version = _binary_read(file_data,0,'I',1)
            main_header.resolution = _binary_read(file_data,0,'I',1)
            main_header.signal_frequency = _binary_read(file_data, 0, 'I', 1)
            # main_header.station_name = _binary_read(file_data, 0, 's',12)
            main_header.latitude = _binary_read(file_data, 12, 's',8)
            main_header.longitude = _binary_read(file_data, 0, 's', 9)
            main_header.date_start = _binary_read(file_data, 3, 'I', 1)
            main_header.time_start = _binary_read(file_data, 0, 'I', 1)

        file_data.close()
        is_correct, error = main_header.check_correct()
        if not is_correct:
            return None
        return main_header

    def get_channel_header(self, channel_index):
        """
        Метод чтения заголовка канала по его индексу
        :param channel_index:
        :return:
        """
        # проверка пути к файлу
        if self.path is None:
            return None

        bin_data = open(self.path, 'rb')
        # пропуск главного заголовка (120 байт) + предыдущих заголовков
        # каналов (
        # кажый по 72 байта)
        bin_data.seek(120 + 72 * channel_index)
        # чтение текущего заголовка
        channel_header = ChannelHeader(self.device_type)
        if self.device_type == 'Baikal7':
            channel_header.phys_num = _binary_read(bin_data, 0, "H", 1)
            channel_header.adc_gain = _binary_read(bin_data, 0, "H", 1)
            channel_header.reserved = _binary_read(bin_data, 0, "H", 2)
            channel_header.channel_name = _binary_read(bin_data, 0, "s", 24)
            channel_header.sensor_type = _binary_read(bin_data, 0, "s", 24)
            channel_header.coefficient = _binary_read(bin_data, 0, "d", 1)
            channel_header.calcfreq = _binary_read(bin_data, 0, "d", 1)
        elif self.device_type == 'Baikal7Part':
            channel_header.phys_num = 0
            channel_header.adc_gain = 0
            channel_header.reserved = 10
            channel_header.channel_name = '_'
            channel_header.sensor_type = '_'
            channel_header.coefficient = 0.0
            channel_header.calcfreq = 0.0
        if self.device_type == 'Baikal8':
            channel_header.phys_num = _binary_read(bin_data, 0, "H", 1)
            channel_header.reserved = _binary_read(bin_data, 0, "H", 3)
            channel_header.channel_name = _binary_read(bin_data, 0, "s", 24)
            channel_header.sensor_type = _binary_read(bin_data, 0, "s", 24)
            channel_header.coefficient = _binary_read(bin_data, 0, "d", 1)
            channel_header.calcfreq = _binary_read(bin_data, 0, "d", 1)
        bin_data.close()
        return channel_header

    @property
    def signal_frequency(self):
        main_header = self.main_header
        if main_header is None:
            return None
        else:
            return main_header.frequency

    @property
    def datetime_start(self):
        main_header = self.main_header
        if main_header is None:
            return None
        else:
            return main_header.full_time_start

    @property
    def longitude(self):
        main_header = self.main_header
        if main_header is None:
            return None
        if self.device_type in ('Baikal7', 'Baikal7Part', 'Baikal8'):
            return main_header.longitude
        elif self.device_type=='Sigma':
            return float(main_header.longitude[1:-1])
        else:
            return None

    @property
    def latitude(self):
        main_header = self.main_header
        if main_header is None:
            return None
        if self.device_type in ('Baikal7', 'Baikal7Part', 'Baikal8'):
            return main_header.latitude
        elif self.device_type == 'Sigma':
            return float(main_header.latitude[:-1])
        else:
            return None

    @property
    def discrete_amount(self):
        if self.path is None:
            return None
        file_size = os.path.getsize(self.path)
        discrete_amount = int((file_size - 336) / 12)
        return discrete_amount

    @property
    def seconds_duration(self):
        discrete_count = self.discrete_amount
        freq = self.signal_frequency
        if discrete_count is None or freq is None:
            return None
        delta_seconds = (discrete_count - 1) / freq
        return delta_seconds

    @property
    def datetime_stop(self):
        delta_sec = self.seconds_duration
        dt_start = self.datetime_start
        if delta_sec is None or dt_start is None:
            return None
        result = dt_start + timedelta(seconds=delta_sec)
        return result

    @property
    def resample_parameter(self):
        signal_frequency = self.signal_frequency
        resample_frequency = self.resample_frequency
        if signal_frequency is None or resample_frequency is None:
            return None
        else:
            return signal_frequency // resample_frequency

    @property
    def record_type(self):
        if self.__record_type is None:
            self.__record_type='ZXY'
        return self.__record_type

    def check_correct(self):
        errors = list()
        if self.path is None:
            errors.append(
                'Неверно указан путь к файлу {0}. Проверьте имя файла на '
                'допустимые символы'.format(self.__input_path))
        else:
            if self.signal_frequency is None:
                errors.append('Не указана частота дискретизации записи '
                              'сигнала')
            if self.record_type is None:
                errors.append('Неверно указан тип записи файла')
            if self.datetime_start is None:
                errors.append(
                    'Ошибка чтения даты+времени старта начала записи прибора')
            if self.longitude is None:
                errors.append('Ошибка чтения долготы точки записи сигнала')
            if self.latitude is None:
                errors.append('Ошибка чтения широты точки записи сигнала')
            if self.start_moment >= self.end_moment:
                errors.append('Неверно указаны пределы извлечения сигнала')
            # if self.discrete_amount is not None:
            #     if self.seconds_duration < 3600:
            #         errors.append('Записанный сигнал в файле менее '
            #                       'одного часа')

            if self.data_type in ('Revise', 'Variation'):
                file_name = os.path.basename(self.path)
                name, extension = file_name.split('.')
                info = name.split('_')
                date_value = datetime.strptime(info[1], '%Y-%m-%d').date()
                if self.datetime_start is not None:
                    if date_value != self.datetime_start.date():
                        errors.append(
                            'Дата записи файла ({}) не совпадает с '
                            'датой, указанной в названии '
                            'файла({})'.format(self.datetime_start.date(),
                                               file_name))
        if len(errors) > 0:
            error = '\n'.join(errors)
            return False, error
        else:
            return True, None

    @property
    def components_index(self):
        record_type = self.record_type
        if record_type is None:
            return None
        x_component_index = record_type.index('X')
        y_component_index = record_type.index('Y')
        z_component_index = record_type.index('Z')
        return x_component_index, y_component_index, z_component_index

    @property
    def signals(self):
        # проверка полей класса
        is_correct, error = self.check_correct()
        if not is_correct:
            return None

        # чтение файла
        file_data = open(self.path, 'rb')
        # пропуск части файла, если указана стартовая позиция
        # start_moment - номер дискреты, с которого начинается выборка
        # сигнала. если параметр равен None, выборка начинается от первого
        # отсчета (нумерация отсчетов с единицы)
        # signals = None
        bytes_count = self.start_moment * 4 * 3
        file_data.seek(336 + bytes_count)

        moment_count = self.end_moment - self.start_moment
        try:
            bin_data = file_data.read(moment_count * 3 * 4)
            signals = np.frombuffer(bin_data, dtype=np.int32)
        except MemoryError:
            return None
        finally:
            # закрытие файла
            file_data.close()

        # проверка на пустотность выборки сигнала
        if signals.shape[0] == 0:
            return None

        # перестройка формы массива
        channel_count = 3
        signal_count = signals.shape[0] // channel_count
        signals = np.reshape(signals, newshape=(signal_count, channel_count))

        # проверка на размер выборки сигнала,
        # если указаны end_moment и start_moment
        if (self.end_moment - self.start_moment) != signal_count:
            print('Error: wrong size array data')
            return None

        # проверка значения параметра ресемплирования
        if self.resample_parameter is None:
            return None

        # операция ресемплирования
        if self.resample_parameter > 1:
            # проверка кратности параметра ресемплирования и длины сигнала
            if signals.shape[0] % self.resample_parameter != 0:
                new_size = signals.shape[0] - \
                           (signals.shape[0] % self.resample_parameter)
                signals = signals[:new_size]
            resample_signal = Resampling.resampling(signals,
                                                    self.resample_parameter)
        else:
            resample_signal = signals

        # resample_signal.setflags(True)
        resample_signal = np.copy(resample_signal)
        if self.use_avg_values:
            avg_values=np.average(resample_signal, axis=0)
            resample_signal=resample_signal-avg_values
        return resample_signal

    @property
    def ordered_signal_by_components(self):
        signal = self.signals
        channel_x, channel_y, channel_z = self.components_index
        result = np.empty_like(signal, dtype=np.int)
        result[:, 0] = signal[:, channel_x]
        result[:, 1] = signal[:, channel_y]
        result[:, 2] = signal[:, channel_z]
        return result

    @property
    def extension(self):
        if self.device_type == 'Baikal7':
            return '00'
        if self.device_type =='Baikal7Part':
            return '00part'
        elif self.device_type == 'Baikal8':
            return 'xx'
        elif self.device_type == 'Sigma':
            return 'bin'
        else:
            return 'null'

    @property
    def unique_file_name(self):
        return '{}.{}'.format(_generate_name(), self.extension)

    @property
    def registrator_number(self):
        if self.path is None:
            return None
        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        parser = re.findall('[0-9]+[A-Z]*', name)
        return parser[-2].upper()

    @property
    def sensor_number(self):
        if self.path is None:
            return None
        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        parser = re.findall('[0-9]+[A-Z]*', name)
        return parser[-1].upper()

    @property
    def point_prefix(self):
        if self.data_type in ('Revise', 'Variation'):
            return None

        if self.path is None:
            return None
        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        prefix_value = name[:2]
        return prefix_value

    @property
    def point_name(self):
        if self.path is None:
            return None
        if self.data_type in ('Revise', 'Variation'):
            return None

        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        if self.data_type in ('Ordinal', 'Control', 'Well'):
            parser = re.findall('[0-9]+[A-Z]*', name)
            point_name = parser[0]
            try:
                number = int(point_name)
                return number, 'A'
            except ValueError:
                try:
                    number = int(point_name[:-1])
                    attr = point_name[-1]
                    return number, attr
                except ValueError:
                    return None
        if self.data_type == 'HydroFrac':
            parser = re.findall('[0-9]{4,4}', name)
            point_name = int(parser[0])
            return point_name

    # @property
    # def dates(self):
    #     is_correct, errors = self.check_correct()
    #     if not is_correct:
    #         return None
    #
    #     record_start = self.datetime_start
    #     record_stop = self.datetime_stop
    #
    #     days_count = (record_stop.date() - record_start.date()).days + 1
    #
    #     result = list()
    #     for i in range(days_count):
    #         result.append(record_start + timedelta(days=i))
    #     return tuple(result)
    #
    # def split_file_by_date(self, export_folder):
    #     """
    #     Метод для разбития bin-файла на части, чтобы сигнал был отнесен
    #     только к единой дате
    #     :param export_folder: папка экспорта данных
    #     :return:
    #     """
    #     date_list = self.dates
    #     if date_list is None:
    #         return None
    #
    #     # запоминание начального состояния параметров
    #     start_use_avg_values_flag = self.__use_avg_values
    #     start_read_dt_start_value = self.__read_date_time_start
    #     start_read_dt_stop_value = self.__read_date_time_stop
    #
    #     # принудительное отключение вычитания средних значений
    #     self.__use_avg_values = False
    #
    #     record_start = self.datetime_start
    #     record_stop = self.datetime_stop
    #
    #     if len(date_list) == 1:
    #         return None
    #
    #     # получение заголовков файла
    #     main_header = self.main_header
    #     channel_header_a = self.get_channel_header(channel_index=0)
    #     channel_header_b = self.get_channel_header(channel_index=1)
    #     channel_header_c = self.get_channel_header(channel_index=2)
    #
    #     extension = self.extension
    #     sensor_number = self.sensor_number
    #     registrator_number = self.registrator_number
    #
    #     days_count = len(date_list)
    #     output_files = list()
    #     for day_index in range(days_count):
    #         left_dt = datetime(year=record_start.year,
    #                            month=record_start.month,
    #                            day=record_start.day) + \
    #                   timedelta(days=day_index)
    #         if left_dt < record_start:
    #             left_dt = record_start
    #
    #         right_dt = datetime(year=record_start.year,
    #                             month=record_start.month,
    #                             day=record_start.day) + \
    #                    timedelta(days=day_index + 1, microseconds=-1)
    #         if right_dt > record_stop:
    #             right_dt = record_stop
    #
    #         main_header.day = left_dt.day
    #         main_header.month = left_dt.month
    #         main_header.year = left_dt.year
    #
    #         if self.device_type == 'Baikal7':
    #             marker_dt = datetime(1980, 1, 1, 0, 0, 0)
    #             seconds_count = int((left_dt - marker_dt).total_seconds())
    #             main_header.time_begin = seconds_count * 256000000
    #         elif self.device_type == 'Baikal8':
    #             marker_dt = datetime(year=left_dt.year,
    #                                  month=left_dt.month,
    #                                  day=left_dt.day)
    #             seconds_count = (left_dt - marker_dt).total_seconds()
    #             main_header.time_first_point = seconds_count
    #
    #         if self.data_type == 'Revise':
    #             output_name = 'RV_{}_{}_{}.{}'.format(
    #                 datetime.strftime(left_dt, '%Y-%m-%d'),
    #                 registrator_number,
    #                 sensor_number, extension)
    #         elif self.data_type == 'Variation':
    #             output_name = 'VR_{}_{}_{}.{}'.format(
    #                 datetime.strftime(left_dt, '%Y-%m-%d'),
    #                 registrator_number,
    #                 sensor_number, extension)
    #         elif self.data_type in ('Revise', 'Variation', 'Ordinal',
    #                                 'Control', 'Well'):
    #             point_prefix = self.point_prefix
    #             number, attr = self.point_name
    #             point_name = '{}{}'.format(number, attr)
    #             output_name = '{}_{}_{}_{}.{}'.format(
    #                 point_prefix, point_name, registrator_number,
    #                 sensor_number,
    #                 extension)
    #         else:
    #             output_name = 'ZZ_{}_{}_{}.{}'.format(
    #                 datetime.strftime(left_dt, '%Y-%m-%d'),
    #                 registrator_number,
    #                 sensor_number, extension)
    #
    #         export_path = os.path.join(export_folder, output_name)
    #
    #         # запись файла
    #         f = open(export_path, 'wb')
    #         f.write(main_header.get_binary_format())
    #         f.write(channel_header_a.get_binary_format())
    #         f.write(channel_header_b.get_binary_format())
    #         f.write(channel_header_c.get_binary_format())
    #
    #         block_count = int((right_dt - left_dt).total_seconds() / 3600) + 1
    #         for block_index in range(block_count):
    #             left_dt_block = left_dt + timedelta(hours=block_index)
    #             if left_dt_block >= right_dt:
    #                 break
    #             right_dt_block = left_dt_block + timedelta(hours=1,
    #                                                        microseconds=-1)
    #             if right_dt_block > right_dt:
    #                 right_dt_block = right_dt
    #             self.__read_date_time_start = left_dt_block
    #             self.__read_date_time_stop = right_dt_block
    #             block_signals = self.signals
    #             if block_signals is None:
    #                 break
    #             block_signals.astype(np.int32).tofile(f)
    #         f.close()
    #         output_files.append(output_name)
    #
    #     # восстановление исходных значений
    #     self.__use_avg_values = start_use_avg_values_flag
    #     self.__read_date_time_start = start_read_dt_start_value
    #     self.__read_date_time_stop = start_read_dt_stop_value
    #     return tuple(output_files)
