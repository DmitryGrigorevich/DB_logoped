from random import choice
import psycopg2

data_anamnesis = (
    'Задержка речевого развития',
    'Позднее начало речи',
    'Нарушение звукопроизношения',
    'Бедный словарный запас',
    'Заикание с трех лет',
    'Нечеткая артикуляция звуков',
    'Речь после травмы',
    'Трудности построения предложений',
    'Нарушено фонематическое восприятие',
    'Отсутствие фразовой речи'
)

medical_card = [{"patient_id":n, "anamnesis":choice(data_anamnesis)} for n in range(1,19)]

with psycopg2.connect (
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:

        cursor.executemany("""
            INSERT INTO medical_card (patient_id, anamnesis) 
            VALUES (%(patient_id)s, %(anamnesis)s)""", medical_card)
    conn.commit()


print(len(medical_card), 'Successfully')