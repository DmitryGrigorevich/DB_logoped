# заполнял вручную в итоге, файл недоделан этот
import psycopg2
import datetime
from random import choice

lessons = []

for n in range(40):
    lessons.append(
        {
            "patient_id":
            "status":
            "date_lesson":
        }
    )



with psycopg2.connect (
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor: