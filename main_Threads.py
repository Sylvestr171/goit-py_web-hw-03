"Модуля 3. Д/з 1 Багатопотоковість"

from pathlib import Path
from threading import Thread, RLock, Semaphore
import logging
import colorama


def show_detailed_help() -> None:

    "Функція виводу детальної довідки"

    logging.info("Вивід детальної довідки")
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
    Enter source directory and destination directory: ./dir/ D:/path to lib/dir 
""")

# функція для виводу короткої довідки при невідповідності параметрів
def show_short_help():

    "Функція виводу короткої довідки"

    logging.info("Вивід короткої довідки")
    print("""
Для отримання довідки введіть: 
    -h або --help або /?
""")


def path_validation(path_str: str) -> bool:

    "Функція для перевірки чи в аргумент передано шлях до існуючої теки"

    logging.info("Перевірка шляху до джерела")
    path = Path(path_str)
    return path.is_dir()


def validation_arg(list_of_arg: list) -> tuple[Path, Path] | tuple[None, None]:

    "Функція валідації і розбору введених користувачем аргументів"

    logging.info("Валідація аргументів %s", list_of_arg)
    path_to_destination_dir = Path('./dist') #вказуємо дефолтний шлях до папки призначення
    logging.info("Присвоєння дефолтне значення для папки призначення")
    if len(list_of_arg) == 2 and path_validation(list_of_arg[0]):
        #якщо кількість аргументів 2 перевіряємо чи вказана в
        # першому шлях до папки джерела і чи вона існує
        logging.info("2 аргументи, перший, існуючий шлях до папки джерела")
        path_to_source_dir = Path(list_of_arg[0])
        path_to_destination_dir = Path(list_of_arg[1])
        print('Тека ', colorama.Fore.RED, \
               path_to_source_dir, '\b\\', colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 1 \
          and path_validation(list_of_arg[0]): \
              #якщо кількість аргументів 1 перевіряємо чи це шлях до папки джерела і чи вона існує
        logging.info("1 аргумент, існуючий шлях до папки джерела")
        path_to_source_dir = Path(list_of_arg[0])
        print('Тека ',
              colorama.Fore.RED, path_to_source_dir, '\b\\',
              colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 1 and list_of_arg[0] \
        in ('-h', '--help', '/?'): #перевіряємо чи аргумент не є запитом на довідку
        logging.info("1 аргумент, перевіряємо чи це не запит на довідку")
        show_detailed_help()
        return None, None
    elif len(list_of_arg) == 1 and not(
        path_validation(list_of_arg[0])
        ): #якщо аргументом не є шлях або така тека не існує
        logging.info("1 аргумент з неіснуючим шляхом")
        print (colorama.Fore.RED, \
               'Даний шлях не існує або аргумент не є шляхом', colorama.Fore.WHITE )
        return None, None
    else:
        show_short_help()
        return None, None


lock = RLock()

def iter_object_in_dir(path: Path,
                       list_of_file: list =[],
                       set_of_suffix: set =set()
                       ) -> tuple[list, set]:

    "Функція формування списку шляхів до папок/файлів"

    threads_for_dir=[]
    logging.info("увійшли в функцію iter_object_in_dir")
    pool_for_iter_object_in_dir=Semaphore(2)
    def worker(pool_for_worker: Semaphore, path: Path) -> None:
        nonlocal list_of_file, set_of_suffix, threads_for_dir
        for i in path.iterdir():
            if i.is_file(): #перевіряємо чи об'єкт файл
                with lock:
                    list_of_file.append(i)
                    #додаємо до списку шлях до файлу,
                    # використовуємо RLock щоб уникнути обночасного запису
                    logging.info("Додавання %s в list_of_file ", i)
            elif i.is_dir():  #перевіряємо чи об'єкт папка
                thread = Thread (target=worker, args=(pool_for_worker ,i, ))
                #принцип рекурсії але замість неї викликаємо новий потік
                thread.start()
                logging.info("Запуск потоку %s", thread)
                threads_for_dir.append(thread)
        for i in list_of_file:
            with lock:
                set_of_suffix.add(i.suffix)
                logging.info("Додавання %s в set_of_suffix ", i)
    main_thread = Thread (target=worker, args=(pool_for_iter_object_in_dir, path, ))
    main_thread.start()
    logging.info("Запуск main_thread")
    threads_for_dir.append(main_thread)
    for t in threads_for_dir:
        t.join()
        logging.info("Завершено %s", t)
    logging.info("Перелік файлів: %s ", list_of_file)
    logging.info("Перелік розширень: %s", set_of_suffix)
    return list_of_file, set_of_suffix

def create_folder(set_of_suffix_in_func: set, destination_path: Path) -> None:

    "Функція створення каталогів"

    logging.info("Створення папок")
    for i in set_of_suffix_in_func:
        new_folder_path=destination_path/i[1::]
        if not new_folder_path.exists():
            new_folder_path.mkdir(parents=True, exist_ok=True)
            logging.info("Створено теку: %s", new_folder_path)
        else:
            logging.info("Тека вже існує: %s", new_folder_path)

def move_file(list_of_path, file_suffix, path_to_destination_dir):

    "Функція переміщення файлів"

    logging.info("Start moving for %s files", file_suffix[1::])
    for i in list_of_path:
        if i.suffix == file_suffix:
            destination_path=path_to_destination_dir/file_suffix[1::]/i.name
            logging.info("Move %s files to %s", i, destination_path)
            i.rename(destination_path)
            print ("Move ", colorama.Fore.RED, i, colorama.Fore.RESET)
    logging.info("End moving for %s files", file_suffix[1::] )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(asctime)s" \
    " %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    print("Welcome!")
    while True:
        user_input = input("Enter source directory and destination directory: ")
        path_to_source_dir, path_to_destination = validation_arg(user_input.split())
        if path_to_source_dir is not None and path_to_destination is not None:
            lock = RLock()
            threads=[]
            pool=Semaphore(2)
            list_of_file, set_of_suffix = iter_object_in_dir(path_to_source_dir)
            create_folder(set_of_suffix, path_to_destination)
            for i in set_of_suffix:
                th = Thread(target=move_file, args=(list_of_file, i, path_to_destination, ))
                th.start()
            break
