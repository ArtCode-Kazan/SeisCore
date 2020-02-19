import os
import struct
from datetime import datetime
from datetime import timedelta
import numpy as np
import re
import uuid

from SeisCore.BinaryFile.Cython.Resampling.Execute import Resampling


def generate_name():
    """
    Generating unique file name
    :return:
    """
    return uuid.uuid4().hex


def binary_read(bin_data, skipping_bytes, x_type, count):
    """
    Reading binary record (different data type)
    :param bin_data: open binary file [filedata = open(file_00, 'rb')]
    :param skipping_bytes: bytes amount for skipping bytes from last pointer
    :param x_type: data C-type [s-string, H-unsigned short, I-unsigned int,
                                d-double, Q-unsigned long long]
    :param count: symbols count(numbers, literals)
    :return: python data type
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
    Base structure of file main header
    """

    def __init__(self, device_type):
        # file type [Baikal7, Baikal8, Sigma, Baikal7Part]
        self.__device_type = device_type

    @property
    def _device_type(self):
        return self.__device_type

    # Common fields for all device types
    channel_count = None
    version = None
    # record day
    day = None
    # record month
    month = None
    # record year
    year = None
    station_name = None
    latitude = None
    longitude = None

    # Exclusive fields for each device type
    if _device_type in ['Baikal7', 'Baikal7Part']:
        # time step (in seconds) = 1/signal_frequency
        dt = None
        # system reserved
        reserved1 = None
        # system reserved
        reserved2 = None
        # don't use
        digitsACP = None
        # system reserved
        reserved3 = None
        signal_frequency = None
        # system reserved
        reserved4 = None
        # unknown
        to_low = None
        # unknown
        to_high = None
        # system reserved
        reserved5 = None
        # system reserved
        reserved6 = None
        # start time of recording signal
        time_begin = None
        # system reserved
        reserved7 = None

    if _device_type == 'Baikal8':
        # time step (in seconds) = 1/signal_frequency
        dt = None
        # don't use
        test_type = None
        # don't use
        satellite_number = None
        # don't use
        minutes_without_valid = None
        # don't use
        synchronization_flag = None
        # don't use
        digits = None
        # don't use
        old_valid = None
        # don't use
        version_bi = None
        # don't use
        version_data = None
        # don't use
        version_adsp = None
        # don't use
        old_satellites = None
        # don't use
        signal = None
        # Time in seconds from the beginning of the day
        time_first_point = None
        # don't use
        deltas = None
        # don't use
        old_time_begin = None
        # don't use
        time_point_file = None
        # don't use
        time_begin = None
        # don't use
        synchro_point = None
        # don't use
        reserved = None

    if _device_type == 'Sigma':
        resolution = None
        signal_frequency = None
        date_start=None
        time_start=None

    def check_correct(self):
        """
        checking data correction
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

        if self._device_type in ('Baikal7', 'Baikal8'):
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
        Date and time start of signal recording
        :return:
        """
        is_correct = self.check_correct()
        if not is_correct:
            return None
        if self._device_type in ['Baikal7', 'Baikal7Part']:
            seconds = self.time_begin / 256000000
            start_date = datetime(1980, 1, 1, 0, 0, 0)
            end_date = start_date + timedelta(seconds=seconds)
            return end_date
        elif self._device_type == 'Baikal8':
            seconds = self.time_first_point
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
        Signal frequency
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
        Method for packing header data to binary format
        :return: binary data (C-type)
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
    Base structure of channel header. Now don't use
    """

    def __init__(self, device_type):
        # file type [Baikal7, Baikal8, Baikal7Part, Sigma]
        self.__device_type = device_type

    @property
    def _device_type(self):
        return self.__device_type

    # Common fields for all device types
    # channel number
    phys_num = None
    # system reserved
    reserved = None
    channel_name = None
    sensor_type = None
    coefficient = None
    # unknown
    calcfreq = None

    # Exclusive fields for Baikal7 and Baikal7Part
    if _device_type in ['Baikal7', 'Baikal7Part']:
        # unknown
        adc_gain = None

    def get_binary_format(self):
        """
        Method for packing header data to binary format
        :return: binary data (C-type)
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
    def __init__(self):
        # full file path - using only for error output
        self.__input_path = None
        # full file path
        self.__path = None
        # data type
        self.__data_type = None
        # resample frequency
        self.__resample_frequency = None
        # record type (by default ZXY)
        self.__record_type = None
        # boolean-parameter for subtraction average values
        self.__use_avg_values = False
        # date and time for start signal reading
        self.__read_date_time_start = None
        # date and time for end signal reading
        self.__read_date_time_stop = None

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
                    if extension in ['00','xx', '00part', 'bin']:
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
        Flag - using substraction average values for signal
        :param value: True - using / False - not need
        :return:
        """
        if isinstance(value, bool):
            self.__use_avg_values = value

    @property
    def read_date_time_start(self):
        if self.__read_date_time_start is None:
            self.__read_date_time_start = self.datetime_start
        return self.__read_date_time_start

    @read_date_time_start.setter
    def read_date_time_start(self, value):
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
        if self.path is None:
            return None

        file_data = open(self.path, 'rb')
        # ----------------------------------------
        # Volume main header 120 bytes
        # ----------------------------------------
        main_header = MainHeader(self.device_type)
        if self.device_type in ['Baikal7', 'Baikal7Part']:
            main_header.channel_count = binary_read(file_data, 0, 'H', 1)
            main_header.reserved1 = binary_read(file_data, 0, 'H', 1)
            main_header.version = binary_read(file_data, 0, 'H', 1)
            main_header.day = binary_read(file_data, 0, 'H', 1)
            main_header.month = binary_read(file_data, 0, 'H', 1)
            main_header.year = binary_read(file_data, 0, 'H', 1)
            main_header.reserved2 = binary_read(file_data, 0, 'H', 3)
            main_header.digitsACP = binary_read(file_data, 0, 'H', 1)
            main_header.reserved3 = binary_read(file_data, 0, 'H', 1)
            main_header.signal_frequency = binary_read(file_data, 0, 'H', 1)
            main_header.reserved4 = binary_read(file_data, 0, 'H', 4)
            main_header.station_name = binary_read(file_data, 0, 's', 16)
            main_header.dt = binary_read(file_data, 0, 'd', 1)
            main_header.to_low = binary_read(file_data, 0, 'I', 1)
            main_header.to_high = binary_read(file_data, 0, 'I', 1)
            main_header.reserved5 = binary_read(file_data, 0, 'd', 1)
            main_header.latitude = binary_read(file_data, 0, 'd', 1)
            main_header.longitude = binary_read(file_data, 0, 'd', 1)
            main_header.reserved6 = binary_read(file_data, 0, 'Q', 2)
            main_header.time_begin = binary_read(file_data, 0, 'Q', 1)
            main_header.reserved7 = binary_read(file_data, 0, 'H', 4)
        elif self.device_type == 'Baikal8':
            main_header.channel_count = binary_read(file_data, 0, 'H', 1)
            main_header.test_type = binary_read(file_data, 0, 'H', 1)
            main_header.version = binary_read(file_data, 0, 'H', 1)
            main_header.day = binary_read(file_data, 0, 'H', 1)
            main_header.month = binary_read(file_data, 0, 'H', 1)
            main_header.year = binary_read(file_data, 0, 'H', 1)
            main_header.satellite_number = binary_read(file_data, 0, 'H', 1)
            main_header.minutes_without_valid = \
                binary_read(file_data, 0, 'H', 1)
            main_header.synchronization_flag = \
                binary_read(file_data, 0, 'H', 1)
            main_header.digits = binary_read(file_data, 0, 'H', 1)
            main_header.old_valid = binary_read(file_data, 0, 'H', 1)
            main_header.version_bi = binary_read(file_data, 0, 'H', 1)
            main_header.version_data = binary_read(file_data, 0, 'H', 1)
            main_header.version_adsp = binary_read(file_data, 0, 'H', 1)
            main_header.old_satellites = binary_read(file_data, 0, 'H', 1)
            main_header.signal = binary_read(file_data, 0, 'H', 1)
            main_header.station_name = binary_read(file_data, 0, 's', 16)
            main_header.dt = binary_read(file_data, 0, 'd', 1)
            main_header.time_first_point = binary_read(file_data, 0, 'd', 1)
            main_header.deltas = binary_read(file_data, 0, 'd', 1)
            main_header.latitude = binary_read(file_data, 0, 'd', 1)
            main_header.longitude = binary_read(file_data, 0, 'd', 1)
            main_header.old_time_begin = binary_read(file_data, 0, 'Q', 1)
            main_header.time_point_file = binary_read(file_data, 0, 'Q', 1)
            main_header.time_begin = binary_read(file_data, 0, 'Q', 1)
            main_header.synchro_point = binary_read(file_data, 0, 'I', 1)
            main_header.reserved = binary_read(file_data, 0, 'I', 1)
        elif self.device_type == 'Sigma':
            main_header.channel_count = binary_read(file_data, 12, 'I', 1)
            main_header.version = binary_read(file_data, 0, 'I', 1)
            main_header.resolution = binary_read(file_data, 0, 'I', 1)
            main_header.signal_frequency = binary_read(file_data, 0, 'I', 1)
            # main_header.station_name = _binary_read(file_data, 0, 's',12)
            main_header.latitude = binary_read(file_data, 12, 's', 8)
            main_header.longitude = binary_read(file_data, 0, 's', 9)
            main_header.date_start = binary_read(file_data, 3, 'I', 1)
            main_header.time_start = binary_read(file_data, 0, 'I', 1)

        file_data.close()
        is_correct, error = main_header.check_correct()
        if not is_correct:
            return None
        return main_header

    def get_channel_header(self, channel_index):
        """
        Method getting channel header by index
        :param channel_index: channel index
        :return:
        """
        if self.path is None:
            return None

        bin_data = open(self.path, 'rb')
        # skipping main header and other channel header
        bin_data.seek(120 + 72 * channel_index)
        channel_header = ChannelHeader(self.device_type)
        if self.device_type == 'Baikal7':
            channel_header.phys_num = binary_read(bin_data, 0, "H", 1)
            channel_header.adc_gain = binary_read(bin_data, 0, "H", 1)
            channel_header.reserved = binary_read(bin_data, 0, "H", 2)
            channel_header.channel_name = binary_read(bin_data, 0, "s", 24)
            channel_header.sensor_type = binary_read(bin_data, 0, "s", 24)
            channel_header.coefficient = binary_read(bin_data, 0, "d", 1)
            channel_header.calcfreq = binary_read(bin_data, 0, "d", 1)
        elif self.device_type == 'Baikal7Part':
            channel_header.phys_num = 0
            channel_header.adc_gain = 0
            channel_header.reserved = 10
            channel_header.channel_name = '_'
            channel_header.sensor_type = '_'
            channel_header.coefficient = 0.0
            channel_header.calcfreq = 0.0
        if self.device_type == 'Baikal8':
            channel_header.phys_num = binary_read(bin_data, 0, "H", 1)
            channel_header.reserved = binary_read(bin_data, 0, "H", 3)
            channel_header.channel_name = binary_read(bin_data, 0, "s", 24)
            channel_header.sensor_type = binary_read(bin_data, 0, "s", 24)
            channel_header.coefficient = binary_read(bin_data, 0, "d", 1)
            channel_header.calcfreq = binary_read(bin_data, 0, "d", 1)
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
        is_correct, error = self.check_correct()
        if not is_correct:
            return None

        file_data = open(self.path, 'rb')
        # skipping bytes
        bytes_count = self.start_moment * 4 * 3
        file_data.seek(336 + bytes_count)

        moment_count = self.end_moment - self.start_moment
        try:
            bin_data = file_data.read(moment_count * 3 * 4)
            signals = np.frombuffer(bin_data, dtype=np.int32)
        except MemoryError:
            return None
        finally:
            file_data.close()

        if signals.shape[0] == 0:
            return None

        channel_count = 3
        signal_count = signals.shape[0] // channel_count
        signals = np.reshape(signals, newshape=(signal_count, channel_count))

        if (self.end_moment - self.start_moment) != signal_count:
            print('Error: wrong size array data')
            return None

        if self.resample_parameter is None:
            return None

        if self.resample_parameter > 1:
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
        return '{}.{}'.format(generate_name(), self.extension)

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
