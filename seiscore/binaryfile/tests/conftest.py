import os
import random
from random import randint
from typing import Tuple, List
from datetime import datetime, timedelta
from itertools import permutations
import struct

import numpy as np
import pytest

from seiscore.binaryfile.binaryfile import (
    CHAR_CTYPE, DOUBLE_CTYPE, UNSIGNED_SHORT_CTYPE, UNSIGNED_INT_CTYPE,
    UNSIGNED_LONG_LONG_CTYPE
)

from seiscore.binaryfile.binaryfile import get_datetime_start_baikal7
from seiscore.binaryfile.binaryfile import FileHeader

from seiscore.binaryfile.tests.helpers import create_latitude_str
from seiscore.binaryfile.tests.helpers import create_longitude_str

from seiscore.binaryfile.tests.helpers import add_microseconds


def generate_word() -> str:
    length = 10
    return ''.join((chr(randint(97, 122)) for _ in range(length)))


@pytest.fixture
def generate_path_with_base_name() -> Tuple[str, str]:
    entering_size = 5
    folders = [generate_word() for _ in range(entering_size)]
    folders[-1] += '.xx'
    return os.path.join(*folders), folders[-1]


@pytest.fixture
def generate_file_info_params(generate_path_with_base_name):
    path, base_name = generate_path_with_base_name
    format_type = base_name.split('.')[-1]
    frequency = 1000
    time_start = datetime.now()
    time_stop = time_start + timedelta(hours=5)
    longitude, latitude = -50.45, 85.56
    return [path, format_type, frequency, time_start, time_stop, longitude,
            latitude], base_name


@pytest.fixture
def generate_durations() -> List[Tuple[int, int, int, int]]:
    # days, hours, minutes, seconds
    variants = [(0, 0, 0, 0), (1, 2, 3, 4)]
    for i in range(1, 4):
        sample = [0] * (4 - i) + [x + 1 for x in range(i)]
        variants += list(set(permutations(sample)))
    return variants


@pytest.fixture(params=(CHAR_CTYPE, UNSIGNED_SHORT_CTYPE, UNSIGNED_INT_CTYPE,
                        DOUBLE_CTYPE, UNSIGNED_LONG_LONG_CTYPE))
def generate_binary_lines(request):
    c_type = request.param
    if c_type == CHAR_CTYPE:
        expected = 'qwerty'
        bin_fmt = struct.pack(f'{len(expected)}s', expected.encode())
    elif c_type == UNSIGNED_SHORT_CTYPE:
        expected = [0, 1, 10, 100, 65535]
        bin_fmt = struct.pack(f'{len(expected)}H', *expected)
    elif c_type == UNSIGNED_INT_CTYPE:
        expected = [0, 1, 100, 1000, 4294967295]
        bin_fmt = struct.pack(f'{len(expected)}I', *expected)
    elif c_type == DOUBLE_CTYPE:
        expected = [-1e10, -1, 0, 1, 1e10]
        bin_fmt = struct.pack(f'{len(expected)}d', *expected)
    elif c_type == UNSIGNED_LONG_LONG_CTYPE:
        expected = [0, 1, 1000, 12456, 18446744073709551615]
        bin_fmt = struct.pack(f'{len(expected)}Q', *expected)
    else:
        raise Exception('Invalid C type parameter')

    return bin_fmt, c_type, expected, len(expected)


@pytest.fixture(params=[datetime(1980, 1, 1, 0, 0, 0),
                        datetime(2000, 1, 2, 3, 4, 5),
                        datetime(2022, 12, 31, 23, 59, 59)])
def generate_baikal7_datetime(request):
    const_datetime = datetime(1980, 1, 1, 0, 0, 0)
    datetime_val = request.param

    seconds_count = (datetime_val - const_datetime).total_seconds()
    time_begin = seconds_count * 256_000_000
    return time_begin, datetime_val


@pytest.fixture
def generate_baikal7_header():
    channel_count = 3
    frequency = random.randint(1, 10000)
    latitude = random.randint(-9900, 9900) / 100
    longitude = random.randint(-9900, 9900) / 100
    time_begin = random.randint(0, int(1e10))

    bin_fmt = struct.pack('H', channel_count)
    bin_fmt += struct.pack('10H', *[0] * 10)
    bin_fmt += struct.pack('H', frequency)
    bin_fmt += struct.pack('24H', *[0] * 24)
    bin_fmt += struct.pack('2d', latitude, longitude)
    bin_fmt += struct.pack('8H', *[0] * 8)
    bin_fmt += struct.pack('1Q', time_begin)

    datetime_start = get_datetime_start_baikal7(time_begin)
    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude), bin_fmt


@pytest.fixture
def generate_baikal8_header():
    channel_count = 3

    datetime_start = datetime.now()
    day = datetime_start.day
    month = datetime_start.month
    year = datetime_start.year

    day_start = datetime_start.replace(hour=0, minute=0, second=0,
                                       microsecond=0)
    seconds = (datetime_start - day_start).total_seconds()

    frequency = randint(1, 10000)
    dt = 1 / frequency
    latitude = random.randint(-9900, 9900) / 100
    longitude = random.randint(-9900, 9900) / 100

    bin_fmt = struct.pack('H', channel_count)
    bin_fmt += struct.pack('2H', 0, 0)
    bin_fmt += struct.pack('3H', day, month, year)
    bin_fmt += struct.pack('18H', *[0] * 18)
    bin_fmt += struct.pack('2d', dt, seconds)
    bin_fmt += struct.pack('d', 0)
    bin_fmt += struct.pack('2d', latitude, longitude)
    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude), bin_fmt


@pytest.fixture
def generate_sigma_header():
    channel_count = 3
    frequency = random.randint(1, 10000)
    latitude = random.randint(1, 9900) / 100
    lat_str = create_latitude_str(latitude)

    longitude = random.randint(1, 9900) / 100
    long_str = create_longitude_str(longitude)

    datetime_start = datetime.now()
    datetime_start = datetime_start.replace(microsecond=0)
    year = datetime_start.year
    month = datetime_start.month
    day = datetime_start.day
    date_as_int = int(str(year)[2:] + str(month).zfill(2) + str(day).zfill(2))

    hour_str = str(datetime_start.hour).zfill(2)
    minute_str = str(datetime_start.minute).zfill(2)
    seconds = str(datetime_start.second).zfill(2)
    time_as_int = int(hour_str + minute_str + seconds)

    bin_fmt = struct.pack('6H', *[0] * 6)
    bin_fmt += struct.pack('I', channel_count)
    bin_fmt += struct.pack('4H', *[0] * 4)
    bin_fmt += struct.pack('I', frequency)
    bin_fmt += struct.pack('6H', *[0] * 6)
    bin_fmt += struct.pack('8s9s', lat_str.encode(), long_str.encode())
    bin_fmt += struct.pack('3s', '   '.encode())
    bin_fmt += struct.pack('I', date_as_int)
    bin_fmt += struct.pack('I', time_as_int)

    return FileHeader(channel_count, frequency, datetime_start, longitude,
                      latitude), bin_fmt


@pytest.fixture
def generate_datetime():
    mid_datetime = add_microseconds(datetime.now(), frequency=1000)
    dataset = [
        (mid_datetime, mid_datetime + timedelta(5),
         mid_datetime),
        (mid_datetime, mid_datetime + timedelta(5),
         mid_datetime + timedelta(5))
    ]
    for i in range(1000):
        start_offset = timedelta(*[randint(-10, -1) for _ in range(4)])
        stop_offset = timedelta(*[randint(1, 10) for _ in range(4)])
        read_offset = timedelta(*[randint(-10, 10) for _ in range(4)])

        start_datetime = add_microseconds(mid_datetime + start_offset,
                                          frequency=1000)
        stop_datetime = add_microseconds(mid_datetime + stop_offset,
                                         frequency=1000)
        read_datetime = add_microseconds(mid_datetime + read_offset,
                                         frequency=1000)

        dataset.append((start_datetime, stop_datetime, read_datetime))
    return dataset


@pytest.fixture
def generate_baikal7_file(generate_baikal7_header):
    file_header, header_bin_fmt = generate_baikal7_header

    channels_header_size = 72 * file_header.channel_count
    zeros_count = int(channels_header_size / UNSIGNED_SHORT_CTYPE.byte_size)
    channels_bin_fmt = struct.pack(f'{zeros_count}H', *[0] * zeros_count)

    values = np.random.randint(-1000, 1000, size=(10_000, 3), dtype=np.int32)
    bin_fmt = header_bin_fmt + channels_bin_fmt + values.tobytes()
    return file_header, values, bin_fmt
