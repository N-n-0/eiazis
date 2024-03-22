import os
from nltk.stem import SnowballStemmer
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet
import pymorphy3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from db import *
import re
from werkzeug.utils import secure_filename
import json
import codecs



UPLOAD_FOLDER = "C:/Users/nikit/Desktop/bsuir/ЕЯзИИС/lab1/files"
SAVE_FOLDER = "C:/Users/nikit/Desktop/bsuir/ЕЯзИИС/lab1/saves"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SAVE_FOLDER'] = SAVE_FOLDER


morphem_dict = ['Часть речи', 'Одушевленность', 'Вид',
           'Падеж', 'Род', 'Наклонение', 'Число', 'Лицо', 'Время',
           'Переходность', 'Основа слова', 'Окончание']

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

part_of_speech_dict = {
                 "NOUN": ["Число", "Падеж"],
                 "ADJF": ["Число", "Падеж", "Род"],
                 "ADJS": ["Число", "Падеж", "Род"],
                 "INFN": ["Наклонение", "Число","Время", "Лицо", "Род"],
                 "VERB": ["Наклонение", "Число","Время", "Лицо", "Род"],
                 "NUMR": ["Падеж", "Число", "Род"],
                 "PRTF": ["Форма", "Число", "Род", "Падеж"],
                 "PRTS": ["Форма", "Число", "Род", "Падеж"],
                 "NPRO": ["Падеж", "Число", "Род"]}

edit_param_dict = {
                "Число": ["Единственное", "Множественное"],
                "Падеж": ["Именительный", "Родительный", "Дательный", "Винительный", "Творительный", "Предложный"],
                "Род": ["Мужской", "Женский", "Средний"],
                "Наклонение": ["Повелительное", "Изъявительное"],
                "Форма": ["Полная", "Краткая"],
                "Время": ["Прошедшее", "Настоящее", "Будущее"],
                "Лицо": ["1-е", "2-е", "3-е"]
}
@app.route('/', methods=['GET', 'POST'])
def intro():
    if request.method == 'POST':
        if 'file' not in request.files:
            print("No file part")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print("No selected file")
            return redirect(request.url)
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            start(filename)
    words = select_all_words()

    return render_template("all_words.html", words=words)


@app.route('/word/<int:id>', methods=["GET", "POST"])
def word(id):
    selected_word = select_word(id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))
    words = select_all_words()
    return render_template("word.html", words=words, value=value, morphem=morphem_dict, size=12, val_size=len(selected_word), id=id)


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


@app.route('/save', methods=['GET', 'POST'])
def output_save():
    if request.method == "POST":
        req = request.form
        filename = req.get("save_name")
        if filename is not None:
            output(filename)
            print(4)
            file_path = os.path.join(filename + '.json')
            return send_from_directory(app.config['SAVE_FOLDER'], file_path, as_attachment=True)

        else:
            return redirect(request.url)
    return render_template("save.html")

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def generate(id):
    selected_word = select_word(id)
    values = generate_edit_value(selected_word[0][2])
    if len(values) == 0:
        return render_template("non.html", id=id)
    header = selected_word[0][1]
    if request.method == "POST":
        morph = pymorphy3.MorphAnalyzer()
        parsed_word = morph.parse(header)[0]
        el_array = []
        for el in values:
            if "Множественное" in el_array and el=="Род":
                pass
            elif el == "Время" and "Повелительное" in el_array:
                pass
            elif el == "Лицо" and "Прошедшее" in el_array:
                pass
            elif el == "Род" and "Прошедшее" not in el_array and (parsed_word.tag.POS == 'INFN' or parsed_word.tag.POS == 'VERB'):
                pass
            else:
                el_value = request.form.get(f'{el}')
                el_array.append(el_value)
        params = []
        for el in el_array:
            for key, val in abbreviations.items():
                if val == el:
                    params.append(f'{key}')

        header = parsed_word.inflect({*params}).word

    return render_template("edit.html", word=header, id=id, values=values, params=edit_param_dict, size=len(values))


def generate_edit_value(word):
    morph = pymorphy3.MorphAnalyzer(lang='ru')
    parsed_word = morph.parse(word)[0].tag
    values = []
    if parsed_word.POS in list(part_of_speech_dict.keys()):
        values = part_of_speech_dict[parsed_word.POS]
    return values


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
    parsed_word = morph.parse(word)[0].tag

    values = [morph.parse(word)[0].normal_form, word, parsed_word.POS,
              parsed_word.animacy, parsed_word.aspect, parsed_word.case,
              parsed_word.gender, parsed_word.mood, parsed_word.number,
              parsed_word.person, parsed_word.tense, parsed_word.transitivity]

    stemmer = SnowballStemmer(language='russian')

    if parsed_word.POS == "ADJS" and parsed_word.gender == "masc":
        stem = word
        ending = ' '
    elif parsed_word.POS == "VERB" and parsed_word.mood == "indc" and parsed_word.tense == "past":
        if parsed_word.gender == "masc":
            stem = word[:-1]
            ending = ' '
        else:
            stem = word[:-2]
            ending = word[len(stem) + 1:] + ' '
    elif parsed_word.POS == "VERB" and parsed_word.mood == "indc" and parsed_word.tense == "pres" and parsed_word.person == "2per" and parsed_word.number == "plur":
        stem = word[:-3]
        ending = word[len(stem):] + ' '
    elif parsed_word.POS == "VERB" and parsed_word.mood == "indc" and parsed_word.tense == "futr" and parsed_word.person == "3per" and parsed_word.number == "plur":
        stem = word[:-2]
        ending = word[len(stem):] + ' '
    else:
        stem = stemmer.stem(word)
        ending = word[len(stem):] + ' '
    values.append(stem)
    values.append(ending)
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





def output(filename):
    data = select_output_info()

# Преобразование данных в формат JSON
    json_data = json.dumps(data, ensure_ascii=False)
    print(2)
    print(f"{json_data}")

    # Сохранение данных в файл JSON с кодировкой UTF-8
    with open(f'{SAVE_FOLDER}/{filename}.json', 'w', encoding='utf-8') as file:
        print(3)
        file.write(json_data)

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
    #clear_table()
    app.run(debug=True)

