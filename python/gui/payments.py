from db import connect_db
import tkinter as tk
from tkinter import ttk

def clear(frame):
    for wid in frame.winfo_children():
        wid.destroy()

def show_payments(content_frame):
    clear(content_frame)

    payments_buttons = [
        ('Создать платёж', lambda: create_payment(content_frame)),
        ('Проверка оплаты занятия', lambda: check_payment(content_frame)),
        ('Проставить статус оплаты', lambda: update_payment_status(content_frame)),
    ]

    for text, comm in payments_buttons:
        tk.Button(
            content_frame,
            text=text,
            command=comm
        ).pack(pady=2)


def get_lesson_and_client_by_datetime(date, time):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT ON (l.id)
                    l.id, c.id, c.first_name, c.phone_number
                FROM shedule s
                JOIN lessons l 
                    ON l.id = s.lesson_id
                JOIN patients_children p 
                    ON p.id = l.patient_id
                JOIN clients_children cc 
                    ON cc.children_id = p.id
                JOIN clients c 
                    ON c.id = cc.client_id
                WHERE s.date_slot = %s AND s.time_slot = %s
            """, (date, time))
            return cursor.fetchone()


def create_payment(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Создать платёж',
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Дата занятия (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20
    )
    entry_date.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Время занятия (ЧЧ:ММ)'
    ).grid(row=2, column=0, sticky='e', padx=5)

    entry_time = tk.Entry(
        content_frame,
        width=20
    )
    entry_time.grid(row=2, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Сумма'
    ).grid(row=3, column=0, sticky='e', padx=5)

    entry_total = tk.Entry(
        content_frame,
        width=20
    )
    entry_total.grid(row=3, column=1, pady=5)

    def save():
        date = entry_date.get() or None
        time = entry_time.get() or None
        total = entry_total.get() or None

        row = get_lesson_and_client_by_datetime(date, time)

        if not row:
            tk.Label(
                content_frame,
                text='Занятие не найдено',
                fg='red'
            ).grid(row=5, column=0, columnspan=4)
            return

        lesson_id, client_id = row[0], row[1]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO payments (
                        client_id,
                        lesson_id,
                        total,
                        payment_date,
                        payment_status
                    ) VALUES (%s, %s, %s, %s, 'не оплачен')
                """, (client_id, lesson_id, total, date))
            conn.commit()

        tk.Label(
            content_frame,
            text='Платёж создан',
            fg='green'
        ).grid(row=5, column=0, columnspan=4)

    tk.Button(
        content_frame,
        text='Создать',
        command=save
    ).grid(row=4, column=0, columnspan=4, pady=10)


def check_payment(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Проверка оплаты занятия',
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Дата занятия (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20
    )
    entry_date.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Время занятия (ЧЧ:ММ)'
    ).grid(row=2, column=0, sticky='e', padx=5)

    entry_time = tk.Entry(
        content_frame,
        width=20
    )
    entry_time.grid(row=2, column=1, pady=5)

    def show():
        date = entry_date.get() or None
        time = entry_time.get() or None

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT ON (l.id)
                        c.first_name, c.phone_number, py.total, l.date_lesson, py.payment_status
                    FROM shedule s
                    JOIN lessons l 
                        ON l.id = s.lesson_id
                    JOIN patients_children p 
                        ON p.id = l.patient_id
                    JOIN clients_children cc 
                        ON cc.children_id = p.id
                    JOIN clients c 
                        ON c.id = cc.client_id
                    JOIN payments py 
                        ON py.lesson_id = l.id
                    WHERE s.date_slot = %s AND s.time_slot = %s
                """, (date, time))
                row = cursor.fetchone()

        for wid in content_frame.grid_slaves():
            if int(wid.grid_info()['row']) >= 4:
                wid.destroy()

        if not row:
            tk.Label(
                content_frame,
                text='Платёж не найден',
                fg='red'
            ).grid(row=4, column=0, columnspan=4)
            return

        columns = (
            'Имя клиента',
            'Телефон',
            'Сумма',
            'Дата занятия',
            'Статус оплаты'
        )

        tree = ttk.Treeview(
            content_frame,
            columns=columns,
            show='headings'
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)

        tree.insert('', tk.END, values=row)
        tree.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=10)

    tk.Button(
        content_frame,
        text='Проверить',
        command=show
    ).grid(row=3, column=0, columnspan=4, pady=10)


def update_payment_status(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Проставить статус оплаты',
        font=('Arial', 14, 'bold')
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Дата занятия (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20
    )
    entry_date.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Время занятия (ЧЧ:ММ)'
    ).grid(row=2, column=0, sticky='e', padx=5)

    entry_time = tk.Entry(
        content_frame,
        width=20
    )
    entry_time.grid(row=2, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Статус'
    ).grid(row=3, column=0, sticky='e', padx=5)

    combo_status = ttk.Combobox(
        content_frame,
        values=['оплачен', 'просрочен'],
        state='readonly',
        width=18
    )
    combo_status.grid(row=3, column=1, pady=5)
    combo_status.current(0)

    def save():
        date = entry_date.get() or None
        time = entry_time.get() or None
        status = combo_status.get()

        row = get_lesson_and_client_by_datetime(date, time)

        if not row:
            tk.Label(
                content_frame,
                text='Занятие не найдено',
                fg='red'
            ).grid(row=5, column=0, columnspan=4)
            return

        lesson_id = row[0]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE payments
                    SET payment_status = %s
                    WHERE lesson_id = %s
                """, (status, lesson_id))
            conn.commit()

        tk.Label(
            content_frame,
            text='Статус обновлён',
            fg='green'
        ).grid(row=5, column=0, columnspan=4)

    tk.Button(
        content_frame,
        text='Сохранить',
        command=save
    ).grid(row=4, column=0, columnspan=4, pady=10)