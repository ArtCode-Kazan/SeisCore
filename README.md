Данный пакет содержит основной математический и графический аппарат для
анализа и визуализации сейсмических данных


# Необходимые модули
    - numpy         version 1.16.3
    - scipy         version 1.2.1
    - pywavelets    version 1.0.2
    - matplotlib    version 2.1.1

# HISTORY

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

# version 0.0.21
Исправлена Cython-функция - неверно вычислялась корреляция

# version 0.0.22
Добавлены изменения в Cython-функции подготовки данных ГРП к минимазации: 
введена фильтрация по порогу корреляции. В пакет добавлены скомпилированные 
pyd-библиотеки для windows x32 и x64

# version 0.0.23
Убраны ссылки на функции из главного init файла

# version 0.0.24
Добавлен модуль для расчета минимизации ГРП

# version 0.0.25
Добавлен экспериментальная Cython-функция для подготовки данных минимизации. В
этой версии используется MinimizationPrepear_NEW

# version 0.0.26
Предварительно завершена работа над функцией минимизации для калибровки
скоростей. ТЕСТИРОВАНИЕ ЕЩЕ НЕ СДЕЛАНО.

# version 0.0.27
Добавлена модификация функции moments_selection2 в модуле MomentsSelection -
убрана завязка на квантили, квантили заменеы на значения (!!!) квантилей. Также
 возвращена Cython-функция подготовки данных к минимизации на исходную.

# version 0.0.28b
Добавлен подпакет для общих функций - GeneralFunction (не связанный с
математической обработкой, а связанный с общими процедурами над файлами). В
подпапкет скопированы мсдули CheckingName, FindFilePath, добавлена функция
cmdLogging - для вывода логированных сообщений в консоль

# version 0.0.29
Исходная версия пакета без правок в алгоритмах обработки ГРП. В функцию
минимизации координат добавлен вывод значения функции минимизации

# version 0.0.29sm2
Change the Cython function for calculating cross correlation. It's transfortm
to SelectionMoment Function.

# version 0.0.30sm2
Fix bug in CythonFunction MomentSelection

# version 0.0.31sm2
Fix bug in CythonFunction MomentSelection - add control error for calculating
correlation (divide by zero)

# version 0.0.32sm2
Change GeneralCalcFunctions and GeneralPlottingFunctions - Add general
functions for signal analysis

# version 0.0.33sm2
Change pointsSelection - add control for negative moments delay

# version 0.0.34sm2ref
Пакет находится в стадии рефакторинга

# version 0.0.35sm2ref
Изменен модуль для построения спектрограммы (убран ввод размера окна и его
сдвига. Они строго зафиксированы)

# version 0.0.36sm2ref
Изменен паттерн для проверки корректности имени папки и файла
В подпакет GeneralCalcFunctions добавлена функция вычисления энергии

# version 0.0.37sm2ref
Изменен алгоритм расчета энергии EnergyCalc (GeneralCalcFunctions) - упрощено
выделение куска анализируемого интервала частот

# version 0.0.38sm2ref
Изменен алгоритм расчета спектрограмм - добавлена возможность вывода данных 
спектроаммы для всего возможного интервала частот. Изменен модуль с 
функциями вычисления энергии - добавлены 2 способа вычисления - по площади 
под графиком спектра, по сумме квадратов амплитуд

# version 0.1.0ref
В пакет добавлен подпакет для парсинга bin-файлов

# version 0.1.1ref
В BinaryFile добавлена обработка случая, если длина сигнала не кратна 
параметру ресемплирования

# version 0.1.2ref
В BinaryFile добавлено свойство извлечение сигнала только для даты записи 
сигнала

# version 0.1.3ref
В BinaryFile исправлена ошибка вычисления начального момента выгрузки 
сигнала в случае только для текущей даты

# version 0.1.4ref
Переписана функция вычисления и построения спектрограмм в соотвествии с 
функции Matlab

# version 0.1.5ref
Исправлена исходная функция вычисления спектрограммы, переписанная функция 
Matlab упразднена

# version 0.1.6ref
В класс BinaryFile добавлено свойство, извлекающее из названия файла номер 
точки и ее атрибут

# version 0.1.7ref
В класс BinaryFile исправлено извлечение сигнала - теперь извлекается только
 четное число отсчетов
 
# version 0.1.8
Изменен класс BinaryFile - добавлены свойства read_date_time_start и 
read_date_time_stop для указания даты+времени считывания сигнала.
Изменен алгоритм минимизации скоростей и координат для расчетов ГРП - 
используется доп. библиотека PyLBFGS для ускорения расчетов

# version 0.1.9
Изменен класс BinaryFile - добавлено новое свойство - получение информации о
 заголовке каналов, а также упаковка заголовков файла в бинарный формат

# version 0.1.10
Изменен класс BinaryFile - добавлен метод для разбития файла на несколько 
файлов, если он охватывает несколько дат

# version 0.1.11
Изменен класс BinaryFile - исправлена ошибка получения номеров дискрет 
начала и окончания считывания данных

# version 0.1.12
Изменен метод расчета энергии по квадратам амплитуд - введена нормировка 
амплитуд на 10000 для избежания некорректности расчетов

# version 0.2.0
Пакет пересобран, убраны старые подпакеты для ГРП, функции перекомпанованы.

# version 0.2.1
Пакет пересобран, убраны старые подпакеты для ГРП, функции перекомпанованы.
Перекомпилирована функция ресемплирования сигнала

# version 0.2.2-3
Сделана кросc-платформенность с Windows и Linux

# version 0.2.4
Исправлены ошибки в чтении файла - установлен строгий тип массива при 
считывании np.int32, что позволило использовать новую версию numpy

# version 0.2.5
Binary class was edited. Added new property - ordered_signal_by_components.
The method return ordered signal by components - x,y,z
Edited property end moment - correct end position for reading signal

# version 0.2.6
Binary class was edited. Add new data type - HydroFrac

# version 0.2.7
Binary class was edited. Change correct condition - deleted condition with 
time duration

# version 0.2.8
Binary class was edited. Fix bug with subtraction average value from signal

# version 0.2.9
Created temporary class for reading Sigma device data

# version 0.3.0
Add new file format - Sigma (bin-file) to BinaryFile Class. Deprecated
methods in BinaryFile Class: dates, split_file_by_date

# version 0.3.1
Fix bug in Binary Class. Change reading time of recording start from
Sigma file type

# version 0.3.2
Fix bug in spectrogram module: fix bug matplotlib _tkinter.TCLError -
change matplotlib.plot backend

# version 0.3.4
Add function Wavelet detrend functions and STA/LTA filter

# version 0.3.5
Fix bug in function STA/LTA filter

# version 0.3.6
Change STA/LTA filter - function was busted

# version 0.3.7
Add new file type in BinaryFile Class - Temporary file for Baikal7 (U3, U4, etc)

# version 0.3.8
Fix bug in BinaryFile Class - Change method signals