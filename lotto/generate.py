import os
import sys
import pandas as pd

def find_files(directory, extensions):
    """ Функция для поиска файлов с нужными расширениями """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                # Получаем относительный путь
                relative_path = os.path.relpath(os.path.join(root, file), start=os.path.dirname(sys.argv[0]))
                yield relative_path, file

def create_xls_from_folder(folder_name):
    """ Основная функция для создания xls файла """
    # Находим все файлы с расширениями .mp3 и .m4a
    files = list(find_files(folder_name, ['.mp3', '.m4a', '.mp4', '.avi', '.mkv']))

    # Создаем DataFrame
    df = pd.DataFrame({
        'Порядковый номер': range(1, len(files) + 1),
        'Имя файла': [os.path.splitext(relative_path)[0] for relative_path, _ in files]
    })

    # Создаем xls файл с именем папки
    xls_file_name = f"{folder_name}.xlsx"
    df.to_excel(xls_file_name, index=False, engine='openpyxl')
    
    print(f"Файл '{xls_file_name}' успешно сохранен.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py [название папки]")
    else:
        folder_name = sys.argv[1]
        create_xls_from_folder(folder_name)