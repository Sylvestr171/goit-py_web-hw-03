import sys
from pathlib import Path
import colorama
from threading import Thread
import logging
from time import sleep

def show_detailed_help():
    print("""
Зразок використання:
    python dir_script.py <path_to_dir>

Аргументи:
    <path_to_dir>       Шлях до текстового файлу, який потрібно прочитати.
    -h, --help, /?  Показати це повідомлення.

Приклад:
    python script.py .\dir\
    python script.py 'D:\path to lib\dir'
""")
    
# функція для виводу короткої довідки при невідповідності параметрів
def show_short_help():
    print("""
Для отримання довідки введіть: 
    python script.py -h
    python script.py --help
    python script.py /?
""")

# функція для перевірки чи в аргумент передано шлях до теки
def path_validation(path_str: str) -> bool:
    logging.info(f"Перевірка шляху до джерела")
    path = Path(path_str)
    return path.is_dir()


def validation_arg(list_of_arg: list) -> tuple[Path, Path] | tuple[None, None]:
    logging.info(f"Валідація аргументів")
    path_to_destination_dir = Path('./dist') #вказуємо дефолтний шлях до папки призначення
    logging.info(f"Присвоєння дефолтного значеннядля папки призначення")
    if len(list_of_arg) == 3 and path_validation(list_of_arg[1]): #якщо кількість аргументів 2 перевіряємо чи вказана в першому шлях до папки джерела і чи вона існує
        logging.info(f"якщо кількість аргументів 2 перевіряємо чи вказана в першому шлях до папки джерела і чи вона існує")
        path_to_source_dir = Path(list_of_arg[1])
        path_to_destination_dir = Path(list_of_arg[2])
        print('Тека ', colorama.Fore.RED, path_to_source_dir, '\b\\', colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 2 and path_validation(list_of_arg[1]): #якщо кількість аргументів 1 перевіряємо чи це шлях до папки джерела і чи вона існує
        logging.info(f"якщо кількість аргументів 1 перевіряємо чи це шлях до папки джерела і чи вона існує")
        path_to_source_dir = Path(list_of_arg[1])
        print('Тека ', colorama.Fore.RED, path_to_source_dir, '\b\\', colorama.Fore.WHITE, 'обробляється')
        return path_to_source_dir, path_to_destination_dir
    elif len(list_of_arg) == 2 and list_of_arg[1] in ('-h', '--help', '/?'): #перевіряємо чи аргумент не є запитом на довідку
        logging.info(f"якщо кількість аргументів 1 перевіряємо чи це не запит на довідку")
        show_detailed_help()
        return None, None
    elif len(list_of_arg) == 2 and not(path_validation(list_of_arg[1])): #якщо аргументом не є шлях або така тека не існує
        logging.info(f"якщо аргумент 1 але він не є шлях або така тека не існує")
        print (colorama.Fore.RED, 'Даний шлях не існує або аргумент не є шляхом', colorama.Fore.WHITE )
        return None, None
    else:
        show_short_help()
        return None, None

list_of_file = []
list_of_suffix = set()
#функція формування списку шляхів до папок/файлів
def iter_object_in_dir(path: Path):
    for i in path.iterdir():
        if i.is_file(): #перевіряємо чи об'єкт файл
            list_of_file.append(i) #додаємо до списку шлях до файлу
        elif i.is_dir():  #перевіряємо чи об'єкт папка
            iter_object_in_dir(i) #рекурсивно викикаємо функцію
    for i in list_of_file:
        list_of_suffix.add(i.suffix)
    return f"{list_of_file}\n {list_of_suffix}"

def move_file(list_of_path, file_suffix):
    logging.info(f"Start moving for {file_suffix[1::]} files")
    for i in list_of_path:
        if i.suffix == file_suffix:
            logging.info(f"Move {i} files")
            print ("Move ", colorama.Fore.RED, i, colorama.Fore.RESET)
            sleep(1)
    logging.info(f"End moving for {file_suffix[1::]} files")



def parse_input(user_input:str) -> tuple[str,*tuple[str,...]]:
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    print("Welcome!")
    while True:
        user_input = input("Enter source directory and destination directory: ")
        path_to_source_dir, path_to_destination_dir = validation_arg(sys.argv)
        if path_to_source_dir is not None and path_to_destination_dir is not None:
            Path(path_to_destination_dir).mkdir(parents=True, exist_ok=True) #створюємо папку призначення
            print (iter_object_in_dir(path_to_source_dir))
            for i in list_of_suffix:
                th = Thread(target=move_file, args=(list_of_file, i, ))
                th.start()
