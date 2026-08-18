import psycopg2
from faker import Faker
from random import choice

fake_ru = Faker("ru_RU")


data_result = [
    ('удовлетворительно', 3),
    ('хорошо', 4),
    ('отлично', 5),
    ('плохо', 2)
]

plan_lesson = []

with psycopg2.connect(
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, status FROM lessons")

        rows = cursor.fetchall()

        lesson_id = [row[0] for row in rows]
        statuses = [row[1] for row in rows]

        for n in range(len(lesson_id)):
            if statuses[n] in ('пропущено','назначено'):
                result = None
                rating = None
            else:
                random_paire = choice(data_result)
                result = random_paire[0]
                rating = random_paire[1]

        
            plan_lesson.append({
                "lesson_id": lesson_id[n],
                "description": fake_ru.text(max_nb_chars=100),
                "reslut": result,
                "rating": rating
            })

        cursor.executemany("""
            INSERT INTO plan_lesson (lesson_id, description, reslut, rating)
            VALUES (%(lesson_id)s, %(description)s, %(reslut)s, %(rating)s)""", plan_lesson)
        conn.commit()

print(len(plan_lesson), 'Success')






