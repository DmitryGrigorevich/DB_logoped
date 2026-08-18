import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname='db_logoped',
        user='postgres',
        password='root1234',
        host='localhost'
    )