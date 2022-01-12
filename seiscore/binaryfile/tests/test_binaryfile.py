import os
from datetime import datetime, timedelta
from unittest.mock import Mock, PropertyMock, patch
from io import BytesIO

import pytest
from hamcrest import assert_that, equal_to
from mock_open import MockOpen

from seiscore.binaryfile.binaryfile import FileInfo
from seiscore.binaryfile.binaryfile import format_duration
from seiscore.binaryfile.binaryfile import is_binary_file_path
from seiscore.binaryfile.binaryfile import binary_read
from seiscore.binaryfile.binaryfile import get_datetime_start_baikal7
from seiscore.binaryfile.binaryfile import read_baikal7_header
from seiscore.binaryfile.binaryfile import read_baikal8_header
from seiscore.binaryfile.binaryfile import read_sigma_header
from seiscore.binaryfile.binaryfile import get_correct_resample_frequency

from seiscore.binaryfile.binaryfile import BadFilePath, InvalidResampleFrequency
from seiscore.binaryfile.binaryfile import BinaryFile

from seiscore.binaryfile.binaryfile import BAIKAL7_FMT, BAIKAL8_FMT, \
    SIGMA_FMT, BINARY_FILE_FORMATS


DEFAULT_PATH = '/some/path'


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
def test_is_binary_file_path(os_mock: Mock, is_exist, is_seismic_file,
                             expected):
    os_mock.return_value = is_exist

    folder_path = '/some/folder'
    base_filename = 'filename'
    if is_seismic_file:
        for extension in BINARY_FILE_FORMATS.values():
            full_path = os.path.join(folder_path, base_filename + f'.{extension}')
            assert is_binary_file_path(full_path) is expected
    else:
        full_path = os.path.join(folder_path, base_filename + '.qwerty')
        assert is_binary_file_path(full_path) is expected


def test_binary_read(generate_binary_lines):
    bin_fmt, c_type, expected, length = generate_binary_lines

    file_sample = BytesIO()
    file_sample.write(bin_fmt)
    assert_that(binary_read(file_sample, c_type, length), equal_to(expected))


def test_get_datetime_start_baikal7(generate_baikal7_datetime):
    time_begin, datetime_val = generate_baikal7_datetime
    expected_datetime = get_datetime_start_baikal7(time_begin)
    assert_that(expected_datetime, equal_to(datetime_val))


def test_read_baikal7_header(generate_baikal7_header):
    file_header, bin_fmt = generate_baikal7_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert_that(file_header, equal_to(read_baikal7_header(file_mock)))


def test_read_baikal8_header(generate_baikal8_header):
    file_header, bin_fmt = generate_baikal8_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert_that(file_header, equal_to(read_baikal8_header(file_mock)))


def test_read_sigma_reader(generate_sigma_header):
    file_header, bin_fmt = generate_sigma_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert_that(file_header, equal_to(read_sigma_header(file_mock)))


@pytest.mark.parametrize('signal_freq, resample_freq, expected_value',
                         [(1000, 0, 1000), (1000, 13, 1000), (1000, 10, 10)])
def test_get_correct_resample_frequency(signal_freq, resample_freq,
                                        expected_value):
    resample_freq_value = get_correct_resample_frequency(signal_freq,
                                                         resample_freq)
    assert resample_freq_value == expected_value


class TestBinaryFile:
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_not_correct_file_path(self, path_checking_mock: Mock):
        path_checking_mock.return_value = False
        try:
            BinaryFile('invalid/path')
            has_error = False
        except BadFilePath:
            has_error = True
        assert has_error is True

    @pytest.mark.parametrize(
        'resample_freq, use_avg_values, freq, expected_resample_freq',
        [(0, True, 1000, 1000), (250, False, 1000, 250)])
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_input_parameters(self, path_checking_mock: Mock, resample_freq,
                              use_avg_values, freq, expected_resample_freq):
        path_checking_mock.return_value = True
        with patch('seiscore.binaryfile.binaryfile.BinaryFile.origin_frequency',
                   new_callable=PropertyMock) as freq_property:
            freq_property.return_value = freq

            bin_file = BinaryFile('some/path', resample_freq, use_avg_values)
            assert bin_file.origin_frequency == freq
            assert bin_file.resample_frequency == expected_resample_freq
            assert bin_file.is_use_avg_values is use_avg_values

    @pytest.mark.parametrize(
        'resample_freq, use_avg_values, freq, is_bad_resample_freq',
        [(13, True, 1000, True), (-11, False, 1000, True),
         (250, True, 1000, False)])
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_resample_frequency(self, path_checking_mock: Mock,
                                resample_freq, use_avg_values, freq,
                                is_bad_resample_freq):
        path_checking_mock.return_value = True
        with patch(
                'seiscore.binaryfile.binaryfile.BinaryFile.origin_frequency',
                new_callable=PropertyMock) as freq_property:
            freq_property.return_value = freq
            try:
                BinaryFile('some/path', resample_freq, use_avg_values)
                has_error = False
            except InvalidResampleFrequency:
                has_error = True

            assert has_error is is_bad_resample_freq

    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_path(self, path_checking_mock: Mock):
        path_checking_mock.return_value = True
        file_path = '/some/path'
        bin_data = BinaryFile(file_path)
        assert bin_data.path == file_path

    @patch('seiscore.binaryfile.binaryfile.read_baikal7_header')
    @patch('seiscore.binaryfile.binaryfile.BinaryFile.format_type',
           new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test__get_file_header_baikal7(self, path_checking_mock: Mock,
                                      format_type_mock: Mock,
                                      read_header_mock: Mock):
        path_checking_mock.return_value = True
        format_type_mock.return_value = BAIKAL7_FMT
        file_path = '/some/path'

        BinaryFile(file_path)
        read_header_mock.assert_called_once_with(file_path)

    @patch('seiscore.binaryfile.binaryfile.read_baikal8_header')
    @patch('seiscore.binaryfile.binaryfile.BinaryFile.format_type',
           new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test__get_file_header_baikal8(self, path_checking_mock: Mock,
                                      format_type_mock: Mock,
                                      read_header_mock: Mock):
        path_checking_mock.return_value = True
        format_type_mock.return_value = BAIKAL8_FMT
        file_path = '/some/path'

        BinaryFile(file_path)
        read_header_mock.assert_called_once_with(file_path)

    @patch('seiscore.binaryfile.binaryfile.read_sigma_header')
    @patch('seiscore.binaryfile.binaryfile.BinaryFile.format_type',
           new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test__get_file_header_sigma(self, path_checking_mock: Mock,
                                    format_type_mock: Mock,
                                    read_header_mock: Mock):
        path_checking_mock.return_value = True
        format_type_mock.return_value = SIGMA_FMT
        file_path = '/some/path'

        BinaryFile(file_path)
        read_header_mock.assert_called_once_with(file_path)
