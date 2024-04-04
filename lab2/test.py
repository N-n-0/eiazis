import time
import matplotlib.pyplot as plt
from main import make_tag_content


def measure_function_time(word_counts):
    execution_times = []

    for count in word_counts:
        # Генерируем список слов заданной длины

        words = "Название: Минюст упростил получение доверенности на автотранспорт \n Автор: Минская правда \n Категория: Транспорт\n"
        words += "Это первое предложение. А это второе. \n" * count

        # Засекаем время перед выполнением функции
        start_time = time.time()

        # Выполняем функцию
        a = make_tag_content(words)

        # Рассчитываем время выполнения
        execution_time = time.time() - start_time

        # Добавляем время выполнения в список
        execution_times.append(execution_time)
        print(count)

    # Строим график
    plt.plot(word_counts, execution_times)
    plt.xlabel('Количество абзацов по 2 предложения')
    plt.ylabel('Время выполнения (секунды)')
    plt.title('Зависимость времени работы от количества абзацов по 2 предложения')
    plt.show()

word_counts = [1, 5, 10, 50, 100, 500, 1000]
measure_function_time(word_counts)