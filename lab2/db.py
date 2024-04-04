import psycopg2
import pymorphy3


def connect_to_db():
    try:
        conn = psycopg2.connect(host='localhost',
                                database='textual_corpus',
                                user='postgres',
                                password='postgres')
        conn.autocommit=True
        return conn
    except Exception as _ex:
        print("Error connection", _ex)

def select_output_info():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM texts;")
        rows = cur.fetchall()
        data = []

        # Преобразование результатов в формат JSON
        for row in rows:
            # Создание словаря для каждой строки
            row_data = {}
            for i, column_name in enumerate(cur.description):
                # Используйте column_name[0] для доступа к имени столбца
                # Используйте row[i] для доступа к значению столбца
                row_data[column_name[0]] = row[i]
            # Добавление словаря в список данных
            data.append(row_data)
        cur.close()
        connect_to_db().close()
        return data
    except Exception as _ex:
        print("Error select all words", _ex)

def select_all_texts():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM texts;")
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select all words", _ex)


def find_text(word):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT id FROM texts WHERE name = '%s' ;" % (word))
        row = cur.fetchone()
        cur.close()
        connect_to_db().close()
        return row[0]
    except Exception as _ex:
        print("Error search", _ex)

def insert_text(info):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''INSERT INTO texts (name, author, category, content, text_content)
        VALUES ('%s', '%s', '%s', '%s', '%s');'''
        cur.execute(insert_query % (info[0], info[1], info[2], info[3], info[4]))
        print("Successfully inserted")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error insert words", _ex)


def select_text(id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM texts where id=%s ;" % (str(id)))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows[0]
    except Exception as _ex:
        print("Error select word", _ex)

def select_output_text(id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT name, content FROM texts where id=%s ;" % (str(id)))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows[0]
    except Exception as _ex:
        print("Error select word", _ex)
def clear_table():
    try:
        cur = connect_to_db().cursor()
        cur.execute('''DELETE FROM texts;
                    SELECT setval('texts_id_seq', 1, false);
                    ''')
        cur.execute('''DELETE FROM normalform_table;
                    SELECT setval('normalform_table_id_seq', 1, false);
                    ''')
        cur.execute('''DELETE FROM word_table;
                    SELECT setval('word_table_id_seq', 1, false);
                    ''')
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error delete table", _ex)


'''Create table texts(
	id serial primary key,
	name varchar(30),
	author varchar(30), 
	category varchar(30),
	content text
);'''

def select_all_words(id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM normalform_table WHERE text_id = %s ORDER BY name ASC ;" % str(id))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select all words", _ex)


def find_word(word, id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT id FROM normalform_table WHERE name = '%s' AND text_id=%s;" % (word, str(id)))
        row = cur.fetchone()
        cur.close()
        connect_to_db().close()
        return row[0]
    except Exception as _ex:
        print("Error search", _ex)

def insert_word(normal_form, words, id):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''INSERT INTO normalform_table (name, text_id)
        VALUES ('%s', %s);'''

        for element in normal_form:
            cur.execute(insert_query % (element, str(id)))
        insert_query = '''
            INSERT INTO word_table (normal_form, name, pos, animacy, aspect, ccase, 
            gender, mood, number, person, tense, transitivity, text_id)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s);
        '''
        for word in words:
            word_list = list(word)

            # Добавление id в список
            word_list.append(id)

            # Преобразование списка обратно в кортеж
            word_with_id = tuple(word_list)
            cur.execute(insert_query % word_with_id)
        print("Successfully inserted words")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error insert words", _ex)


def select_word(text_id, id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT name FROM normalform_table where id=%s AND text_id=%s;" % (str(id), str(text_id)))
        rows = cur.fetchall()
        cur.execute("SELECT * FROM word_table where normal_form='%s' AND text_id=%s;" % (rows[0][0], str(text_id)))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select word", _ex)