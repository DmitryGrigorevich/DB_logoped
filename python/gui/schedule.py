from db import connect_db
import tkinter as tk
from tkinter import ttk

def clear(frame):
    for wid in frame.winfo_children():
        wid.destroy()



def show_schedule(content_frame):
    clear(content_frame)

    schedule_buttons = [
        ('Расписание на день', lambda: schedule_day(content_frame)),
        ('Расписание на неделю', lambda: schedule_week(content_frame)),
        ('Свободные места на неделю', lambda: schedule_free(content_frame))
    ]

    for text, comm in schedule_buttons:
        tk.Button(
            content_frame,
            text=text,
            command=comm
        ).pack(pady=2)



def get_day(data):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.date_slot, s.time_slot, p.first_name, s.is_free
                FROM schedule s
                LEFT JOIN lessons l
                    ON s.lesson_id = l.id
                LEFT JOIN patients_children p
                    ON p.id = l.patient_id
                WHERE s.date_slot = %s
                ORDER BY s.time_slot ASC;
            """, (data, ))

            return cursor.fetchall()
        

def schedule_day(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Введите день в формате ГГГГ-ММ-ДД'
    ).grid(column=0, row=0, columnspan=4)

    entry_day = tk.Entry(
        content_frame,
        width=30,
    )

    entry_day.grid(column=0, row=1, columnspan=4)

    def save_data():
        data = entry_day.get() or None
        day = get_day(data)

        columns = (
            'Дата',
            'Время',
            'Имя ребенка',
            'Статус слота'
        )
        tree = ttk.Treeview(content_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in day:
            tree.insert('', tk.END, values=row)
        tree.grid(
            column=0,
            row=4,
            columnspan=4,
            sticky='nsew'
        )

    tk.Button(
        content_frame,
        text='Выбрать день',
        command=save_data
    ).grid(column=0, row=3, columnspan=4)



def get_week(start, end):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.date_slot, s.time_slot, p.first_name, s.is_free
                FROM schedule s
                LEFT JOIN lessons l 
                    ON s.lesson_id = l.id
                LEFT JOIN patients_children p
                    ON p.id = l.patient_id
                WHERE s.date_slot BETWEEN %s AND %s
                ORDER BY s.date_slot, s.time_slot ASC
            """, (start, end))
            return cursor.fetchall()

def schedule_week(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Укажите дни недели:'
    ).grid(column=0, row=0, columnspan=6)


    tk.Label(
        content_frame, 
        text='Начало (ГГГГ-ММ-ДД)'
    ).grid(column=0, row=1, sticky='e', padx=5)

    entry_start = tk.Entry(
        content_frame, 
        width=20
    )
    entry_start.grid(column=1, row=1, pady=5)

    tk.Label(
        content_frame, 
        text='Конец (ГГГГ-ММ-ДД)'
    ).grid(column=0, row=2, sticky='e', padx=5)

    entry_end = tk.Entry(
        content_frame, 
        width=20
    )
    entry_end.grid(column=1, row=2, pady=5)

    def show_week():
        data = get_week(entry_start.get() or None, entry_end.get() or None)
        columns = ('Дата', 'Время', 'Имя ребенка', 'Статус')
        tree = ttk.Treeview(
            content_frame,
            columns=columns,
            show='headings'
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for row in data:
            tree.insert('', tk.END, values=row)

        tree.grid(column=0, row=4, columnspan=6, sticky='nsew')

    tk.Button(
        content_frame,
        text='Выбрать неделю',
        command=show_week
    ).grid(column=0, row=3)

def get_free(start, end):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.date_slot, s.time_slot
                FROM schedule s
                WHERE s.is_free = true
                AND s.date_slot BETWEEN %s AND %s
                ORDER BY s.date_slot, s.time_slot ASC
            """, (start, end))
            return cursor.fetchall()  
          
def schedule_free(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Свободные места:'
    ).grid(column=0, row=0, columnspan=6)

    tk.Label(
        content_frame,
        text='Начало (ГГГГ-ММ-ДД)'
    ).grid(column=0, row=1, sticky='e', padx=5)
    entry_start = tk.Entry(content_frame, width=20)
    entry_start.grid(column=1, row=1, pady=5)

    tk.Label(
        content_frame,
        text='Конец (ГГГГ-ММ-ДД)'
    ).grid(column=0, row=2, sticky='e', padx=5)
    entry_end = tk.Entry(content_frame, width=20)
    entry_end.grid(column=1, row=2, pady=5)

    def show_free():
        data = get_free(entry_start.get() or None, entry_end.get() or None)

        columns = ('Дата', 'Время')
        tree = ttk.Treeview(content_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        for row in data:
            tree.insert('', tk.END, values=row)

        tree.grid(column=0, row=4, columnspan=6, sticky='nsew')

    tk.Button(
        content_frame,
        text='Показать',
        command=show_free
    ).grid(column=0, row=3, columnspan=6, pady=5)

