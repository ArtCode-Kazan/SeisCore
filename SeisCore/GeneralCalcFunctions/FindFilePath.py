import os

def find_file_path(work_directory, file_name):
    """
    Функция для поиска полного пути к файлу в каталоге
    :param work_directory: каталог, где лежит файл
    :param file_name: имя файла + его расширение
    :return: None? если файла нет, полный абсолютный путь, если файл найден
    """
    folder_structure=os.walk(work_directory)
    result = None
    for root_folder, folders, files in folder_structure:
        if file_name in files:
            result=os.path.join(root_folder,file_name)
            break
    return result
