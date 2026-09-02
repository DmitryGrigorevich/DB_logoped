from db import connect_db
from export_data import export_to_exel
from tkinter import ttk
import tkinter as tk


def clear(frame):
    for wid in frame.winfo_children():
        wid.destroy()

def show_clients(content_frame):
    clear(content_frame)

    clients_buttons = [
        ('Добавить нового клиента и пациента', lambda: add_new_client(content_frame)),
        ('Получить архив клиентов', lambda: get_archive_clients(content_frame)),
        ('Получить активных клиентов', lambda: get_active_clients(content_frame)),
        ('Добавить потенциального клиента', lambda: add_potential_client(content_frame)),
        ('Получить потенциальных клиентов и свободные места', lambda: get_free_place_and_clients(content_frame))
    ]

    for text, comm in clients_buttons:
        tk.Button(
            content_frame, 
            text=text,
            command=comm
            ).pack(pady=2)



def add_new_client(content_frame):
    clear(content_frame)
    entry_parents_text = [
        'Имя *',
        'Фамилия *',
        'Отчество',
        'Дата рождения',
        'Номер телефона *',
        'Станция метро',
        'Заметка',
        'Пол'
    ]

    entry_children_text = [
        'Имя *',
        'Фамилия *',
        'Отчество',
        'Дата рождения',
        'Первый визит *',
        'Анамнез *'
    ]
    entry_parents_data = []
    entry_children_data = []
    tk.Label(
        content_frame,
        text='Данные родителя'
        ).grid(column=0, row=0, columnspan=5)

    for el in range(0, len(entry_parents_text)):
        tk.Label(content_frame, 
                text=entry_parents_text[el]).grid(column=0, row=el + 1, sticky='e', pady=5)

        entry = tk.Entry(content_frame, width=30)
        entry.grid(column=2, row=el + 1)
        entry_parents_data.append(entry)


    tk.Label(
        content_frame,
        text='Данные ребенка'
        ).grid(column=0, row=11, columnspan=5)

    for el in range(0, len(entry_children_text)):
        tk.Label(content_frame, 
                text=entry_children_text[el]).grid(column=0, row=12 + el, sticky='e', pady=5)
        

        entry = tk.Entry(content_frame, width=30)
        entry.grid(column=2, row=12 + el)
        entry_children_data.append(entry)


    def save_data():
        values_parents = [entry.get() or None for entry in entry_parents_data]
        values_children = [entry.get() or None for entry in entry_children_data]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO clients (
                        first_name,
                        last_name,
                        middle_name,
                        birth_date,
                        phone_number,
                        metro_station,
                        notes,
                        gender,
                        status 
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'новый')
                    RETURNING id""", values_parents)

                client_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO patients_children (
                        first_name,
                        last_name,
                        middle_name,
                        birth_date,
                        first_visit,
                        status
                    ) VALUES (%s, %s, %s, %s, %s, 'новый')
                    RETURNING id""", values_children[:5])
                
                child_id = cursor.fetchone()[0]
                relationship = None
                if values_parents[7] == 'мужской':
                    relationship = 'отец'
                elif values_parents[7] == 'женский':
                    relationship = 'мать'
                cursor.execute("""
                    INSERT INTO clients_children
                    (children_id, client_id, relationship)
                    VALUES (%s, %s, %s)
                    """, (child_id, client_id, relationship))
                cursor.execute("""
                    INSERT INTO medical_card
                    (patient_id, anamnesis)
                    VALUES (%s, %s)
                """, (child_id, values_children[5]))

            conn.commit()
            

    tk.Button(
        content_frame, 
        text='Сохранить',
        command=save_data,        
    ).grid(row=20, column=0, columnspan=5)

def get_active_clients(content_frame):

    clear(content_frame)

    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                            SELECT p.id, c.first_name, c.last_name, p.first_name,
                                r.relationship, c.phone_number, p.first_visit
                            FROM clients c
                            JOIN clients_children r
	                            ON c.id = r.client_id
                            JOIN patients_children p
	                            ON p.id = r.children_id
                            WHERE c.status = 'активный'
                            ORDER BY p.id
                        """)

            rows = cursor.fetchall()

            columns = (
                'ID ребенка',
                'Имя родителя',
                'Фамилия родителя',
                'Имя ребенка',
                'Связь',
                'Телефон',
                'Дата первого визита'
            )

    tree = ttk.Treeview(content_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in rows:    
        tree.insert('', tk.END, values=row)

    tree.pack(fill='both', expand=True)

    tk.Button(
        content_frame,
        text='Выгрузить в exel',
        command=lambda: export_to_exel('active_clients.xlsx', rows, columns)
    ).pack(pady=5)

def get_archive_clients(contnent_frame):
    clear(contnent_frame)

    with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, c.first_name, c.last_name, p.first_name,
                        r.relationship, c.phone_number, p.first_visit, p.last_visit
                    FROM clients c
                    JOIN clients_children r
                        ON c.id = r.client_id
                    JOIN patients_children p
                        ON p.id = r.children_id
                    WHERE c.status = 'архив'
                    ORDER BY p.id
                """)
                
                rows = cursor.fetchall()

                columns = (
                    'ID ребенка',
                    'Имя родителя',
                    'Фамилия родителя',
                    'Имя ребенка',
                    'Связь',
                    'Телефон',
                    'Дата первого визита',
                    'Дата последнего визита'
                )

    tree = ttk.Treeview(contnent_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in rows:    
        tree.insert('', tk.END, values=row)

    tree.pack(fill='both', expand=True)

    tk.Button(
        contnent_frame,
        text='Выгрузить в exel',
        command=lambda: export_to_exel('archive_clients.xlsx', rows, columns)
    ).pack(pady=5)

def add_potential_client(content_frame):
    clear(content_frame)

    entry_clients_text = [
        'Имя *',
        'Фамилия *',
        'Имя ребенка *',
        'Номер телефона *',
        'Диагноз *',
        'Желаемое время',
        'Желаемая дата',
        'Заметка'
    ]    

    entry_clients_data = []

    tk.Label(
        content_frame,
        text='Данные потенциального клиента',
    ).grid(row=0, column=0, columnspan=5)

    for el in range(0, len(entry_clients_text)):
        tk.Label(
            content_frame,
            text=entry_clients_text[el]
        ).grid(row=el + 1, column=0, sticky='e', pady=5)

        entry = tk.Entry(content_frame, width=30)
        if entry_clients_text[el] == 'Желаемая дата':
            entry.insert(0, 'ГГГГ-ММ-ДД')
        
        entry.grid(row=el + 1, column=1)
        entry_clients_data.append(entry)


    def save():
        values = [entry.get() or None for entry in entry_clients_data]
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO potential_clients (
                        first_name,
                        last_name,
                        child_name,
                        phone_number,
                        diagnosis,
                        desired_time,
                        request_date,
                        notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, values)
            conn.commit()

    tk.Button(
        content_frame,
        text='Сохранить',
        command=save,
    ).grid(row=len(entry_clients_text) + 2, column=0, columnspan=5)

# TODO
def get_free_place_and_clients(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Свободные места и потенциальные клиенты',
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Начало недели (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_start = tk.Entry(content_frame, width=20)
    entry_start.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Конец недели (ГГГГ-ММ-ДД)'
    ).grid(row=2, column=0, sticky='e', padx=5)

    entry_end = tk.Entry(content_frame, width=20)
    entry_end.grid(row=2, column=1, pady=5)

    def show():
        start = entry_start.get() or None
        end = entry_end.get() or None

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT date_slot, time_slot
                    FROM schedule
                    WHERE is_free = true
                    AND date_slot BETWEEN %s AND %s
                    ORDER BY date_slot, time_slot
                """, (start, end))
                free_slots = cursor.fetchall()

                cursor.execute("""
                    SELECT first_name, last_name, phone_number, diagnosis, desired_time, request_date
                    FROM potential_clients
                    ORDER BY request_date
                """)
                potential = cursor.fetchall()

        for wid in content_frame.grid_slaves():
            if int(wid.grid_info()['row']) >= 4:
                wid.destroy()

        tk.Label(
            content_frame,
            text='Свободные слоты',
        ).grid(row=4, column=0, columnspan=4, pady=5)

        cols_slots = ('Дата', 'Время')
        tree_slots = ttk.Treeview(
            content_frame,
            columns=cols_slots,
            show='headings',
            height=8
        )

        for col in cols_slots:
            tree_slots.heading(col, text=col)
            tree_slots.column(col, width=150)

        for row in free_slots:
            tree_slots.insert('', tk.END, values=row)
        tree_slots.grid(row=5, column=0, columnspan=4, sticky='nsew', pady=5)

        tk.Label(
            content_frame,
            text='Потенциальные клиенты',
        ).grid(row=6, column=0, columnspan=4, pady=5)

        cols_clients = ('Имя', 'Фамилия', 'Телефон', 'Диагноз', 'Желаемое время', 'Дата обращения')

        tree_clients = ttk.Treeview(
            content_frame,
            columns=cols_clients,
            show='headings',
            height=8
        )
        for col in cols_clients:
            tree_clients.heading(col, text=col)
            tree_clients.column(col, width=110)
            
        for row in potential:
            tree_clients.insert('', tk.END, values=row)
        tree_clients.grid(row=7, column=0, columnspan=4, sticky='nsew', pady=5)

    tk.Button(
        content_frame,
        text='Показать',
        command=show
    ).grid(row=3, column=0, columnspan=4, pady=5)