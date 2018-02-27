a = [10, 100, 113, 30, 70, 90, 310, 350, 1000, 30, 1000, 315, 340]
moment_interval = 50

result = [a[0]]
for moment1 in a:
    is_correct = True
    for res in result:
        # получение номера левого отсчета сигнала из результативной выборки
        moment2 = res
        if abs(moment2 - moment1) < moment_interval:
            is_correct = is_correct and False
        else:
            is_correct = is_correct and True

    if is_correct is True:
        # добавление в результативную выборку, если условие соблюдено,
        # выход из вложенного цикла и переход к следующему элементу
        result.append(moment1)

print(result)
