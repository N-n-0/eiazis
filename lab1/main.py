import os

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet
import pymorphy3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from db import *
import re

from werkzeug.utils import secure_filename

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = "C:/Users/nikit/Desktop/bsuir/ЕЯзИИС/lab1/files"

app = Flask(__name__)
morphem = ['Часть речи', 'Одушевленность', 'Вид',
           'Падеж', 'Род', 'Наклонение', 'Число', 'Лицо', 'Время',
           'Переходность']
abbreviations = {"NOUN": "Имя существительное", "ADJF": "Имя прилагательное (полное)",
                 "ADJS": "Имя прилагательное (краткое)", "COMP": "Компаратив",
                 "VERB": "Глагол", "INFN": "Инфинитив",
                 "PRTF": "Причастие (полное)", "PRTS": "Причастие (краткое)",
                 "GRND": "Деепричастие", "NUMR": "Числительное", "ADVB": "Наречие",
                 "NPRO": "Местоимение", "PRED": "Предикатив", "PREP": "Предлог",
                 "CONJ": "Союз", "PRCL": "Частица", "INTJ": "Междометие",
                 "nomn": "Именительный", "gent": "Родительный", "datv": "Дательный",
                 "accs": "Винительный", "ablt": "Творительный", "loct": "Предложный",
                 "voct": "Звательный", "gen2": "Родительный (частичный)",
                 "acc2": "Винительный", "loc2": "Предложный (местный)",
                 "sing": "Единственное", "plur": "Множественное",
                 "masc": "Мужской", "femn": "Женский", "neut": "Средний",
                 "LATN": "Токен состоит из латинских букв", "NUMB": "Число",
                 "intg": "Целое число", "real": "Вещественное число",
                 "ROMN": "Римское число", "anim": "Одушевленное",
                 "inan": "Неодушевленное", "perf": "Совершенный",
                 "impf": "Несовершенный", "tran": "Переходный",
                 "intr": "Непереходный", "1per": "1", "2per": "2", "3per": "3",
                 "pres": "Настоящее", "past": "Прошедшее", "futr": "Будущее",
                 "indc": "Изъявительное", "impr": "Повелительное"}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def intro():
    print("3")
    if request.method == 'POST':
        print("2")
        """req = request.form
        print(req.get("file"))
        adress = find_word(req.get("search"))
        file = request.files['file']
        # Далее можно работать с файлом, например, сохранить его на сервере
        file.save(f'{adress}')
        print(file)
        start(file)"""
        if 'file' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            print("No file part")
            return redirect(request.url)
        file = request.files['file']
        print(file)
        # Если файл не выбран, то браузер может
        # отправить пустой файл без имени.
        if file.filename == '':
            print("No selected file")
            return redirect(request.url)
        if file :
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # если все прошло успешно, то перенаправляем
            # на функцию-представление `download_file`
            # для скачивания файла
            start(filename)
    print("1")
    words = select_all_words()
    return render_template("all_words.html", words=words)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/word/<int:id>', methods=["GET", "POST"])
def word(id):
    selected_word = select_word(id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))

    words = select_all_words()
    return render_template("word.html", words=words, value=value, morphem=morphem, size=10, val_size=len(selected_word))

@app.route('/word', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        req = request.form
        print(req.get("search"))
        id = find_word(req.get("search"))
        if id is not None:
            return redirect(url_for('word', id=id))
        else:
            return redirect(request.url)
    words = select_all_words()
    return render_template("all_words.html", words=words)


@app.route('/example/<int:id>', methods=['GET', 'POST'])
def example(id):
    if request.method == "POST":
        req = request.form
        print(req.get("file"))
    selected_word = select_word(id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))
    if request.method == "POST":
        req = request.form
        print(req.get("file"))
        return redirect(request.url)

    words = select_all_words()
    return render_template("example.html", words=words, id=id, value=value, morphem=morphem, size=10, val_size=len(selected_word))


def change_info(word):
    value = []
    for element in word[1:]:
        if element in abbreviations:
            value.append(abbreviations[element])
        else:
            value.append(element)
    return value


def make_insert_value(word):
    morph = pymorphy3.MorphAnalyzer(lang='ru')
    parsed_word = morph.parse(word)[0].tag  # Морфологический анализ слова

    values = [morph.parse(word)[0].normal_form, word, parsed_word.POS,
              parsed_word.animacy, parsed_word.aspect, parsed_word.case,
              parsed_word.gender, parsed_word.mood, parsed_word.number,
              parsed_word.person, parsed_word.tense, parsed_word.transitivity]
    return values


def make_insert(tokens):
    normal_form = []
    words = []
    for token in tokens:
        value = make_insert_value(token)
        if value[0] not in normal_form:
            normal_form.append(value[0])
        if value not in words:
            words.append(value)
    return normal_form, words


def start(filename):

    with open(f"{UPLOAD_FOLDER}/{filename}", "r", encoding='utf-8') as f:
        text = f.read()
        filtered_text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
        tokens = [token.lower() for token in word_tokenize(filtered_text)]
        clear_table()
        normal_form, words = make_insert(tokens)
        insert_word(normal_form, words)
        f.close()


if __name__ == '__main__':
    app.run(debug=True)
