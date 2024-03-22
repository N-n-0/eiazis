import psycopg2
import pymorphy3


def connect_to_db():
    try:
        conn = psycopg2.connect(host='localhost',
                                database='word_database',
                                user='postgres',
                                password='postgres')
        conn.autocommit=True
        return conn
    except Exception as _ex:
        print("Error connection", _ex)

def select_output_info():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM word_table;")
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

def select_all_words():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM normalform_table ORDER BY name ASC;")
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select all words", _ex)


def find_word(word):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT id FROM normalform_table WHERE name = '%s' ;" % (word))
        row = cur.fetchone()
        cur.close()
        connect_to_db().close()
        return row[0]
    except Exception as _ex:
        print("Error search", _ex)

def insert_word(normal_form, words):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''INSERT INTO normalform_table (name)
        VALUES ('%s');'''
        for element in normal_form:
            cur.execute(insert_query % (element))
        insert_query = '''
            INSERT INTO word_table (normal_form, name, pos, animacy, aspect, ccase, 
            gender, mood, number, person, tense, transitivity, stem, ending)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
        '''
        for word in words:
            cur.execute(insert_query % tuple(word))
        print("Successfully inserted")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error insert words", _ex)


def select_word(id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT name FROM normalform_table where id=%s ;" % (str(id)))
        rows = cur.fetchall()
        cur.execute("SELECT * FROM word_table where normal_form='%s' ;" % (rows[0][0]))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select word", _ex)

def clear_table():
    try:
        cur = connect_to_db().cursor()
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