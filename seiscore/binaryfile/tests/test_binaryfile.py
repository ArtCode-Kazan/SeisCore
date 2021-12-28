import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from io import BytesIO

import pytest
from hamcrest import assert_that, equal_to

from seiscore.binaryfile.binaryfile import FileInfo
from seiscore.binaryfile.binaryfile import format_duration
from seiscore.binaryfile.binaryfile import is_binary_file_path
from seiscore.binaryfile.binaryfile import binary_read


@pytest.mark.parametrize('days, hours, minutes, seconds, expected', [
    (0, 1, 2, 3, '01:02:03.000'),
    (1, 5, 6, 7, '1 days 05:06:07.000'),
    (1, 0, 0, 0, '1 days 00:00:00.000'),
    (0, 0, 0, 0, '00:00:00.000')
])
def test_format_duration(days, hours, minutes, seconds, expected):
    assert_that(format_duration(days, hours, minutes, seconds),
                equal_to(expected))


class TestFileInfo:
    @patch('seiscore.binaryfile.binaryfile.FileInfo')
    def test_name(self, file_info_mock: Mock, generate_file_info_params):
        params, base_name = generate_file_info_params
        file_info_mock.name.return_value = base_name

        f_info = FileInfo(*params)
        assert_that(f_info.name, equal_to(base_name))

    def test_duration_in_seconds(self, generate_file_info_params,
                                 generate_durations):
        params, base_name = generate_file_info_params
        for days, hours, minutes, seconds in generate_durations:
            datetime_start = datetime.now()
            duration = timedelta(days=days, hours=hours, minutes=minutes,
                                 seconds=seconds)
            datetime_stop = datetime_start + duration

            params[3:5] = [datetime_start, datetime_stop]

            expected_value = days * 3600 * 24 + hours * 3600 + \
                             minutes * 60 + seconds

            f_info = FileInfo(*params)
            assert_that(f_info.duration_in_seconds, equal_to(expected_value))

    def test_formatted_duration(self, generate_file_info_params,
                                generate_durations):
        params, _ = generate_file_info_params
        for days, hours, minutes, seconds in generate_durations:
            datetime_start = datetime.now()
            duration = timedelta(days=days, hours=hours, minutes=minutes,
                                 seconds=seconds)
            datetime_stop = datetime_start + duration
            params[3:5] = [datetime_start, datetime_stop]

            expected_value = format_duration(days, hours, minutes, seconds)

            f_info = FileInfo(*params)
            assert_that(f_info.formatted_duration, equal_to(expected_value))


@pytest.mark.parametrize('is_exist, is_seismic_file, expected',
                         [(True, True, True), (True, False, False),
                          (False, True, False), (False, False, False)])
@patch('os.path.isfile')
def test_check_binary_file_path(os_mock: Mock, is_exist, is_seismic_file,
                                expected):
    os_mock.return_value = is_exist

    folder_path = '/some/folder'
    base_filename = 'filename'
    if is_seismic_file:
        full_path = os.path.join(folder_path, base_filename + '.00')
    else:
        full_path = os.path.join(folder_path, base_filename + '.qwerty')
    assert_that(is_binary_file_path(full_path), equal_to(expected))


def test_binary_read(generate_binary_lines):
    bin_fmt, c_type, expected, length = generate_binary_lines

    file_sample = BytesIO()
    file_sample.write(bin_fmt)
    file_sample.seek(0)
    assert_that(binary_read(file_sample, c_type, length), equal_to(expected))
