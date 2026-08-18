import psycopg2
from datetime import date, time, timedelta

slots = []
start_date = date(2026,1, 1)
end_date = date(2026, 10, 1)

current_date = start_date

while current_date <= end_date:
    current_time = time(10, 0)

    while current_time <= time(21,0):

        slots.append(
            {
                "lesson_id": None,
                "date":current_date,
                "time": current_time,
                "is_free": True,    
            }
        )
        h = current_time.hour
        m = current_time.minute
        m += 30

        if m == 60:
            h += 1
            m = 0
        current_time = time(h, m)
    current_date += timedelta(days=1)



with psycopg2.connect(
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, date_lesson FROM lessons")
        rows = cursor.fetchall()

        lesson_id = [row[0] for row in rows]
        date_lessons = [row[1] for row in rows]
        used_date = set()

        for elem in slots:
            

            for n in range(50):
                if elem["date"] == date_lessons[n] and elem["date"] not in used_date:
                    elem["lesson_id"] = lesson_id[n]
                    elem["is_free"] = False
                    used_date.add(elem["date"])
                    break
            

        cursor.executemany("""
        INSERT INTO shedule 
        (lesson_id, "date", "time", is_free)
        VALUES (%(lesson_id)s, %(date)s, %(time)s, %(is_free)s)""", slots)

    conn.commit()

print('Success')