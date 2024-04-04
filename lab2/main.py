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
import string
import codecs
import docx2txt
from PyPDF2 import PdfReader
from docx import Document as d

UPLOAD_FOLDER = "C:/Users/nikit/Desktop/bsuir/ЕЯзИИС/lab2/files"
SAVE_FOLDER = "C:/Users/nikit/Desktop/bsuir/ЕЯзИИС/lab2/saves"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SAVE_FOLDER'] = SAVE_FOLDER

morphem_dict = ['Часть речи', 'Одушевленность', 'Вид',
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
punctuation = ['.', ',', '\'', '\"', '(', ')', ':', ';', '{', '}', '[', ']', '?', '~', '`', '<', '>', '!', '...', '-', '—', '«', '»']

@app.route('/', methods=['GET', 'POST'])
def intro():
    texts = select_all_texts()
    return render_template("all_texts.html", texts=texts)


@app.route('/text/<int:id>', methods=["GET", "POST"])
def text(id):
    selected_text = select_text(id)
    texts = select_all_texts()
    return render_template("text.html", texts=texts, text=selected_text, id=selected_text[0])


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            print("No file part")
            return redirect(request.url)
        files = request.files.getlist('file')
        for file in files:
            if file.filename == '':
                print("No selected file")
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                start(filename)
        texts = select_all_texts()
        return render_template("all_texts.html", texts=texts)
    return redirect('/')


@app.route('/clear', methods=["GET", "POST"])
def clear_all():
    clear_table()
    return redirect('/')


@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        req = request.form
        id = find_text(req.get("search"))
        print(id)
        if id is not None:
            return redirect(url_for('text', id=id))
        else:
            print(request.referrer)
            if request.referrer.endswith("?"):
                url = request.referrer.rstrip("?")
            else:
                url = request.referrer
            segments = url.split("/")
            text_id = segments[-1]

            id = find_word(req.get("search"), text_id)
            print(id)
            if id is not None:
                return redirect(url_for('word', id=id, text_id=text_id))
            else:
                return redirect(request.referrer)
    return redirect('/')


@app.route('/save', methods=['GET', 'POST'])
def output_save():
    if request.method == "POST":
        req = request.form
        filename = req.get("save_name")
        if filename is not None:
            output(filename)
            file_path = os.path.join(filename + '.json')
            return send_from_directory(app.config['SAVE_FOLDER'], file_path, as_attachment=True)
        else:
            return redirect(request.url)
    return render_template("save.html")


@app.route('/save/<int:id>', methods=['GET', 'POST'])
def output_save_text(id):
    if request.method == "POST":
        filename, type = output_text(id, request.method)
        file_path = os.path.join(filename + '.txt')
        return send_from_directory(app.config['SAVE_FOLDER'], file_path, as_attachment=True)
    if request.method == "GET":
        filename, type = output_text(id, request.method)
        file_path = os.path.join(filename + '.docx')
        return send_from_directory(app.config['SAVE_FOLDER'], file_path, as_attachment=True)
    selected_text = select_text(id)

    return render_template("text.html", text=selected_text)

@app.route('/words/<int:text_id>', methods=['GET', 'POST'])
def words(text_id):
    words = select_all_words(text_id)
    return render_template("all_words.html", words=words, texts=words)

@app.route('/word/<int:text_id>/<int:id>', methods=["GET", "POST"])
def word(text_id, id):
    selected_word = select_word(text_id,id)
    value = []
    for i in range(len(selected_word)):
        value.append(change_info(selected_word[i]))
    words = select_all_words(text_id)
    return render_template("word.html", words=words, value=value, morphem=morphem_dict, size=12, val_size=len(selected_word), id=id, texts=words, text_id=text_id)

def output(filename):
    data = select_output_info()

    # Преобразование данных в формат JSON
    json_data = json.dumps(data, ensure_ascii=False)

    if os.path.exists(f'{SAVE_FOLDER}/{filename}.json'):
        os.remove(f'{SAVE_FOLDER}/{filename}.json')
    # Сохранение данных в файл JSON с кодировкой UTF-8
    with open(f'{SAVE_FOLDER}/{filename}.json', 'w', encoding='utf-8') as file:
        file.write(json_data)
        file.close()


def output_text(id, method):
    if method == "POST":
        data = select_output_text(id)
        filename = data[0]
        content = data[1]

        if os.path.exists(f'{SAVE_FOLDER}/{filename}.txt'):
            os.remove(f'{SAVE_FOLDER}/{filename}.txt')

        with open(f'{SAVE_FOLDER}/{filename}.txt', 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()
    elif method == "GET":
        data = select_text(id)
        filename = data[1]
        content = f"Название: {data[1]}\nАвтор: {data[2]}\nКатегория: {data[3]}\n{data[5]}"
        doc = d()
        doc.add_paragraph(content)
        # Сохранение документа

        if os.path.exists(f'{SAVE_FOLDER}/{filename}.docx'):
            os.remove(f'{SAVE_FOLDER}/{filename}.docx')
        doc.save(f'{SAVE_FOLDER}/{filename}.docx')


    return filename, type


def make_tag_content(text):
    # Разбиваем текст на абзацы
    paragraphs = text.split('\n\n')
    tagged_text = '<?xml version="1.0" encoding="utf-8"?><text>'
    paragraphs = paragraphs[0].split("\n")
    content = '\n'.join(text.splitlines()[3:])
    for paragraph in paragraphs[3:]:
        if paragraph not in ['', ' ']:
            tagged_text += '\n <p>'
            # Разбиваем абзац на предложения
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                words_and_punctuation = re.findall(r'\w+|[^\w\s]', sentence)  # Разделяем слова и знаки препинания

                tagged_sentence = ''
                for word_punct in words_and_punctuation:
                    if re.match(r'\w+', word_punct):  # Если это слово
                        morph = pymorphy3.MorphAnalyzer(lang='ru')
                        parsed_word = morph.parse(word_punct)[0].tag.cyr_repr

                        if "ПРИЛ " not in parsed_word and "ЧИСЛ " not in parsed_word:
                            if "," in parsed_word:
                                parts = parsed_word.split(",", 1)
                                morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parts[0]}" gram="{parts[1]}"'
                            else:
                                morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parsed_word}" gram=""'
                        else:
                            parts = parsed_word.split(" ", 1)
                            morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parts[0]}" gram="{parts[1]}"'

                        tagged_sentence += f'\n<w>{word_punct} {morph_tags[:-1]}" /></w>'
                    elif word_punct in punctuation: # Если это знак препинания
                        tagged_sentence += f'\n<pun>{word_punct}</pun>'

                tagged_sentence = tagged_sentence.strip()  # Удаляем лишние пробелы в конце предложения
                tagged_sentence = f'\n<s>\n{tagged_sentence}</s>'  # Добавляем тег предложения
                tagged_text += tagged_sentence

            tagged_text += '</p>'  # Добавляем тег абзаца
    tagged_text += '</text>'
    return paragraphs[0].split(":")[1].lstrip().rstrip(), paragraphs[1].split(":")[1].lstrip().rstrip(), paragraphs[2].split(":")[1].lstrip().rstrip(), tagged_text, content


def start(filename):
    if filename.split(".")[1] == "txt":
        with open(f"{UPLOAD_FOLDER}/{filename}", "r", encoding='utf-8') as file:
            text = file.read()
            file.close()
    elif filename.split(".")[1] == "pdf":
        with open(f"{UPLOAD_FOLDER}/{filename}", "rb") as file:
            reader = PdfReader(file)
            num_pages = len(reader.pages)

            text = ''
            # Access individual pages
            for page_number in range(num_pages):
                page = reader.pages[page_number]
                text += page.extract_text()
            file.close()
    else:
        doc = d(f"{UPLOAD_FOLDER}/{filename}")
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

    info = make_tag_content(text)
    insert_text(info)
    make_word_morphem(info[4],find_text(info[0]))

def make_word_morphem(text, id):
    filtered_text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
    tokens = [token.lower() for token in word_tokenize(filtered_text)]
    normal_form, words = make_insert(tokens)
    insert_word(normal_form, words, id)

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

def make_insert_value(word):
    morph = pymorphy3.MorphAnalyzer(lang='ru')
    parsed_word = morph.parse(word)[0].tag

    values = [morph.parse(word)[0].normal_form, word, parsed_word.POS,
              parsed_word.animacy, parsed_word.aspect, parsed_word.case,
              parsed_word.gender, parsed_word.mood, parsed_word.number,
              parsed_word.person, parsed_word.tense, parsed_word.transitivity]

    return values

def change_info(word):
    value = []
    for element in word[1:-1]:
        if element in abbreviations:
            value.append(abbreviations[element])
        else:
            value.append(element)
    return value

if __name__ == '__main__':
    app.run(debug=True)
