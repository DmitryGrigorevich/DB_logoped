import psycopg2


payments = []

with psycopg2.connect(
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost",
) as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT DISTINCT ON (l.id) cs.id , l.id, l.status, l.date_lesson
        FROM clients cs
        JOIN clients_children cc
	        ON cs.id = cc.client_id
        JOIN patients_children p
            ON p.id = cc.children_id
        JOIN lessons l
	        ON l.patient_id = p.id
        ORDER BY l.id;""")

        rows = cursor.fetchall()
        client_id = [row[0] for row in rows]
        lesson_id = [row[1] for row in rows]
        lesson_status = [row[2] for row in rows]
        date_lesson = [row[3] for row in rows]

        for n in range(50):
            if lesson_status[n] == 'назначено':
                status = 'не оплачен'
            elif lesson_status[n] == 'завершилось':
                status = 'оплачен'
            else:
                status = 'просрочен'

            payments.append(
                {
                    "client_id":client_id[n],
                    "lesson_id": lesson_id[n],
                    "total": 2000,
                    "payment_date":date_lesson[n],
                    "status": status
                }
            )

        cursor.executemany("""
        INSERT INTO payments (client_id, lesson_id, total, payment_date, status)
        VALUES (%(client_id)s, %(lesson_id)s, %(total)s, %(payment_date)s, %(status)s)""", payments)
    conn.commit()

print("Success")