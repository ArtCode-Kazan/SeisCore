import os
from datetime import datetime, timedelta
from unittest.mock import Mock, PropertyMock, patch
from io import BytesIO

import pytest
from hamcrest import assert_that, equal_to
from mock_open import MockOpen

from seiscore.binaryfile.binaryfile import FileInfo, FileHeader
from seiscore.binaryfile.binaryfile import format_duration
from seiscore.binaryfile.binaryfile import is_binary_file_path
from seiscore.binaryfile.binaryfile import binary_read
from seiscore.binaryfile.binaryfile import get_datetime_start_baikal7
from seiscore.binaryfile.binaryfile import read_baikal7_header
from seiscore.binaryfile.binaryfile import read_baikal8_header
from seiscore.binaryfile.binaryfile import read_sigma_header

from seiscore.binaryfile.binaryfile import BadFilePath
from seiscore.binaryfile.binaryfile import InvalidResampleFrequency
from seiscore.binaryfile.binaryfile import InvalidDateTimeValue
from seiscore.binaryfile.binaryfile import BinaryFile

from seiscore.binaryfile.binaryfile import (BAIKAL7_FMT, BAIKAL8_FMT,
                                            SIGMA_FMT, BINARY_FILE_FORMATS)
from seiscore.binaryfile.binaryfile import SIGMA_SECONDS_OFFSET
from seiscore.binaryfile.binaryfile import COMPONENTS_ORDER

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
        assert f_info.name == base_name

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
            assert f_info.duration_in_seconds == expected_value

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
            assert f_info.formatted_duration == expected_value


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
            full_path = os.path.join(folder_path,
                                     base_filename + f'.{extension}')
            assert is_binary_file_path(full_path) is expected
    else:
        full_path = os.path.join(folder_path, base_filename + '.qwerty')
        assert is_binary_file_path(full_path) is expected


def test_binary_read(generate_binary_lines):
    bin_fmt, c_type, expected, length = generate_binary_lines

    file_sample = BytesIO()
    file_sample.write(bin_fmt)
    assert binary_read(file_sample, c_type, length) == expected


def test_get_datetime_start_baikal7(generate_baikal7_datetime):
    time_begin, datetime_val = generate_baikal7_datetime
    expected_datetime = get_datetime_start_baikal7(time_begin)
    assert expected_datetime == datetime_val


def test_read_baikal7_header(generate_baikal7_header):
    file_header, bin_fmt = generate_baikal7_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert file_header == read_baikal7_header(file_mock)


def test_read_baikal8_header(generate_baikal8_header):
    file_header, bin_fmt = generate_baikal8_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert file_header == read_baikal8_header(file_mock)


def test_read_sigma_reader(generate_sigma_header):
    file_header, bin_fmt = generate_sigma_header

    file_mock = MockOpen(read_data=bin_fmt)
    with patch('builtins.open', file_mock):
        assert file_header == read_sigma_header(file_mock)


class TestBinaryFile:
    default_path = '/some/path'

    @patch('seiscore.binaryfile.binaryfile.read_baikal7_header')
    @patch.object(BinaryFile, 'format_type', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_get_file_header_baikal7(self, check_path_mock: Mock,
                                     format_type_mock: Mock,
                                     reader_mock: Mock):
        check_path_mock.return_value = True
        format_type_mock.return_value = BAIKAL7_FMT

        BinaryFile(self.default_path)
        reader_mock.assert_called_once_with(self.default_path)

    @patch('seiscore.binaryfile.binaryfile.read_baikal8_header')
    @patch.object(BinaryFile, 'format_type', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_get_file_header_baikal8(self, check_path_mock: Mock,
                                     format_type_mock: Mock,
                                     reader_mock: Mock):
        check_path_mock.return_value = True
        format_type_mock.return_value = BAIKAL8_FMT

        BinaryFile(self.default_path)
        reader_mock.assert_called_once_with(self.default_path)

    @patch('seiscore.binaryfile.binaryfile.read_sigma_header')
    @patch.object(BinaryFile, 'format_type', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_get_file_header_sigma(self, check_path_mock: Mock,
                                   format_type_mock: Mock,
                                   reader_mock: Mock):
        check_path_mock.return_value = True
        format_type_mock.return_value = SIGMA_FMT

        BinaryFile(self.default_path)
        reader_mock.assert_called_once_with(self.default_path)

    @patch('seiscore.binaryfile.binaryfile.read_sigma_header')
    @patch('seiscore.binaryfile.binaryfile.read_baikal8_header')
    @patch('seiscore.binaryfile.binaryfile.read_baikal7_header')
    @patch.object(BinaryFile, 'format_type', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_get_file_header_unknown(self, check_path_mock: Mock,
                                     format_type_mock: Mock,
                                     reader_baikal7_mock: Mock,
                                     reader_baikal8_mock: Mock,
                                     reader_sigma_mock: Mock):
        check_path_mock.return_value = True
        format_type_mock.return_value = None

        BinaryFile(self.default_path)
        reader_baikal7_mock.assert_not_called()
        reader_baikal8_mock.assert_not_called()
        reader_sigma_mock.assert_not_called()

    @pytest.mark.parametrize(
        'origin_freq, input_value, is_correct, resample_value',
        [(100, 25, True, 25), (100, 0, True, 100),
         (100, 26, False, 0), (100, -250, False, 0)])
    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_is_correct_resample_frequency(self, path_checking_mock: Mock,
                                           origin_frequency_mock: Mock,
                                           origin_freq, input_value,
                                           is_correct, resample_value):
        path_checking_mock.return_value = True
        origin_frequency_mock.return_value = origin_freq
        try:
            bin_data = BinaryFile(self.default_path,
                                  resample_frequency=input_value)
            assert bin_data.resample_frequency == resample_value
            is_success = True
        except InvalidResampleFrequency:
            is_success = False
        assert is_success is is_correct

    @pytest.mark.parametrize('filename, extension',
                             [('f1.00', '00'), ('f2.xx', 'xx'),
                              ('f3.bin', 'bin')])
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_file_extension(self, path_checking_mock: Mock, filename,
                            extension):
        path_checking_mock.return_value = True
        path = os.path.join('/some/folder', filename)
        bin_data = BinaryFile(path)
        assert bin_data.file_extension == extension

    @pytest.mark.parametrize('filename, extension',
                             [('f1.00', '00'), ('f2.xx', 'xx'),
                              ('f3.bin', 'bin')])
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_create_unique_file_name(self, path_checking_mock: Mock,
                                     get_file_header_mock: Mock,
                                     filename, extension):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        path = os.path.join('/some/folder', filename)
        bin_data = BinaryFile(path)
        unique_filename = bin_data.unique_file_name
        base_name, extension_val = unique_filename.split('.')
        assert extension_val == extension

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_path(self, path_checking_mock: Mock, get_file_header_mock: Mock):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        bin_data = BinaryFile(self.default_path)
        assert self.default_path == bin_data.path

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_file_header(self, path_checking_mock: Mock,
                         get_file_header_mock: Mock):
        file_header_mock_value = 'file-header-mock'
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header_mock_value
        bin_data = BinaryFile(self.default_path)
        assert bin_data.file_header == file_header_mock_value

    @pytest.mark.parametrize('is_use', [True, False])
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_is_use_avg_values(self, path_checking_mock: Mock,
                               get_file_header_mock: Mock, is_use):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        bin_data = BinaryFile(self.default_path, is_use_avg_values=is_use)
        assert bin_data.is_use_avg_values is is_use

    @pytest.mark.parametrize('frequency', [1, 10, 1000])
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_origin_frequency(self, path_checking_mock: Mock,
                              get_file_header_mock: Mock, frequency):
        path_checking_mock.return_value = True
        file_header = FileHeader(3, frequency, datetime.now(), 1, 2)
        get_file_header_mock.return_value = file_header
        bin_data = BinaryFile(self.default_path)
        assert bin_data.origin_frequency == frequency

    @pytest.mark.parametrize(
        'resample_freq, origin_freq, expect_resample_freq',
        [(0, 1000, 1000), (1, 1000, 1), (10, 1000, 10), (100, 1000, 100)])
    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_resample_frequency(self, path_checking_mock: Mock,
                                get_file_header_mock: Mock,
                                origin_frequency_mock: Mock,
                                resample_freq, origin_freq,
                                expect_resample_freq):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        origin_frequency_mock.return_value = origin_freq

        bin_data = BinaryFile(self.default_path, resample_freq)
        assert bin_data.resample_frequency == expect_resample_freq

    @pytest.mark.parametrize(
        'extension, expect_format_type',
        [(x[1], x[0]) for x in BINARY_FILE_FORMATS.items()])
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_format_type(self, path_checking_mock: Mock,
                         get_file_header_mock: Mock,
                         extension, expect_format_type):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        default_folder = '/some/folder'
        filename = f'file.{extension}'
        path = os.path.join(default_folder, filename)
        bin_data = BinaryFile(path)
        assert bin_data.format_type == expect_format_type

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_resample_frequency(self, path_checking_mock: Mock,
                                get_file_header_mock: Mock):
        expected_datetime = datetime.now()
        file_header = FileHeader(3, 1000, expected_datetime, 0, 0)

        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header

        bin_data = BinaryFile(self.default_path)
        assert bin_data.origin_datetime_start == expected_datetime

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_channels_count(self, path_checking_mock: Mock,
                            get_file_header_mock: Mock):
        expected_count = 3
        file_header = FileHeader(expected_count, 1000, datetime.now(), 0, 0)

        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header

        bin_data = BinaryFile(self.default_path)
        assert bin_data.channels_count == expected_count

    @pytest.mark.parametrize('channels_count, expected_memory_size',
                             [(3, 336), (6, 552)])
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_header_memory_size(self, path_checking_mock: Mock,
                                get_file_header_mock: Mock,
                                channels_count, expected_memory_size):
        file_header = FileHeader(channels_count, 1000, datetime.now(), 0, 0)

        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header

        bin_data = BinaryFile(self.default_path)
        assert bin_data.header_memory_size == expected_memory_size

    @pytest.mark.parametrize('file_size, channels_count, '
                             'expected_discrete_count',
                             [(15144, 3, 1234), (336, 3, 0)])
    @patch('os.path.getsize')
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_discrete_amount(self, path_checking_mock: Mock,
                             get_file_header_mock: Mock,
                             os_mock: Mock,
                             file_size, channels_count,
                             expected_discrete_count):
        file_header = FileHeader(channels_count, 1000, datetime.now(), 0, 0)

        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header
        os_mock.return_value = file_size

        bin_data = BinaryFile(self.default_path)
        assert bin_data.discrete_amount == expected_discrete_count

    @pytest.mark.parametrize('discrete_count, frequency, expected_duration',
                             [(1000, 100, 10), (0, 1000, 0),
                              (1001, 100, 10.01)])
    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'discrete_amount', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_seconds_duration(self, path_checking_mock: Mock,
                              get_file_header_mock: Mock,
                              discrete_amount_mock: Mock,
                              origin_frequency_mock: Mock,
                              discrete_count, frequency, expected_duration):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        discrete_amount_mock.return_value = discrete_count
        origin_frequency_mock.return_value = frequency

        bin_data = BinaryFile(self.default_path)
        assert bin_data.seconds_duration == expected_duration

    @patch.object(BinaryFile, 'origin_datetime_start',
                  new_callable=PropertyMock)
    @patch.object(BinaryFile, 'seconds_duration', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_origin_datetime_stop(self, path_checking_mock: Mock,
                                  get_file_header_mock: Mock,
                                  seconds_duration_mock: Mock,
                                  origin_datetime_start_mock: Mock):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        start_datetime = datetime.now()
        stop_datetime = start_datetime + timedelta(
            hours=1, minutes=10, seconds=27, microseconds=108)
        seconds_diff = (stop_datetime - start_datetime).total_seconds()
        seconds_duration_mock.return_value = seconds_diff
        origin_datetime_start_mock.return_value = start_datetime

        bin_data = BinaryFile(self.default_path)
        assert bin_data.origin_datetime_stop == stop_datetime

    @pytest.mark.parametrize('file_format',
                             [x for x in BINARY_FILE_FORMATS.values()])
    @patch.object(BinaryFile, 'seconds_duration', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'origin_datetime_start',
                  new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_datetime_start_stop(self, path_checking_mock: Mock,
                                 get_file_header_mock: Mock,
                                 origin_datetime_start_mock: Mock,
                                 seconds_duration_mock: Mock, file_format):
        duration_sec = 60
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        start_datetime = datetime.now()
        origin_datetime_start_mock.return_value = start_datetime
        seconds_duration_mock.return_value = duration_sec
        if file_format == SIGMA_FMT:
            expected_start_datetime = start_datetime + timedelta(
                seconds=SIGMA_SECONDS_OFFSET)
        else:
            expected_start_datetime = start_datetime
        expected_stop_datetime = expected_start_datetime + timedelta(
            seconds=duration_sec)

        bin_data = BinaryFile(self.default_path)
        assert bin_data.datetime_start == expected_start_datetime
        assert bin_data.datetime_stop == expected_stop_datetime

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_datetime_longitude_latitude(self, path_checking_mock: Mock,
                                         get_file_header_mock: Mock):
        longitude, latitude = -1.234567, 7.654321
        file_header = FileHeader(3, 1000, datetime.now(), longitude,
                                 latitude)
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = file_header

        bin_data = BinaryFile(self.default_path)
        assert bin_data.longitude == longitude
        assert bin_data.latitude == latitude

    @patch.object(BinaryFile, 'datetime_stop', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_start', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_read_datetime_start(self, path_checking_mock: Mock,
                                 get_file_header_mock: Mock,
                                 datetime_start_mock: Mock,
                                 datetime_stop_mock: Mock,
                                 generate_datetime):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        for start_datetime, stop_datetime, start_read_datetime in \
                generate_datetime:
            datetime_start_mock.return_value = start_datetime
            datetime_stop_mock.return_value = stop_datetime

            bin_data = BinaryFile(self.default_path)
            try:
                bin_data.read_date_time_start = start_read_datetime
                has_error = False
            except InvalidDateTimeValue:
                has_error = True

            if start_datetime <= start_read_datetime < stop_datetime:
                assert has_error is False
                assert bin_data.read_date_time_start == start_read_datetime
            else:
                assert has_error is True
                assert bin_data.read_date_time_start == start_datetime

    @patch.object(BinaryFile, 'datetime_stop', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_start', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_read_datetime_stop(self, path_checking_mock: Mock,
                                get_file_header_mock: Mock,
                                datetime_start_mock: Mock,
                                datetime_stop_mock: Mock,
                                generate_datetime):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        for start_datetime, stop_datetime, stop_read_datetime in \
                generate_datetime:
            datetime_start_mock.return_value = start_datetime
            datetime_stop_mock.return_value = stop_datetime

            bin_data = BinaryFile(self.default_path)
            try:
                bin_data.read_date_time_stop = stop_read_datetime
                has_error = False
            except InvalidDateTimeValue:
                has_error = True

            if start_datetime < stop_read_datetime <= stop_datetime:
                assert has_error is False
                assert bin_data.read_date_time_stop == stop_read_datetime
            else:
                assert has_error is True
                assert bin_data.read_date_time_stop == stop_datetime

    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_stop', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_start', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_start_moment(self, path_checking_mock: Mock,
                          get_file_header_mock: Mock,
                          datetime_start_mock: Mock,
                          datetime_stop_mock: Mock,
                          origin_freq_mock: Mock, generate_datetime):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        for start_datetime, stop_datetime, start_read_datetime in \
                generate_datetime:
            if not start_datetime <= start_read_datetime < stop_datetime:
                continue

            datetime_start_mock.return_value = start_datetime
            datetime_stop_mock.return_value = stop_datetime
            origin_freq_mock.return_value = 1000

            bin_data = BinaryFile(self.default_path)
            bin_data.read_date_time_start = start_read_datetime

            diff_total = (stop_datetime - start_datetime).total_seconds()
            total_discrete_count = int(round(diff_total *
                                             bin_data.origin_frequency))

            dt_diff = (stop_datetime - start_read_datetime).total_seconds()
            discrete_count = int(round(dt_diff * bin_data.origin_frequency))

            start_discrete_index = total_discrete_count - discrete_count
            assert bin_data.start_moment == start_discrete_index

    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_stop', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_start', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_end_moment(self, path_checking_mock: Mock,
                        get_file_header_mock: Mock,
                        datetime_start_mock: Mock,
                        datetime_stop_mock: Mock,
                        origin_frequency_mock: Mock, generate_datetime):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        for start_datetime, stop_datetime, stop_read_datetime in \
                generate_datetime:
            if not start_datetime < stop_read_datetime <= stop_datetime:
                continue

            datetime_start_mock.return_value = start_datetime
            datetime_stop_mock.return_value = stop_datetime
            origin_frequency_mock.return_value = 1000

            bin_data = BinaryFile(self.default_path)
            bin_data.read_date_time_stop = stop_read_datetime

            diff_total = (stop_datetime - start_datetime).total_seconds()
            total_discrete_count = int(round(diff_total *
                                             bin_data.origin_frequency))

            dt_diff = (stop_datetime - stop_read_datetime).total_seconds()
            discrete_count = int(round(dt_diff * bin_data.origin_frequency))

            stop_discrete_index = total_discrete_count - discrete_count
            assert bin_data.end_moment == stop_discrete_index

    @pytest.mark.parametrize('origin_frequency, resample_frequency, '
                             'resample_parameter',
                             [(1000, 0, 1), (1000, 250, 4), (1000, 500, 2)])
    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_resample_parameter(self, path_checking_mock: Mock,
                                get_file_header_mock: Mock,
                                origin_frequency_mock: Mock,
                                origin_frequency, resample_frequency,
                                resample_parameter):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        origin_frequency_mock.return_value = origin_frequency

        bin_data = BinaryFile(self.default_path, resample_frequency)
        assert bin_data.resample_parameter == resample_parameter

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_record_type(self, path_checking_mock: Mock,
                         get_file_header_mock: Mock, ):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None
        assert BinaryFile(self.default_path).record_type == COMPONENTS_ORDER

    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_components_index(self, path_checking_mock: Mock,
                              get_file_header_mock: Mock):
        path_checking_mock.return_value = True
        get_file_header_mock.return_value = None

        bin_data = BinaryFile(self.default_path)
        for i, component in enumerate(bin_data.record_type):
            assert i == bin_data.components_index[component]

    @patch.object(BinaryFile, 'latitude', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'longitude', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_stop', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'datetime_start', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'origin_frequency', new_callable=PropertyMock)
    @patch.object(BinaryFile, 'format_type', new_callable=PropertyMock)
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    def test_short_file_info(self, path_checking_mock: Mock,
                             format_type_mock: Mock,
                             origin_frequency_mock: Mock,
                             datetime_start_mock: Mock,
                             datetime_stop_mock: Mock,
                             longitude_mock: Mock, latitude_mock: Mock,
                             generate_baikal7_header):
        expected_file_info = FileInfo(self.default_path, 'qwerty', 1000,
                                      datetime.now(), datetime.now(),
                                      -1000, 100)

        path_checking_mock.return_value = True
        format_type_mock.return_value = expected_file_info.format_type
        origin_frequency_mock.return_value = expected_file_info.frequency
        datetime_start_mock.return_value = expected_file_info.time_start
        datetime_stop_mock.return_value = expected_file_info.time_stop
        longitude_mock.return_value = expected_file_info.longitude
        latitude_mock.return_value = expected_file_info.latitude

        bin_data = BinaryFile(self.default_path)
        assert bin_data.short_file_info == expected_file_info

    @patch.object(BinaryFile, 'discrete_amount', new_callable=PropertyMock)
    @patch.object(BinaryFile, '_BinaryFile__get_file_header')
    @patch('seiscore.binaryfile.binaryfile.is_binary_file_path')
    @pytest.mark.parametrize('component', ['X', 'Y', 'Z'])
    def test_get_component_signal(self,  path_checking_mock: Mock,
                                  file_header_mock: Mock,
                                  discrete_amount_mock: Mock,
                                  component: str,
                                  generate_baikal7_file):
        file_header, values, bin_fmt = generate_baikal7_file

        path_checking_mock.return_value = True
        file_header_mock.return_value = file_header
        discrete_amount_mock.return_value = values.shape[0]

        file_sample = BytesIO()
        file_sample.write(bin_fmt)

        file_mock = MockOpen(read_data=file_sample)
        with patch('builtins.open', file_mock):
            bin_data = BinaryFile(self.default_path)
            print(bin_data.file_header)
            print(bin_data._get_component_signal('X'))
