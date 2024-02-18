import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet
import pymorphy3
from flask import Flask, render_template, request, redirect, url_for
from db import *
import re

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


@app.route('/')
def intro():
    start()
    words = select_all_words()
    return render_template("all_words.html", words=words)


@app.route('/word/<int:id>')
def word(id):
    selected_word = select_word(id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))
    print(value)
    return render_template("word.html", value=value, morphem=morphem, size=10, val_size=len(selected_word))


@app.route('/example/<int:id>')
def example(id):
    selected_word = select_word(id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))
    print(value)
    return render_template("example.html", value=value, morphem=morphem, size=10, val_size=len(selected_word))


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


def start():
    with open("test.txt", "r", encoding='utf-8') as f:
        text = f.read()
        filtered_text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
        tokens = [token.lower() for token in word_tokenize(filtered_text)]
        delete_table()
        create_table()
        normal_form, words = make_insert(tokens)
        insert_word(normal_form, words)
        f.close()


if __name__ == '__main__':
    app.run(debug=True)
