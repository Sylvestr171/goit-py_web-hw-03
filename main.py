import sys
from pathlib import Path
import colorama
from threading import Thread, RLock
import logging
from time import sleep

def show_detailed_help():
    logging.info(f"Вивід детальної довідки")
    print("""
Введіть шлях до теки джерела і до теки призначення:
    Enter source directory and destination directory: <path_to_dir> <path_to_dir>
або тільки шлях до теки джерела
    "Enter source directory and destination directory: <path_to_dir>
    тоді тека призначення буде './dist'
або введіть 
    -h, --help, /?  для виводу цього повідомлення.

Аргументи:
    <path_to_dir>       Шлях до теки джерела і до теки призначення.
    -h, --help, /?      Показати це повідомлення.

Приклад:
    Enter source directory and destination directory: .\dir\ D:\path to lib\dir
""")
    
# функція для виводу короткої довідки при невідповідності параметрів
def show_short_help():
    logging.info(f"Вивід короткої довідки")
    print("""
Для отримання довідки введіть: 
    -h або --help або /?
""")

# функція для перевірки чи в аргумент передано шлях до існуючої теки
def path_validation(path_str: str) -> bool:
    logging.info(f"Перевірка шляху до джерела")
    path = Path(path_str)
    return path.is_dir()


def validation_arg(list_of_arg: list) -> tuple[Path, Path] | tuple[None, None]:
    logging.info(f"Валідація аргументів {list_of_arg}")
    path_to_destination_dir = Path('./dist') #вказуємо дефолтний шлях до папки призначення
    logging.info(f"Присвоєння дефолтне значення для папки призначення")
    if len(list_of_arg) == 2 and path_validation(list_of_arg[0]): #якщо кількість аргументів 2 перевіряємо чи вказана в першому шлях до папки джерела і чи вона існує
        logging.info(f"2 аргументи, перший, існуючий шлях до папки джерела")
        path_to_source_dir = Path(list_of_arg[0])
        path_to_destination_dir = Path(list_of_arg[1])
        print('Тека ', colorama.Fore.RED, path_to_source_dir, '\b\\', colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 1 and path_validation(list_of_arg[0]): #якщо кількість аргументів 1 перевіряємо чи це шлях до папки джерела і чи вона існує
        logging.info(f"1 аргумент, існуючий шлях до папки джерела")
        path_to_source_dir = Path(list_of_arg[0])
        print('Тека ', colorama.Fore.RED, path_to_source_dir, '\b\\', colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 1 and list_of_arg[0] in ('-h', '--help', '/?'): #перевіряємо чи аргумент не є запитом на довідку
        logging.info(f"1 аргумент, перевіряємо чи це не запит на довідку")
        show_detailed_help()
        return None, None
    elif len(list_of_arg) == 1 and not(path_validation(list_of_arg[0])): #якщо аргументом не є шлях або така тека не існує
        logging.info(f"1 аргумент з неіснуючим шляхом")
        print (colorama.Fore.RED, 'Даний шлях не існує або аргумент не є шляхом', colorama.Fore.WHITE )
        return None, None
    else:
        show_short_help()
        return None, None


lock = RLock()
#функція формування списку шляхів до папок/файлів
def iter_object_in_dir(path: Path, list_of_file: list =[], set_of_suffix: set =set()) -> tuple[list, set]:
    threads=[]
    logging.info(f"увійшли в функцію iter_object_in_dir")
    def worker(path: Path) -> None:
        nonlocal list_of_file, set_of_suffix, threads
        for i in path.iterdir():
            if i.is_file(): #перевіряємо чи об'єкт файл
                with lock:
                    list_of_file.append(i) #додаємо до списку шлях до файлу, використовуємо RLock щоб уникнути обночасного запису
                    logging.info(f"Додавання {i} в list_of_file ")
            elif i.is_dir():  #перевіряємо чи об'єкт папка
                thread = Thread (target=worker, args=(i, )) #принцип рекурсії але замість неї викликаємо новий потік
                thread.start()
                logging.info(f"Запуск потоку {thread}")
                threads.append(thread)
        for i in list_of_file:
            with lock:
                set_of_suffix.add(i.suffix)
                logging.info(f"Додавання {i} в set_of_suffix ")
    main_thread = Thread (target=worker, args=(path, ))
    main_thread.start()
    logging.info(f"Запуск main_thread")
    threads.append(main_thread)
    for t in threads:
        t.join()
        logging.info(f"Завершено {t}")
    logging.info(f"Перелік файлів: {list_of_file}\n Перелік розширень: {set_of_suffix}")
    return list_of_file, set_of_suffix

def create_folder(set_of_suffix, destination_path):
    logging.info(f"Створення папок")
    for i in set_of_suffix:
        new_folder_path=destination_path/i[1::]
        if not new_folder_path.exists():
            new_folder_path.mkdir(parents=True, exist_ok=True)
            logging.info(f'Створено теку: {new_folder_path}')
        else:
            logging.info(f'Тека вже існує: {new_folder_path}')

def move_file(list_of_path, file_suffix, path_to_destination_dir):
    logging.info(f"Start moving for {file_suffix[1::]} files")
    for i in list_of_path:
        if i.suffix == file_suffix:
            destination_path=path_to_destination_dir/file_suffix[1::]/i.name
            logging.info(f"Move {i} files to {destination_path}")
            i.rename(destination_path)
            print ("Move ", colorama.Fore.RED, i, colorama.Fore.RESET)
    logging.info(f"End moving for {file_suffix[1::]} files")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    print("Welcome!")
    while True:
        user_input = input("Enter source directory and destination directory: ")
        path_to_source_dir, path_to_destination_dir = validation_arg(user_input.split())
        if path_to_source_dir is not None and path_to_destination_dir is not None:
            lock = RLock()
            threads=[]
            list_of_file, set_of_suffix = iter_object_in_dir(path_to_source_dir)
            create_folder(set_of_suffix, path_to_destination_dir)
            for i in set_of_suffix:
                th = Thread(target=move_file, args=(list_of_file, i, path_to_destination_dir, ))
                th.start()
            break
