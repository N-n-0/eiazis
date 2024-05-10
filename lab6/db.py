import psycopg2


def connect_to_db():
    try:
        conn = psycopg2.connect(host='localhost',
                                database='chat',
                                user='postgres',
                                password='postgres')
        conn.autocommit = True
        return conn
    except Exception as _ex:
        print("Error connection", _ex)


def select_output_info():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT question, answer FROM messages order by id;")
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


def clear_table():
    try:
        cur = connect_to_db().cursor()
        cur.execute('''DELETE FROM chats;
                    SELECT setval('chats_id_seq', 1, false);
                    ''')
        cur.execute('''DELETE FROM messages;
                    SELECT setval('messages_id_seq', 1, false);
                    ''')
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error delete table", _ex)


def drop_chat(id):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''    DELETE FROM chats  WHERE
    id = %s;'''
        cur.execute(insert_query % id)

        insert_query = '''    DELETE FROM messages  WHERE
        chat_id = %s;'''
        cur.execute(insert_query % id)

        print("Successfully inserted message")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error drop", _ex)


def add_message(id, question, answer):
    try:
        cur = connect_to_db().cursor()
        insert_query = '''INSERT INTO messages (chat_id, question, answer)
        VALUES (%s, '%s', '%s');'''
        cur.execute(insert_query % (id, question, answer))

        print("Successfully inserted message")
        cur.close()
        connect_to_db().close()
    except Exception as _ex:
        print("Error add message", _ex)


def select_name(id):
    try:
        cur = connect_to_db().cursor()
        query = "SELECT name FROM chats where id=%s"
        cur.execute(query % id)
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows[0][0]
    except Exception as _ex:
        print("Error select chat", _ex)


def insert_name(id, name):
    try:
        cur = connect_to_db().cursor()
        query = "UPDATE chats SET name = '%s' WHERE id = %s;"
        cur.execute(query % (name, id))
        cur.close()
        connect_to_db().close()

    except Exception as _ex:
        print("Error insert name", _ex)


def select_all_chats():
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT * FROM chats")
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select chat", _ex)


def create_chat():
    try:
        cur = connect_to_db().cursor()
        cur.execute("insert into chats(name) values('Пустой чат');")
        cur.execute("select * from chats")
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows[-1][0]
    except Exception as _ex:
        print("Error select chat", _ex)


def select_chat(id):
    try:
        cur = connect_to_db().cursor()
        cur.execute("SELECT question, answer FROM messages where chat_id=%s" % (id))
        rows = cur.fetchall()
        cur.close()
        connect_to_db().close()
        return rows
    except Exception as _ex:
        print("Error select chat", _ex)


"""create table chats(
	id serial PRIMARY KEY,
	name varchar(50)
);

create table messages(
	id serial PRIMARY key,
	chat_id integer,
	question varchar(50),
	answer text
);"""