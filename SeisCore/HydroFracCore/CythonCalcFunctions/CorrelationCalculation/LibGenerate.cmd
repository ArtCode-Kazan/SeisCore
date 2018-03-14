python setup.py build_ext --inplace

python setup.py build_ext --inplace --compiler=mingw32

gcc -mdll -O -Wall -ID:\AppsBuilding\Venvs\venvTesting\Include -c CorrelationCalculation_win32.c

gcc -c -Ofast -ID:\AppsBuilding\Venvs\venvTesting\Include -o CorrelationCalculation_win32.o CorrelationCalculation_win32.c