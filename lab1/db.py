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

def create_table():
    try:
        cur = connect_to_db().cursor()
        cur.execute('''CREATE TABLE word_table (
        id SERIAL PRIMARY KEY,
        normal_form varchar(20) NOT NULL,
        name VARCHAR(20) NOT NULL ,
        pos VARCHAR(10),
        animacy VARCHAR(10),
        aspect VARCHAR(10),
        ccase VARCHAR(10),
        gender VARCHAR(10),
        mood VARCHAR(10),
        number VARCHAR(10),
        person VARCHAR(10),
        tense VARCHAR(10),
        transitivity VARCHAR(10));''')
        cur.execute('''CREATE TABLE normalform_table(
        id SERIAL PRIMARY KEY,
        name VARCHAR(30));''')
        cur.close()
        connect_to_db().close()
        print("Successfully created")
    except Exception as _ex:
        print("Error create tables", _ex)


def insert_word(normal_form, words):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''INSERT INTO normalform_table (name)
        VALUES ('%s');'''
        for element in normal_form:
            cur.execute(insert_query % (element))
        insert_query = '''
            INSERT INTO word_table (normal_form, name, pos, animacy, aspect, ccase, 
            gender, mood, number, person, tense, transitivity)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
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
        print(rows)
        cur.execute("SELECT * FROM word_table where normal_form='%s' ;" % (rows[0][0]))
        rows = cur.fetchall()
        print(rows)
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select word", _ex)

def delete_table():
    try:
        cur = connect_to_db().cursor()
        cur.execute("DROP TABLE normalform_table;")
        cur.execute("DROP TABLE word_table;")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error delete table", _ex)