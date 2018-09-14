import os
import struct
from datetime import datetime
from datetime import timedelta
import numpy as np
import re
import uuid

from SeisCore.BinaryFile.Cython.Resampling.ResamplingExecute import Resampling


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


class _MainHeader:
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
    # шаг квантования сигнала по времени (в секундах) = 1/signal_frequency
    dt = None
    # широта
    latitude = None
    # долгота
    longitude = None
    # Экслюзивные поля для каждого типа прибора
    if _device_type == 'Baikal7':
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

    def check_correct(self):
        """
        свойство-геттер для проверки корректности класса
        :return:
        """
        errors = list()
        if self._device_type == 'Baikal7' and self.signal_frequency is None:
            errors.append('Отсутствует частота записи сигнала')
        if self._device_type == 'Baikal8':
            if self.dt is None:
                errors.append('Отсутствует шаг квантования сигнала по времени')
            if self.dt == 0:
                errors.append('Шаг квантования сигнала по времени равен нулю.')
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
        if self._device_type == 'Baikal7':
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
        else:
            return None

    @property
    def frequency(self):
        """
        Свойство-геттер, возвращающее частоту дискретизации записи сигнала
        :return:
        """
        if self.dt is None or self.dt == 0:
            if self._device_type == 'Baikal7':
                return self.signal_frequency
            if self._device_type == 'Baikal8':
                return None
        else:
            return int(1 / self.dt)


class _ChannelHeader:
    """
    базовая структура заголовка канала. На данный момент нигде не используется
    """
    # тип файла - служебное поле
    device_type = None

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
    if device_type == 'Baikal7':
        # неясное содержание
        adc_gain = None


def _read_channel_header(file_path, file_type, channel_number):
    """
    Функция для чтения заголовка канала.
    На данный момент нигде не используется
    :param file_path: путь к бинарному файлу
    :param file_type: тип файла
    :param channel_number: номер канала для считывания (нумерация от ноля)
    :return:
    """
    bin_data = open(file_path, 'rb')
    # пропуск главного заголовка (120 байт) + редыдущих заголовков каналов (
    # кажый по 72 байта)
    bin_data.seek(120 + 72 * channel_number)
    # чтение текущего заголовка
    channel_header = _ChannelHeader()
    if file_type == 'Baikal7':
        channel_header.phys_num = _binary_read(bin_data, 120, "H", 1)
        channel_header.adc_gain = _binary_read(bin_data, 0, "H", 1)
        channel_header.reserved = _binary_read(bin_data, 0, "H", 2)
        channel_header.channel_name = _binary_read(bin_data, 0, "s", 24)
        channel_header.sensor_type = _binary_read(bin_data, 0, "s", 24)
        channel_header.coefficient = _binary_read(bin_data, 0, "d", 1)
        channel_header.calcfreq = _binary_read(bin_data, 0, "d", 1)
    if file_type == 'Baikal8':
        channel_header.phys_num = _binary_read(bin_data, 120, "H", 1)
        channel_header.reserved = _binary_read(bin_data, 0, "H", 3)
        channel_header.channel_name = _binary_read(bin_data, 0, "s", 24)
        channel_header.sensor_type = _binary_read(bin_data, 0, "s", 24)
        channel_header.coefficient = _binary_read(bin_data, 0, "d", 1)
        channel_header.calcfreq = _binary_read(bin_data, 0, "d", 1)
    bin_data.close()
    return channel_number


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
        # номер отсчета для начала выгрузки куска сигнала
        self.__start_moment = None
        # номер отсчета для конца выгрузки куска сигнала
        self.__end_moment = None
        # среднее значение по каналам
        self.__avg_value_channels = None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__input_path = value
        if len(value) != 0:
            if os.path.isfile(value):
                file_name = os.path.basename(value)
                t = file_name.split('.')
                if len(t) == 2:
                    name, extension = t
                    if self.data_type in ('Ordinal', 'Control'):
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
                    else:
                        pattern = ''
                    if re.match(pattern, name):
                        self.__path = value

    @property
    def data_type(self):
        if self.__data_type is None:
            self.__data_type = 'NoDataType'
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        if value in ('Revise', 'Variation', 'Ordinal', 'Control'):
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
    def only_date_start_signal(self):
        return self.__only_date_start_signal

    @only_date_start_signal.setter
    def only_date_start_signal(self, value):
        if isinstance(value, bool) and self.path is not None:
            self.__only_date_start_signal = value

    @property
    def start_moment(self):
        if self.only_date_start_signal:
            return None
        else:
            return self.__start_moment

    @start_moment.setter
    def start_moment(self, value):
        if isinstance(value, int):
            self.__start_moment = value

    @property
    def end_moment(self):
        if self.only_date_start_signal:
            date_time_in = self.datetime_start
            date_time_out = datetime(year=date_time_in.year,
                                     month=date_time_in.month,
                                     day=date_time_in.day) + \
                timedelta(days=1) - timedelta(microseconds=1)

            delta_t = int((date_time_out - date_time_in).total_seconds())
            result = delta_t * self.signal_frequency
            if result > self.discrete_amount:
                return None
            else:
                return result
        else:
            return self.__end_moment

    @end_moment.setter
    def end_moment(self, value):
        if isinstance(value, int):
            self.__end_moment = value

    @property
    def device_type(self):
        if self.path is None:
            return None
        file_name = os.path.basename(self.path)
        name, extension = file_name.split('.')
        if extension == '00':
            return 'Baikal7'
        if extension == 'xx':
            return 'Baikal8'

    @property
    def _main_header(self):
        # проверка пути к файлу
        if self.path is None:
            return None

        # чтение файла
        file_data = open(self.path, 'rb')
        # ----------------------------------------
        # объем главного заголовка 120 байт
        # ----------------------------------------
        # создание экземпляра класса MainHeader
        main_header = _MainHeader(self.device_type)
        # парсинг заголовка в зависимости от типа файла
        if self.device_type == 'Baikal7':
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

        if self.device_type == 'Baikal8':
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
        file_data.close()
        is_correct, error = main_header.check_correct()
        if not is_correct:
            return None
        return main_header

    @property
    def signal_frequency(self):
        main_header = self._main_header
        if main_header is None:
            return None
        else:
            return main_header.frequency

    @property
    def datetime_start(self):
        main_header = self._main_header
        if main_header is None:
            return None
        else:
            return main_header.full_time_start

    @property
    def longitude(self):
        main_header = self._main_header
        if main_header is None:
            return None
        else:
            return main_header.longitude

    @property
    def latitude(self):
        main_header = self._main_header
        if main_header is None:
            return None
        else:
            return main_header.latitude

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
        return self.__record_type

    @record_type.setter
    def record_type(self, value):
        if 'X' in value and 'Y' in value and 'Z' in value and len(value) == 3:
            self.__record_type = value

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
            if self.resample_frequency is None:
                errors.append('Неверно указана частота ресемплирования')
            if self.record_type is None:
                errors.append('Неверно указан тип записи файла')
            if self.datetime_start is None:
                errors.append(
                    'Ошибка чтения даты+времени старта начала записи прибора')
            if self.longitude is None:
                errors.append('Ошибка чтения долготы точки записи сигнала')
            if self.latitude is None:
                errors.append('Ошибка чтения широты точки записи сигнала')
            if self.start_moment is not None and self.end_moment is not None:
                if self.start_moment >= self.end_moment:
                    errors.append('Неверно указаны пределы извлечения сигнала')
                if self.discrete_amount is not None:
                    if self.end_moment >= self.discrete_amount:
                        errors.append('Максимальный предел извлечения сигнала '
                                      'выходит за пределы длительности записи '
                                      'сигнала')

            if self.data_type in ['Revise', 'Variation']:
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
    def average_value_channels(self):
        # проверка полей класса
        is_correct, error = self.check_correct()
        if not is_correct:
            return None

        if self.__avg_value_channels is None:
            # чтение файла
            file_data = open(self.path, 'rb')
            # пропуск части файла с шапкой
            file_data.seek(336)

            # чтение всего сигнала
            try:
                bin_data = file_data.read()
                signals = np.frombuffer(bin_data, dtype=np.int32)
            except MemoryError:
                return None
            finally:
                # закрытие файла
                file_data.close()

            # перестройка формы массива
            channel_count = 3
            signal_count = signals.shape[0] // channel_count
            signals = np.reshape(signals,
                                 newshape=(signal_count, channel_count))

            # Вычисление средних значений
            avg_values = np.mean(a=signals, axis=0).round(decimals=0)
            self.__avg_value_channels = \
                (avg_values[0], avg_values[1], avg_values[2])
        return self.__avg_value_channels

    @property
    def signals(self):
        # проверка полей класса
        is_correct, error = self.check_correct()
        if not is_correct:
            return None

        # вычисление средних значений для каждого канала по всему сигналу
        avg_values = self.average_value_channels
        if avg_values is None:
            return None

        # чтение файла
        file_data = open(self.path, 'rb')
        # пропуск части файла, если указана стартовая позиция
        # start_moment - номер дискреты, с которого начинается выборка
        # сигнала. если параметр равен None, выборка начинается от первого
        # отсчета (нумерация отсчетов с единицы)
        # signals = None
        if self.start_moment is not None:
            bytes_value = self.start_moment * 4 * 3
            file_data.seek(336 + bytes_value)
        else:
            file_data.seek(336)

        if self.end_moment is None:
            try:
                bin_data = file_data.read()
                signals = np.frombuffer(bin_data, dtype=np.int32)
            except MemoryError:
                return None
            finally:
                # закрытие файла
                file_data.close()
        else:
            moment_count = self.end_moment - self.start_moment + 1
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
        if self.start_moment is not None and self.end_moment is not None:
            if (self.end_moment - self.start_moment + 1) != signal_count:
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

        resample_signal.setflags(True)
        resample_signal[:, 0] = resample_signal[:, 0] - avg_values[0]
        resample_signal[:, 1] = resample_signal[:, 1] - avg_values[1]
        resample_signal[:, 2] = resample_signal[:, 2] - avg_values[2]
        return resample_signal

    @property
    def unique_file_name(self):
        if self.device_type == 'Baikal7':
            file_name = '{}.{}'.format(_generate_name(), '00')
        elif self.device_type == 'Baikal8':
            file_name = '{}.{}'.format(_generate_name(), 'xx')
        else:
            file_name = None
        return file_name

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
