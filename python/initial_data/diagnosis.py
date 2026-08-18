from random import choice
import psycopg2

data_diagnosis = (
    'Моторная алалия',
    'Артикуляционная диспраксия',
    'Сенсорная алалия',
    'Дизартрия',
    'Заикание',
    'Дислексия',
    'Дисграфия',
    'Дислалия',
    'Общее недоразвитие речи',
    'Фонетико-фонематическое недоразвитие речи'
)

diagnosis = [{"patient_id":n, "diagnosis":choice(data_diagnosis)} for n in range(1,19)]


with psycopg2.connect (
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:

        cursor.executemany("""
            INSERT INTO diagnosis (patient_id, diagnosis) 
            VALUES (%(patient_id)s, %(diagnosis)s)""",diagnosis)
    conn.commit()

print(len(diagnosis), 'Successfully')