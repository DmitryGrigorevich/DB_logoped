from faker import Faker
from datetime import date
import psycopg2

def gender_assignment(gen):
    if gen == "мужской":
        first_name = fake_ru.first_name_male()
        last_name = fake_ru.last_name_male()
        middle_name = fake_ru.middle_name_male()
    else:
        first_name = fake_ru.first_name_female()
        last_name = fake_ru.last_name_female()
        middle_name = fake_ru.middle_name_female()

    return first_name, last_name, middle_name

def status_assignment(data):
    total_archive = sum(1 for client in data if client['status'] == 'архив')
    total_new = sum(1 for client in data if client['status'] == 'новый')
    if (total_archive + total_new) >= 4:
        return 'активный'

    return fake_ru.random_element(["новый", "активный", "архив"])

fake_ru = Faker("ru_RU")
patients_children = []


for _ in range(18):
    gender = fake_ru.random_element(["мужской","женский"])
    
    [first_name, last_name, middle_name] = gender_assignment(gender)
    status = status_assignment(patients_children)

    patients_children.append({
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "birth_date": fake_ru.date_of_birth(minimum_age=2, maximum_age=13),
        "first_visit": fake_ru.date_between(
            start_date=date(2024,1,1),
            end_date=date(2025,12,31)
        ),
        "last_visit": fake_ru.random_element([
            fake_ru.date_between(
                start_date=date(2026,1,1),
                end_date=date(2026,8,1)),
            None]),
        "status": status

    })

with psycopg2.connect (
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO patients_children (
                first_name,
                last_name,
                middle_name,
                birth_date,
                first_visit,
                last_visit,
                status
            ) VALUES (
                %(first_name)s, 
                %(last_name)s, 
                %(middle_name)s, 
                %(birth_date)s, 
                %(first_visit)s, 
                %(last_visit)s, 
                %(status)s 
            )""", patients_children)
    conn.commit()

print(len(patients_children), 'Successfully')