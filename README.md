﻿﻿Данный пакет содержит основной математический и графический аппарат для
анализа и визуализации сейсмических данных

Структура пакета:
    - GeneralCalcFunctions (содержит общие функции для расчетов)
        - BandPassFilter.py - модуль с функцией полосовой фильтрации
        - CheckingName.py - модуль с функцией проверки имен файлов и каталогов
        на корректность (допустима только латиница, цифры, _ и -)
        - FindFilePath.py - модуль с функцией поиска абсолютного пути к файлу
        по каталогу, где он может лежать и его имени
        - NormingSignal.py - модуль с функцией нормировки сигнала с учетом
        коэф-тов сенсора и регистратора
    - GeneralPlottingFunctions (содержит общие модули для построения графиков)
        - histogram.py - модуль для построения гистограммы
    - HydroFracCore (содержит подпакеты для обработки только данных ГРП)
        - CalcFunctions (пакет содержит сугубо математически функции на 
        чистом Python)
             - CorrelationCalculation.py - модуль для расчета средних значений
             максимальных квадратов корреляций (на даный момент не 
             используется - заменен на Cython-функцию)
             - MomentsSelection.py - модуль для выборки номеров отсчетов
             сигналов с двух датчиков исходя из значения корреляции сигналов, а
             также разницы времени между событиями
             - PointsSelection.py - модуль с функциями для геометрической
             выборки пар датчиков
        - CythonCalcFunctions (пакет содержит функции на языке Cython и 
        python-обвязку к ним)
            - CorrelationCalculation (пакет содержит функцию и обвязку к ней
             для расчета корреляций с базовой точкой (второй этап обработки 
             ГРП))
            - MinimizationPrepear (пакет содержит функцию и обвязку к ней 
            для подготовки данных ГРП к минимазации (четвертый этап ГРП))
        - PlottingFunctions (пакет содержит функции для отрисовки графиков)
             - histograms.py  - модуль для построения гистограмм распределений
             углов и размахов задержек
    - MSICore (содежит подпакеты для обработки только данных МСИ)
        - CalcFunctions (пакет содержит сугубо математически функции)
            - AverSpectrum.py   - модуль для расчета осредненнего
            (кумулятивного спектра)
            - EnergyCalc.py     - модуль для расчета энергии спектра
            - PureSignal.py     - модуль для выделения чистого участка сигнала
            - PureSignal_experiment.py - экспериментальный модуль выделения
            чистого участка сигнала
            - Spectrogram.py    - модуль для расчета 2D-спектрограммы
            - Spectrum.py       - модуль для расчета 1D спектра сигнала
            - Wavelett.py       - модуль для проведения wavelett-трансформаций
        - PlottingFunctions (пакет служит для визуализации данных)
            - Spector.py        - модуль для построения и сохранения спектров с
            классификацией энергий (как каротаж)
            - Spectrogram.py    - модуль для построения и сохранения 2D
            спектрограммы
    - VisualFunctions (пакет с общими модулями для визуализации)
        - Colors.py -модуль для работы с цветами (перевод из RGB в HEX-формат)

# Необходимые модули
    - numpy         version 1.13.3
    - scipy         version 1.0.0
    - pywavelets    version 0.5.2
    - matplotlib    version 2.1.0

# version 0.0.0
Первая версия пакета

# version 0.0.1
Добавлен подпакет с функциями расчета данных ГРП. НО ФУНКЦИИ еще не
оттестированы!!!

# version 0.0.2
Добавлена функция проверки имени файлов и папко на допустимые символы. Функции
ГРП еще не оттестированы

# version 0.0.3
Условно оттестированы функции расчета корреляции и фильтррации значений
корреляции для ГРП. Не оттестирована функция вычисления задержек по времени

# version 0.0.4
Изменена функция генерации узлов (nodes) в модуле ГРП MomentsSelection
Создан модуль PureSignal_experiment - экспериментальный модуль выделения
чистого участка сигнала

# version 0.0.5
Убрана зависимость от пакета SeisPars.
Добавлены комментарии в модули CheckingName, NormingSignal.
Создан подпакет с общими функциями для визуализации данных
(GeneralPlottingFunctions)
В подпакете для вычислений ГРП модуль разделен на две части - выборка событий по
максимальным значениям квадратов коэф-та корреляции (MomentsSelection) и
геометрическая выборка пар датчиков (PointsSelection). В подпакет ГРП добавлен
подпакет для визуализации данных (гистограммы углов и размахов задержек)
# version 0.0.6
Изменена функция pairs_points_filtration в ГРП - добавлена опция сохранения
результатов расчетов задержек в файл Начата работа над модулем MinimizationPrep.py

# version 0.0.7
Исправлена ошибка в функции reproject_coords (ГРП) - неверно вычислялась
y-координата
Изменена функция pairs_points_filtration -
добавлена опция сохранения результатов расчетов задержек в файл

# version 0.0.8
Дополнено описание пакета
Добавлена функция вычисления средних значений максимальных квадратов корреляций
для ГРП. Очищена стуктура пакета от старых подпапкетов

# version 0.0.9
Добавлен модуль FindFilePath.py с функцией поиска абсолютного пути к файлу
Добавлены дополнительные комментарии в модули HydroFracCore

# version 0.0.10
Добавлен экспериментальный модуль на Cython CorrelationCalculation

# version 0.0.11
Удален экспериментальный модуль на Cython CorrelationCalculation

# version 0.0.12
Протестирована функция расчета корреляций для ГРП

# version 0.0.13
Оптимизирована функция расчета корреляции - переложена на Cython

# version 0.0.14
Добавлена обвязка кода Cython

# version 0.0.15
Доработана структура для хранения функций Cython

# version 0.0.16
Функция расчета корреляции для ГРП (второй этап) полностью написана на
Cython

# version 0.0.17
Исправлена ошибка в полосовом фильтре. Функция вычисления перенесена в 
GeneralCalcFunctions
Подправлена Cython-функция для расчета корреляции ГРП. Исправлен setup.py 
этой функции специально для windows

# version 0.0.18
Добавлены бинарные файлы функции CorrelationCalculation(Cython) для систем 
Windows32, Windows64, Linux32

# version 0.0.19
Изменены результаты представления данных из функций модуля PointSelection.py
. Убрана опция выгрузки данных в файл - заменено на выгрузку в виде массивов
 numpy
Исправлены функции построения гистограмм для ГРП в соответствии с тем, что 
теперь результаты возвращаются в виде массивов numpy
Изменена Cython-функция расчета корреляции - вместо списков задержек 
подается теперь numpy массив. Pyd-библиотека перекомпилирована

# version 0.0.20
Написана функция на Cython для подготовки данных к минимизации. ПОКА НЕ 
ПРОТЕСТИРОВАНА!