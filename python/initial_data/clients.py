import psycopg2
from faker import Faker

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
    if (total_archive + total_new) >=4:
        return 'активный'

    return fake_ru.random_element(["новый", "активный", "архив"])


fake_ru = Faker("ru_RU")
clients = []



dataMetroStation = (
    'Проспект Ветеранов',
    'Ленинский проспект',
    'Автово',
    'Нарвская',
    'Балтийская',
    'Технологический институт 1',
    'Пушкинская',
    'Владимирская',
    'Садовая',
    'Улица Дыбенко'
)

for _ in range(20):

    gender = fake_ru.random_element(["мужской","женский"])

    [first_name, last_name, middle_name] = gender_assignment(gender)

    status = status_assignment(clients)

    clients.append({
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "birth_date": fake_ru.date_of_birth(minimum_age=18, maximum_age=80),
        "phone_number": fake_ru.phone_number(),
        "metro_station": fake_ru.random_element(dataMetroStation),
        "notes": fake_ru.text(max_nb_chars=100),
        "gender": gender,
        "status": status
    })

with psycopg2.connect(
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:
        cursor.executemany("""INSERT INTO clients (
        first_name,
        last_name,
        middle_name,
        birth_date,
        phone_number,
        metro_station,
        notes,
        gender,
        status) VALUES(
        %(first_name)s, 
        %(last_name)s, 
        %(middle_name)s, 
        %(birth_date)s, 
        %(phone_number)s, 
        %(metro_station)s, 
        %(notes)s, 
        %(gender)s, 
        %(status)s)""", clients)
    conn.commit()



print(*clients, sep ="\n")