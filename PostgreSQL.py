import psycopg2
import configparser
import datetime

config = configparser.ConfigParser()
config.read('settings.ini')
password = config['Postgres']['password']



with psycopg2.connect(database='client_management_db', user='postgres', password=password) as conn:
    with conn.cursor() as cur:
        def delete_table():
            with conn.cursor() as cur:
                cur.execute("""
                    DROP TABLE phone;
                    DROP TABLE client;
                """)
            return "Tables deleted"

    # создание БД
        def do_db():
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS client (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(40) NOT NULL,
                        surname VARCHAR(60) NOT NULL,
                        birthday DATE NOT NULL,
                        email VARCHAR(80) NOT NULL,
                        phone_number VARCHAR(100)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phone (
                        id INTEGER PRIMARY KEY REFERENCES client(id),
                        phone_number_update VARCHAR(100)
                    );
                """)
                conn.commit()
            return "Database created"

        #заполним данные для удобства выполнения дальнейших запросов
        cur.execute("""
            INSERT INTO client(name, surname, birthday, email, phone_number)
                VALUES('Анастасия', 'Климанова', '1998-04-01', '12345@mail.ru', '+79151234567'),
                      ('Екатерина', 'Орлова', '1990-05-09', 'katka5@mail.ru', '+79261234567'),
                      ('Ольга', 'Бузова', '1986-01-20', 'olka5@mail.ru', '+79251234567');
        """)
        conn.commit()

        cur.execute("""
            INSERT INTO phone(id, phone_number_update)
                VALUES('1', '300400500');
        """)
        conn.commit()

    #добавить нового клиента
        def new_client():
            with conn.cursor() as cur:
                new_name = str(input("Обязательные поля для заполнения*\nПожалуйста, укажите имя* "))
                if len(new_name) <= 1:
                    print('Имя пользователя не заполнено')
                new_surname = str(input("Пожалуйста, укажите фамилию*: "))
                if len(new_surname) <= 3:
                    print('Фамилия пользователя не заполнена')
                new_birthday = input("Пожалуйста, укажите дату рождения в формате YYYY-MM-DD ")
                new_birthday = datetime.datetime.strptime(new_birthday, "%Y-%m-%d")
                #print(new_birthday) не понимаю, почему при принте он выводит норм дату(хоть и со временем 00:00:00),
                #а в выводе в консоли все равно дает datetime.date(тут цифры через запятую)
                new_email = str(input("Введите email*: "))
                if '@' not in new_email:
                    print('email пользователя не заполнен')
                new_phone_number = str(input("Введите номер(а) телефона(ов): "))
                cur.execute("""
                    INSERT INTO client(name, surname, birthday, email, phone_number)
                        VALUES(%s, %s, %s, %s, %s);
                """, (new_name, new_surname, new_birthday, new_email, new_phone_number))

                conn.commit()
            return 'Новый клиент внесен'

        # cur.execute("""
        #      SELECT * FROM client;
        # """)
        # print('вся таблица клиент', cur.fetchall())
        #
        # cur.execute("""
        #              SELECT * FROM phone;
        #         """)
        # print('вся таблица телефон', cur.fetchall())

    #ищем id клиента
        def get_id(cursor, name: str) -> int:
            cursor.execute("""
                SELECT id FROM client WHERE name=%s;
            """, (name,))
            return cur.fetchone()[0]

        python_id = get_id(cur, 'Екатерина')



    #добавить телефон для существующего клиента
        def add_phone(cursor, python_id):
            new_phone = input('Введите номер телефона: ')
            cursor.execute("""
                INSERT INTO phone(id, phone_number_update)
                    VALUES(%s, %s);
            """, (python_id, new_phone))
            conn.commit()
            return 'Номер успешно добавлен'

        # phone_check_second_table = add_phone(cur, 2)


    #изменить старый номер на новый
        def change_phone(cursor, python_id):
            cursor.execute("""
                UPDATE client SET phone_number = %s WHERE id = %s;
            """, (input('Введите новый номер: '), python_id))
            conn.commit()
            return 'Номер успешно изменен'

        # check_change_phone = change_phone(cur, 2)


    # изменить данные о клиенте
        def change_client_data(cursor, python_id):
            cursor.execute("""
            UPDATE client 
                SET name = %s, surname = %s, birthday = %s, email = %s
                WHERE id = %s;
            """, (input('Введите имя: '),
                  input('Введите фамилию: '),
                  input('Введите дату рождения в формате YYYY-MM-DD: '),
                  input('Введите email: '),
                  python_id))
            conn.commit()
            return 'Данные клиента успешно изменены'

        # check_change_client_data = change_client_data(cur, 2)

    #удалить телефон для существующего клиента
        def delete_phone(cursor, python_id):
            cursor.execute("""
            UPDATE client
                SET phone_number = %s
                WHERE id = %s;
            """, ('Номер удален', python_id))
            conn.commit()
            return 'Номер удален'

        # check_delete_phone = delete_phone(cur, 2)

    #удалить существующего клиента
        def delete_client(python_id):
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM phone
                    WHERE id = %s;
                """, (python_id,))
                cur.execute("""
                DELETE FROM client
                    WHERE id = %s;
                """, (python_id,))
                conn.commit()
                return 'Клиент удален'

        check_delete_client = delete_client(3)

    #найти клиента по его данным: имени, фамилии, email или телефону
        def find_client(cursor, name, surname):
            cursor.execute("""
            SELECT id FROM client
                WHERE
                name = %s AND 
                surname = %s 
            """, (name, surname))
            conn.commit()
            return cur.fetchone()[0]

        def find_client_email(cursor, email):
            cursor.execute("""
            SELECT id FROM client
                WHERE
                email = %s
            """, (email,))
            conn.commit()
            return cur.fetchone()[0]

        def find_client_phone(cursor, phone_number):
            cursor.execute("""
                SELECT id FROM client
                    WHERE
                    phone_number = %s
            """, (phone_number,))
            conn.commit()
            return cur.fetchone()[0]
        
        def find_client_phone_2(cursor, phone_number_update):
            cursor.execute("""
                SELECT id FROM phone
                    WHERE
                    phone_number_update = %s
            """, (phone_number_update,))
            conn.commit()
            return cur.fetchone()[0]
        
        # check_find = find_client(cur,'Анастасия', 'Климанова')
        # find_cl_email = find_client_email(cur, '12345@mail.ru')
        # find_cl_phone1 = find_client_phone(cur, '+79261234567')
        # find_cl_phone2 = find_client_phone_2(cur,'300400500')
        
if __name__ == '__main__':
    print(delete_table())
    print(do_db())
    # print(new_client())
    # print('id', python_id)
    # print(phone_check_second_table)
    # print(check_change_phone)
    # print(check_change_client_data)
    # print(check_delete_phone)
    # print(check_delete_client)
    # print(check_find)
    # print(find_cl_email)
    # print(find_cl_phone1)
    # print(find_cl_phone2)


