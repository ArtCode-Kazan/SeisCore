import os
import struct
from mmap import mmap
from mmap import ACCESS_READ
from datetime import datetime
from datetime import timedelta
import uuid
from typing import NamedTuple
from dataclasses import dataclass

import numpy as np

from seiscore.binaryfile.resampling.wrap import resampling


class TypeClass(NamedTuple):
    label: str
    byte_size: int


class FileHeader(NamedTuple):
    channel_count: int
    frequency: int
    datetime_start: datetime
    longitude: float
    latitude: float


def format_duration(days: int, hours: int, minutes: int,
                    seconds: float) -> str:
    hours_fmt = str(hours).zfill(2)
    minutes_fmt = str(minutes).zfill(2)
    seconds_fmt = f'{seconds:.3f}'.zfill(6)
    if days:
        duration_format = f'{days} days {hours_fmt}:{minutes_fmt}:{seconds_fmt}'
    else:
        duration_format = f'{hours_fmt}:{minutes_fmt}:{seconds_fmt}'
    return duration_format


@dataclass
class FileInfo:
    path: str
    format_type: str
    frequency: int
    time_start: datetime
    time_stop: datetime
    longitude: float
    latitude: float

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def duration_in_seconds(self) -> float:
        return (self.time_stop - self.time_start).total_seconds()

    @property
    def formatted_duration(self) -> str:
        days = int(self.duration_in_seconds / (24 * 3600))
        hours = int((self.duration_in_seconds - days * 24 * 3600) / 3600)
        minutes = int((self.duration_in_seconds - days * 24 * 3600 - hours * 3600) / 60)
        seconds = self.duration_in_seconds - days * 24 * 3600 - hours * 3600 - \
            minutes * 60
        return format_duration(days, hours, minutes, seconds)


CHAR_CTYPE = TypeClass('s', 1)
UNSIGNED_SHORT_CTYPE = TypeClass('H', 2)
UNSIGNED_INT_CTYPE = TypeClass('I', 4)
DOUBLE_CTYPE = TypeClass('d', 8)
UNSIGNED_LONG_LONG_CTYPE = TypeClass('Q', 8)

BAIKAL7_FMT, BAIKAL8_FMT, SIGMA_FMT = 'Baikal7', 'Baikal8', 'Sigma'
BAIKAL7_EXTENSION, BAIKAL8_EXTENSION, SIGMA_EXTENSION = '00', 'xx', 'bin'

BINARY_FILE_FORMATS = {BAIKAL7_FMT: BAIKAL7_EXTENSION,
                       BAIKAL8_FMT: BAIKAL8_EXTENSION,
                       SIGMA_FMT: SIGMA_EXTENSION}

SIGMA_SECONDS_OFFSET = 2


class BadHeaderData(ValueError):
    pass


class BadFilePath(OSError):
    pass


class InvalidComponentName(ValueError):
    pass


class InvalidResampleFrequency(ValueError):
    pass


def is_binary_file_path(path) -> bool:
    if os.path.isfile(path):
        extension = os.path.basename(path).split('.')[-1]
        if extension in {BAIKAL7_EXTENSION, BAIKAL8_EXTENSION,
                         SIGMA_EXTENSION}:
            return True
        else:
            return False
    return False


def binary_read(bin_data, x_type: TypeClass, count: int, skipping_bytes=0) \
        -> Union[str, List[int], List[float], int, float]:
    """
    Reading binary record (different data type)
    :param bin_data: open binary file [bin_data = open(file_00, 'rb')]
    :param skipping_bytes: bytes amount for skipping bytes from beginning
    of file
    :param x_type: data C-type [s-string (char), H-unsigned short,
                                I-unsigned int, d-double,
                                Q-unsigned long long]
    :param count: symbols count or numbers count (not digits!)
    :return: python data type
    """
    fmt = f'{count}{x_type.label}'
    size = x_type.byte_size * count

    bin_data.seek(skipping_bytes)
    record = bin_data.read(size)
    if x_type.label == 's':
        result = struct.unpack(fmt, record)[0].decode('utf-8')
    else:
        if count == 1:
            result = struct.unpack(fmt, record)[0]
        else:
            result = list(struct.unpack(fmt, record))
    return result


def get_datetime_start_baikal7(time_begin: int) -> datetime:
    const_datetime = datetime(1980, 1, 1, 0, 0, 0)
    seconds = time_begin / 256_000_000
    return const_datetime + timedelta(seconds=seconds)


def read_baikal7_header(file_path: str) -> FileHeader:
    """
    Details: http://www.gsras.ru/unu/uploads/files/Dataloggers/Baikal-7HR.pdf
    """
    with open(file_path, 'rb') as f:
        channel_count = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 0)
        frequency = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 22)
        latitude = binary_read(f, DOUBLE_CTYPE, 1, 72)
        longitude = binary_read(f, DOUBLE_CTYPE, 1, 80)
        time_begin = binary_read(f, UNSIGNED_LONG_LONG_CTYPE, 1, 104)

    datetime_start = get_datetime_start_baikal7(time_begin)
    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude)


def read_baikal8_header(file_path: str) -> FileHeader:
    with open(file_path, 'rb') as f:
        channel_count = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 0)
        day = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 6)
        month = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 8)
        year = binary_read(f, UNSIGNED_SHORT_CTYPE, 1, 10)
        dt = binary_read(f, DOUBLE_CTYPE, 1, 48)
        seconds = binary_read(f, DOUBLE_CTYPE, 1, 56)
        latitude = binary_read(f, DOUBLE_CTYPE, 1, 72)
        longitude = binary_read(f, DOUBLE_CTYPE, 1, 80)
    datetime_start = datetime(year, month, day, 0, 0, 0) + timedelta(
        seconds=seconds)
    frequency = int(1 / dt)
    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude)


def read_sigma_header(file_path: str) -> FileHeader:
    with open(file_path, 'rb') as f:
        channel_count = binary_read(f, UNSIGNED_INT_CTYPE, 1, 12)
        frequency = binary_read(f, UNSIGNED_INT_CTYPE, 1, 24)
        latitude_src = binary_read(f, CHAR_CTYPE, 8, 40)
        longitude_src = binary_read(f, CHAR_CTYPE, 9, 48)
        date_src = str(binary_read(f, UNSIGNED_INT_CTYPE, 1, 60))
        time_src = str(binary_read(f, UNSIGNED_INT_CTYPE, 1, 64))

    time_src = time_src.zfill(6)
    year = 2000 + int(date_src[:2])
    month, day = int(date_src[2:4]), int(date_src[4:])
    hours, minutes = int(time_src[:2]), int(time_src[2:4])
    seconds = int(time_src[4:])
    try:
        datetime_start = datetime(year, month, day, hours, minutes,
                                  seconds) + timedelta(seconds=2)
    except ValueError:
        raise BadHeaderData('invalid date/time values')

    try:
        longitude = round(int(longitude_src[:3]) +
                          float(longitude_src[3:-1]) / 60, 2)
        latitude = round(int(latitude_src[:2]) +
                         float(latitude_src[2:-1]) / 60, 2)
    except ValueError:
        raise BadHeaderData('invalid longitude/latitude')
    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude)


class BinaryFile:
    def __init__(self, file_path: str,
                 resample_frequency=0, is_use_avg_values=False):
        is_path_correct = is_binary_file_path(path=file_path)
        if not is_path_correct:
            raise BadFilePath(f'Invalid path - {file_path}')
        # full file path
        self.__path = file_path
        # resample frequency
        self.__resample_frequency = resample_frequency

        # file type
        self.__format_type = None

        # header file data
        self.__header_data = None

        # boolean-parameter for subtraction average values
        self.__is_use_avg_values = is_use_avg_values

        # date and time for start signal reading
        self.__read_date_time_start = None
        # date and time for end signal reading
        self.__read_date_time_stop = None

    @property
    def file_extension(self) -> str:
        return os.path.basename(self.path).split('.')[-1]

    @property
    def path(self) -> str:
        return self.__path

    @property
    def format_type(self) -> str:
        if self.__format_type is None:
            for format_type, extension in BINARY_FILE_FORMATS.items():
                if self.file_extension == extension:
                    self.__format_type = format_type
                    break
        return self.__format_type

    @property
    def unique_file_name(self) -> str:
        return '{}.{}'.format(uuid.uuid4().hex, self.file_extension)

    @property
    def use_avg_values(self) -> bool:
        return self.__use_avg_values

    @use_avg_values.setter
    def use_avg_values(self, value: bool):
        """
        Flag - using substruction average values for signal
        :param value: True - using / False - not need
        :return:
        """
        self.__use_avg_values = value

    @property
    def file_header(self) -> FileHeader:
        if self.__header_data is None:
            format_type = self.format_type
            if format_type == 'Baikal7':
                self.__header_data = read_baikal7_header(self.path)
            elif format_type == 'Baikal8':
                self.__header_data = read_baikal8_header(self.path)
            elif format_type == 'Sigma':
                self.__header_data = read_sigma_header(self.path)
            else:
                pass
        return self.__header_data

    @property
    def signal_frequency(self) -> int:
        return self.file_header.signal_frequency

    @property
    def origin_datetime_start(self):
        return self.file_header.datetime_start

    @property
    def datetime_start(self) -> datetime:
        if self.format_type == 'Sigma':
            time_diff = timedelta(seconds=SIGMA_SECONDS_OFFSET)
        else:
            time_diff = timedelta(seconds=0)
        return self.file_header.datetime_start + time_diff

    @property
    def datetime_stop(self) -> datetime:
        time_diff = timedelta(seconds=self.seconds_duration)
        dt_start = self.datetime_start
        return dt_start + time_diff

    @property
    def longitude(self) -> float:
        return round(self.file_header.longitude, 6)

    @property
    def latitude(self) -> float:
        return round(self.file_header.latitude, 6)

    @property
    def channels_count(self) -> int:
        return self.file_header.channel_count

    @property
    def resample_frequency(self) -> int:
        if self.__resample_frequency == 0:
            self.__resample_frequency = self.signal_frequency
        return self.__resample_frequency

    @resample_frequency.setter
    def resample_frequency(self, value: int):
        signal_freq = self.signal_frequency
        if signal_freq % value == 0:
            self.__resample_frequency = value

    @property
    def read_date_time_start(self) -> datetime:
        if self.__read_date_time_start is None:
            self.__read_date_time_start = self.datetime_start
        return self.__read_date_time_start

    @property
    def corrected_read_datetime_start(self) -> datetime:
        origin_freq = self.signal_frequency
        resample_freq = self.__resample_frequency
        dt_offset = int(0.5 * (origin_freq / resample_freq - 1)) / origin_freq
        return self.read_date_time_start + timedelta(seconds=dt_offset)

    @read_date_time_start.setter
    def read_date_time_start(self, value: datetime):
        dt1 = (value - self.datetime_start).total_seconds()
        if dt1 >= 0:
            self.__read_date_time_start = value
        else:
            self.__read_date_time_start = self.datetime_start

    @property
    def read_date_time_stop(self) -> datetime:
        if self.__read_date_time_stop is None:
            self.__read_date_time_stop = self.datetime_stop
        return self.__read_date_time_stop

    @read_date_time_stop.setter
    def read_date_time_stop(self, value: datetime):
        dt2 = (self.datetime_stop - value).total_seconds()
        if dt2 >= 0:
            self.__read_date_time_stop = value
        else:
            self.__read_date_time_stop = self.datetime_stop

    @property
    def start_moment(self) -> int:
        dt = (self.read_date_time_start - self.datetime_start).total_seconds()
        return int(round(dt * self.signal_frequency))

    @property
    def end_moment(self) -> int:
        dt = (self.read_date_time_stop - self.datetime_start).total_seconds()
        discreet_index = int(round(dt * self.signal_frequency))
        signal_length = discreet_index - self.start_moment
        signal_length -= signal_length % self.resample_parameter
        discreet_index = self.start_moment + signal_length
        return discreet_index

    @property
    def header_memory_size(self) -> int:
        channel_count = self.channels_count
        return 120 + 72 * channel_count

    @property
    def discrete_amount(self):
        file_size = os.path.getsize(self.path)
        discrete_amount = int((file_size - self.header_memory_size) / (
                self.file_header.channel_count * UNSIGNED_INT_CTYPE.byte_size))
        return discrete_amount

    @property
    def seconds_duration(self) -> float:
        discrete_count = self.discrete_amount
        freq = self.signal_frequency
        delta_seconds = (discrete_count - 1) / freq
        return delta_seconds

    @property
    def datetime_stop(self) -> datetime:
        delta_sec = self.seconds_duration
        dt_start = self.datetime_start
        result = dt_start + timedelta(seconds=delta_sec)
        return result

    @property
    def resample_parameter(self) -> int:
        return self.signal_frequency // self.resample_frequency

    @property
    def record_type(self) -> str:
        return 'ZXY'

    @property
    def components_index(self) -> dict:
        record_type = self.record_type
        x_component_index = record_type.index('X')
        y_component_index = record_type.index('Y')
        z_component_index = record_type.index('Z')
        return dict(zip(list('XYZ'),
            (x_component_index, y_component_index, z_component_index)))

    @property
    def short_file_info(self) -> FileInfo:
        return FileInfo(self.path, self.format_type, self.signal_frequency,
                        self.datetime_start, self.datetime_stop,
                        self.longitude, self.latitude)

    def _get_component_signal(self, component_name='Z') -> np.ndarray:
        if self.channels_count == 3:
            column_index = self.components_index[component_name]
        else:
            column_index = 3 + self.components_index[component_name]

        skip_data_size = UNSIGNED_INT_CTYPE.byte_size * \
            self.channels_count * self.start_moment
        offset_size = self.header_memory_size + skip_data_size + \
            column_index * UNSIGNED_INT_CTYPE.byte_size
        strides_size = UNSIGNED_INT_CTYPE.byte_size * self.channels_count
        signal_size = self.end_moment - self.start_moment
        with open(self.path, 'rb') as f, \
                mmap(f.fileno(), length=0, access=ACCESS_READ) as mm:
            signal_array = np.ndarray(signal_size, buffer=mm, dtype=np.int32,
                                      offset=offset_size,
                                      strides=strides_size).copy()
        return signal_array

    def _resample_signal(self, src_signal: np.ndarray) -> np.ndarray:
        if self.resample_parameter == 1:
            return src_signal
        return resampling(src_signal, self.resample_parameter)

    def read_signal(self, component='Z') -> np.ndarray:
        component = component.upper()
        if component not in self.components_index:
            raise InvalidComponentName(f'{component} not found')
        signal_array = self._get_component_signal(component_name=component)
        return self._resample_signal(src_signal=signal_array)
