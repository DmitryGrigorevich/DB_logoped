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
            comm=comm
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
    return

def schedule_week(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Укажите дни недели через запятую: (ГГГГ-ММ-ДД, ГГГГ-ММ-ДД)'
    ).grid(column=0, row=0, columnspan=6)

    entry_week = tk.Entry(
        content_frame,
        width=30
    )
    entry_week.grid(column=0, row=1, columnspan=6)

    def save_week():
        week = entry_week.get()
        if week:
            data_start, data_end = week.split(', ')
        else:
            data_start, data_end = None, None

        data = get_week(data_start, data_end)



    tk.Button(
        content_frame,
        text='Выбрать неделю',
        command=save_week
    )


def schedule_free(content_frame):
    return