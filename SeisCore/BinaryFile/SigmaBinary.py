import os
from datetime import datetime
from datetime import timedelta
import numpy as np
import re

from SeisCore.BinaryFile.Cython.Resampling.Execute import Resampling


class SigmaBinaryFile:
    """
    Основной (главный) класс для работы с bin-файлами
    """

    def __init__(self):
        # путь к файлу (полный) - только для вывода текста ошибок
        self.__input_path = None
        # путь к файлу (полный)
        self.__path = None
        self.__data_type = None
        # частота ресемплирования
        self.__resample_frequency = None
        # тип записи данных
        self.__record_type = None
        # boolean-параметр удаления среднего значения из каждого канала
        self.__use_avg_values = False
        # дата+время начала считывания сигнала
        self.__read_date_time_start = None
        # дата+время окончания считывания сигнала
        self.__read_date_time_stop = None
        # среднее значение по каналам
        self.__avg_value_channels = None
        self.__signal_frequency=None

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
                      '[0-9]{2,2}_[0-9]+[A-Z]*_[0-9]+[A-Z]*$'
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
        return int(round(dt * self.signal_frequency)-1)

    @property
    def signal_frequency(self):
        return self.__signal_frequency

    @signal_frequency.setter
    def signal_frequency(self, value):
        self.__signal_frequency=value

    @property
    def datetime_start(self):
        if self.path is None:
            return None
        file_name=os.path.basename(self.path)
        t=file_name.split('_')
        date_str=t[2]
        time_str=t[3][:-3]
        year_str, month_str, day_str = date_str.split('-')
        hour_str, minute_str, second_str=time_str.split('-')
        return datetime(year=int(year_str), month=int(month_str),
                        day=int(day_str), hour=int(hour_str),
                        minute=int(minute_str), second=int(second_str))

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
            if self.start_moment >= self.end_moment:
                errors.append('Неверно указаны пределы извлечения сигнала')

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
    def average_value_channels(self):
        # проверка полей класса
        is_correct, error = self.check_correct()
        if not is_correct:
            return None

        if not self.use_avg_values:
            self.__avg_value_channels = (0, 0, 0)
        else:
            if self.__avg_value_channels is None:
                # количество дискрет в одном блоке
                discrete_block_count = 3600 * self.signal_frequency

                # количество блоков для считывания
                block_count = self.discrete_amount // discrete_block_count + 1

                # список для сохранения суммы средних значений блоков сигнала
                mean_values = [0, 0, 0]

                # поблочное чтение данных файла и вычисление средних по каждому
                # каналу
                file_data = open(self.path, 'rb')
                for i in range(block_count):
                    file_data.seek(336 + i * 4 * 3 * discrete_block_count)
                    bin_data = file_data.read(4 * 3 * discrete_block_count)
                    signals = np.frombuffer(bin_data, dtype=np.int32)
                    if signals.shape[0] == 0:
                        break
                    for j in range(3):
                        channel_signal = signals[j:len(signals):3]
                        mean_value = np.mean(channel_signal)
                        mean_values[j] = mean_values[j] + mean_value
                file_data.close()

                # вычисление средних значений по каналам
                for i in range(3):
                    mean_values[i] = int(mean_values[i] / block_count)

                self.__avg_value_channels = \
                    (mean_values[0], mean_values[1], mean_values[2])
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
            bytes_count = self.start_moment * 4 * 3
            file_data.seek(336 + bytes_count)
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
                print(self.end_moment - self.start_moment + 1, signal_count)
                print('Err')
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

        #resample_signal.setflags(True)
        resample_signal = np.copy(resample_signal)
        if self.use_avg_values:
            resample_signal[:, 0] = resample_signal[:, 0] - avg_values[0]
            resample_signal[:, 1] = resample_signal[:, 1] - avg_values[1]
            resample_signal[:, 2] = resample_signal[:, 2] - avg_values[2]
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
