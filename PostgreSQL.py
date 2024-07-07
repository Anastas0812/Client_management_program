import psycopg2
import configparser
import datetime

config = configparser.ConfigParser()
config.read('settings.ini')
password = config['Postgres']['password']

###раскомментировать нужное при вызове функций
# new_name = str(input("Обязательные поля для заполнения*\nПожалуйста, укажите имя* "))
# new_surname = str(input("Пожалуйста, укажите фамилию*: "))
# new_email = str(input("Введите email*: "))
# new_phone_number = str(input("Введите номер(а) телефона(ов): "))
# new_birthday = input("Пожалуйста, укажите дату рождения в формате YYYY-MM-DD ")



#удаление таблиц
def delete_table():
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE phone;
            DROP TABLE client;
        """)
    return "Tables deleted"

# создание БД
def do_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client (
            id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            surname VARCHAR(60) NOT NULL,
            birthday DATE,
            email VARCHAR(80) NOT NULL,
            phone_number VARCHAR(100)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phone (
            id INTEGER PRIMARY KEY REFERENCES client(id),
            phone_number VARCHAR(100)
        );
    """)
    return "Database created"


# заполним данные для удобства выполнения дальнейших запросов
def create_tables():
    cur.execute("""
        INSERT INTO client(name, surname, birthday, email, phone_number)
            VALUES('Анастасия', 'Климанова', '1998-04-01', '12345@mail.ru', '+79151234567'),
                  ('Екатерина', 'Орлова', '1990-05-09', 'katka5@mail.ru', '+79261234567'),
                  ('Ольга', 'Бузова', '1986-01-20', 'olka5@mail.ru', '+79251234567');
    """)
    cur.execute("""
        INSERT INTO phone(id, phone_number)
            VALUES('1', '300400500');
    """)
    return 'Tables created'

# добавить нового клиента
def new_client():
    if len(new_name) <= 1:
        print('Имя пользователя не заполнено')
    if len(new_surname) <= 3:
        print('Фамилия пользователя не заполнена')
    if '@' not in new_email:
        print('email пользователя не заполнен')
    for _ in new_birthday:
        try:
            datetime.datetime.strptime(new_birthday, "%Y-%m-%d").date()
            continue
        except ValueError:
            print('Пример заполнения даты рождения 1995-10-25, попробуйте еще раз')
            break
    cur.execute("""
        INSERT INTO client(name, surname, birthday, email, phone_number)
            VALUES(%s, %s, %s, %s, %s);
    """, (new_name, new_surname, new_birthday, new_email, new_phone_number))
    return 'Новый клиент внесен'



# ищем id клиента
def get_id(cursor, name: str) -> int:
    cursor.execute("""
        SELECT id FROM client WHERE name=%s;
    """, (name,))
    return cur.fetchone()[0]

# добавить телефон для существующего клиента
def add_phone(cursor, python_id):
    cursor.execute("""
        INSERT INTO phone(id, phone_number)
            VALUES(%s, %s);
    """, (python_id, new_phone_number))
    return 'Номер успешно добавлен'

# изменить старый номер на новый
def change_phone(cursor, python_id):
    cursor.execute("""
        UPDATE client SET phone_number = %s WHERE id = %s;
    """, (new_phone_number, python_id))
    return 'Номер успешно изменен'

# изменить данные о клиенте
def change_client_data(cursor, python_id, new_name=None, new_surname=None, new_birthday=None, new_email=None):
    cursor.execute("""
        UPDATE client
            SET name = %s, surname = %s, birthday = %s, email = %s
            WHERE id = %s;
    """, (new_name, new_surname, new_birthday, new_email, python_id))
    return 'Данные клиента успешно изменены'

def old_surname(cursor, python_id):
    cur.execute("""
        SELECT surname FROM client
            WHERE id = %s;
    """, (python_id,))
    return cur.fetchone()

def old_name(cursor, python_id):
    cur.execute("""
        SELECT name FROM client
            WHERE id = %s;
    """, (python_id,))
    return cur.fetchone()

def old_birthday(cursor, python_id):
    cur.execute("""
        SELECT birthday FROM client
            WHERE id = %s;
    """, (python_id,))
    result = cur.fetchone()
    formatted_date = result[0].strftime("%Y-%m-%d")
    return formatted_date

def old_email(cursor, python_id):
    cur.execute("""
        SELECT email FROM client
            WHERE id = %s;
    """, (python_id,))
    return cur.fetchone()


# удалить телефон для существующего клиента
def delete_phone(cursor, python_id):
    cursor.execute("""
        UPDATE client
            SET phone_number = %s
            WHERE id = %s;
    """, ('Номер удален', python_id))
    return 'Номер удален'

# удалить существующего клиента
def delete_client(cursor, python_id):
        cur.execute("""
            DELETE FROM phone
                WHERE id = %s;
        """, (python_id,))
        cur.execute("""
            DELETE FROM client
                WHERE id = %s;
        """, (python_id,))
        return 'Клиент удален'


# найти клиента по его данным: имени, фамилии, email или телефону или дате рождения
def find_client(cursor, name=None, surname=None, email=None, phone_number=None, birthday=None):
    cursor.execute("""
        SELECT id FROM client
            WHERE name = %s OR surname = %s OR email = %s OR phone_number = %s OR birthday = %s;
    """, (name, surname, email, phone_number, birthday))
    return cur.fetchone()[0]

#найти по номеру телефона в резервной таблице
def find_phone_additional(cursor, phone_number):
    cursor.execute("""
        SELECT id FROM phone
            WHERE phone_number = %s;
    """, (phone_number,))
    return cur.fetchone()[0]


with psycopg2.connect(database='client_management_db', user='postgres', password=password) as conn:
    with conn.cursor() as cur:
        print(delete_table())
        print(do_db())
        print(create_tables())
        # print(new_client())
        # cur.execute("""
        #      SELECT * FROM client;
        # """)
        # print('вся таблица клиент', cur.fetchall())
        #
        # cur.execute("""
        #              SELECT * FROM phone;
        #         """)
        # print('вся таблица телефон', cur.fetchall())
        # print(get_id(cur, 'Анастасия'))
        # print(add_phone(cur, 2))
        # print(change_phone(cur, 3))
        #### если хотим поменять, например, только почту: new_email='123@ya.com', остальные параметры с функцией old_[название переменной](cur, id) и т.д.
        # print(change_client_data(cur, 2, new_name=old_name(cur, 2), new_surname=old_surname(cur, 2), new_birthday=old_birthday(cur, 2), new_email='123@ya.com'))
        # # print(delete_phone(cur, 1))
        # print(delete_client(cur, '2'))
        # print(find_client(cur, birthday='1998-04-01'))
        # print(find_phone_additional(cur, '300400500'))

conn.close()


