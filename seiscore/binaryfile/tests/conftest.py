import os
from random import randint
from typing import Tuple, List
from datetime import datetime, timedelta
from itertools import permutations
import struct

import pytest

from seiscore.binaryfile.binaryfile import CHAR_CTYPE, DOUBLE_CTYPE, \
    UNSIGNED_SHORT_CTYPE, UNSIGNED_INT_CTYPE, UNSIGNED_LONG_LONG_CTYPE


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
        expected = (0, 1, 10, 100, 65535)
        bin_fmt = struct.pack(f'{len(expected)}H', *expected)
    elif c_type == UNSIGNED_INT_CTYPE:
        expected = (0, 1, 100, 1000, 4294967295)
        bin_fmt = struct.pack(f'{len(expected)}I', *expected)
    elif c_type == DOUBLE_CTYPE:
        expected = (-1e10, -1, 0, 1, 1e10)
        bin_fmt = struct.pack(f'{len(expected)}d', *expected)
    elif c_type == UNSIGNED_LONG_LONG_CTYPE:
        expected = (0, 1, 1000, 12456, 18446744073709551615)
        bin_fmt = struct.pack(f'{len(expected)}Q', *expected)
    else:
        raise Exception('Invalid C type parameter')

    return bin_fmt, c_type, expected, len(expected)
