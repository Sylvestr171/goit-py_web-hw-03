"""modul_3_homework_1_multiprocesing"""

import logging
import time
from multiprocessing import Process,  Queue
from typing import List, cast
import colorama

logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(asctime)s" \
    " %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def factorize_without_multiproc(*number) -> List[List[int]]:

    """Функція factorize без мультипроцесорності"""

    logging.info("Функція factorize_without_multiproc")

    list_of_list=[]
    for i in number:
        list_for_one_element=[]
        for k in range(1,i+1):
            if i%k==0:
                list_for_one_element.append(k)
        logging.info("Результат для %s -> %s", i, list_for_one_element)
        list_of_list.append(list_for_one_element)
    return list_of_list

def worker(idx, i, queue):

    """Функція для мультипроцесорності"""

    list_for_one_element=[]
    for k in range(1,i+1):
        if i%k==0:
            list_for_one_element.append(k)
    queue.put([idx, list_for_one_element])


def factorize_with_multiproc(*number: int) -> List[List[int]]:

    """Функція дункція factorize з мультипроцесором"""

    logging.info("Функція ffactorize_with_multiproc")

    processes = []
    queue = Queue()
    list_of_list=[None]*len(number)

    for idx, i in enumerate(number):
        pr = Process(target=worker, args=(idx, i, queue, ))
        processes.append(pr)
        pr.start()
        logging.info("Start %s for %s", pr, i)

    for el in processes:
        logging.info("очікуємо завершення %s", el)
        el.join()

    while not queue.empty():
        idx, result = queue.get()
        logging.info("IDX %s, Result %s", idx, result)
        list_of_list[idx] = result

    return cast(List[List[int]], list_of_list)

if __name__ == '__main__':

    start_without_multiproc = time.perf_counter()
     # pylint: disable=unbalanced-tuple-unpacking
    a, b, c, d, e, f, g, h = \
        factorize_without_multiproc(128, 255, 99999, 10651060, \
                                    100000007, 100000037, 100000039, 1000000007)
    end_without_multiproc = time.perf_counter()
    elapsed_without_multiproc = end_without_multiproc - start_without_multiproc
    print(colorama.Fore.RED, "Час виконання factorize_without_multiproc ",\
           elapsed_without_multiproc, colorama.Fore.RESET)

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079,\
                  152158, 304316, 380395, 532553, 760790, 1065106, \
                    1521580, 2130212, 2662765, 5325530, 10651060]
    assert e == [1, 100000007]
    assert f == [1, 100000037]
    assert g == [1, 100000039]
    assert h == [1, 1000000007]

    start = time.perf_counter()
    a2, b2, c2, d2, e2, f2, g2, h2 = \
        factorize_with_multiproc(1000000007, 100000039, 128, \
                                 255, 99999, 10651060, 100000007, 100000037)
    end = time.perf_counter()
    elapsed = end - start
    print(colorama.Fore.RED, "Час виконання factorize_with_multiproc ",\
           elapsed, colorama.Fore.RESET)


    assert a2 == [1, 1000000007]
    assert b2 == [1, 100000039]
    assert c2 == [1, 2, 4, 8, 16, 32, 64, 128]
    assert d2 == [1, 3, 5, 15, 17, 51, 85, 255]
    assert e2 == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert f2 == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079,\
                   152158, 304316, 380395, 532553, 760790, 1065106, \
                    1521580, 2130212, 2662765, 5325530, 10651060]
    assert g2 == [1, 100000007]
    assert h2 == [1, 100000037]
