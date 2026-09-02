from db import connect_db
import tkinter as tk
from tkinter import ttk

def clear(frame):
    for wid in frame.winfo_children():
        wid.destroy()

def show_lessons(content_frame):
    clear(content_frame)

    lessons_buttons = [
        ('Добавить занятие', lambda: add_lesson(content_frame)),
        ('Проставить статус занятия', lambda: add_status_lesson(content_frame)),
        ('Добавить план на занятие', lambda: add_lesson_plan(content_frame)),
        ('Просмотр плана на занятие', lambda: view_lesson_plan(content_frame)),
        ('Ввод результата и оценки', lambda: add_lesson_result(content_frame)),
        ('Просмотр результата и оценки', lambda: view_lesson_result(content_frame))
    ]

    for text, comm in lessons_buttons:
        tk.Button(
            content_frame,
            text=text,
            command=comm
        ).pack(pady=2)

def add_lesson(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Добавить занятие',
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='ID пациента'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_patient_id = tk.Entry(
        content_frame,
        width=20
    )
    entry_patient_id.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Дата (ГГГГ-ММ-ДД)'
    ).grid(row=2, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20
    )
    entry_date.grid(row=2, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Время (ЧЧ:ММ)'
    ).grid(row=3, column=0, sticky='e', padx=5)

    entry_time = tk.Entry(
        content_frame,
        width=20
    )
    entry_time.grid(row=3, column=1, pady=5)

    def save():
        patient_id = entry_patient_id.get() or None
        date = entry_date.get() or None
        time = entry_time.get() or None

        with connect_db() as conn:
            with conn.cursor() as cursor:
                # создаём занятие
                cursor.execute("""
                    INSERT INTO lessons (patient_id, status, date_lesson)
                    VALUES (%s, 'назначено', %s)
                    RETURNING id
                """, (patient_id, date))
                lesson_id = cursor.fetchone()[0]

                # занимаем слот в расписании
                cursor.execute("""
                    UPDATE schedule
                    SET lesson_id = %s, is_free = false
                    WHERE date_slot = %s AND time_slot = %s
                """, (lesson_id, date, time))

            conn.commit()

        tk.Label(
            content_frame,
            text='Занятие добавлено',
            fg='green'
        ).grid(row=5, column=0, columnspan=4)

    tk.Button(
        content_frame,
        text='Сохранить',
        command=save
    ).grid(row=4, column=0, columnspan=4, pady=10)

def add_status_lesson(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Проставить статус занятия',
        font=('Arial', 14, 'bold')
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Дата (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20
    )
    entry_date.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Время (ЧЧ:ММ)'
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
        values=['завершилось', 'пропущено'],
        state='readonly',
        width=18
    )
    combo_status.grid(row=3, column=1, pady=5)
    combo_status.current(0)

    def save():
        date = entry_date.get() or None
        time = entry_time.get() or None
        status = combo_status.get()

        with connect_db() as conn:
            with conn.cursor() as cursor:
                # получаем lesson_id из расписания
                cursor.execute("""
                    SELECT lesson_id FROM schedule
                    WHERE date_slot = %s AND time_slot = %s
                """, (date, time))
                row = cursor.fetchone()

                if not row or not row[0]:
                    tk.Label(
                        content_frame,
                        text='Занятие не найдено',
                        fg='red'
                    ).grid(row=5, column=0, columnspan=4)
                    return

                lesson_id = row[0]

                cursor.execute("""
                    UPDATE lessons
                    SET status = %s
                    WHERE id = %s
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

def get_lesson_by_date(date, time):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT l.id, p.first_name, p.last_name
                FROM lessons l
                JOIN patients_children p ON p.id = l.patient_id
                WHERE l.date_lesson = %s
                AND l.id = (
                    SELECT lesson_id FROM schedule
                    WHERE date_slot = %s AND time_slot = %s
                )
            """, (date, date, time))
            return cursor.fetchone()

def add_lesson_plan(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Добавить план на занятие',
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
        width=20)
    entry_time.grid(row=2, column=1, pady=5)

    tk.Label(
        content_frame,
        text='План занятия'
    ).grid(row=3, column=0, sticky='e', padx=5)
    entry_plan = tk.Text(
        content_frame,
        width=40,
        height=6
    )
    entry_plan.grid(row=3, column=1, pady=5)

    def save():
        date = entry_date.get() or None
        time = entry_time.get() or None
        plan = entry_plan.get('1.0', tk.END).strip() or None

        lesson = get_lesson_by_date(date, time)
        if not lesson:
            tk.Label(
                content_frame,
                text='Занятие не найдено',
                fg='red'
            ).grid(row=5, column=0, columnspan=4)
            return

        lesson_id = lesson[0]
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO plan_lesson (lesson_id, description)
                    VALUES (%s, %s)
                """, (lesson_id, plan))
            conn.commit()

        tk.Label(
            content_frame,
            text='План добавлен', 
            fg='green'
        ).grid(row=5, column=0, columnspan=4)

    tk.Button(
        content_frame,
        text='Сохранить',
        command=save
    ).grid(row=4, column=0, columnspan=4, pady=10)

def view_lesson_plan(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Просмотр плана на занятие', 
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

        lesson = get_lesson_by_date(date, time)
        if not lesson:
            tk.Label(
                content_frame,
                text='Занятие не найдено', 
                fg='red'
            ).grid(row=4, column=0, columnspan=4)
            return

        lesson_id = lesson[0]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT pl.description, l.date_lesson, p.first_name, p.last_name
                    FROM plan_lesson pl
                    JOIN lessons l 
                        ON l.id = pl.lesson_id
                    JOIN patients_children p 
                        ON p.id = l.patient_id
                    WHERE pl.lesson_id = %s
                """, (lesson_id,))
                row = cursor.fetchone()

        if not row:
            tk.Label(
                content_frame,
                text='План не найден',
                fg='red'
            ).grid(row=4, column=0, columnspan=4)
            return

        tk.Label(
            content_frame,
            text=f'Ребёнок: {row[2]} {row[3]}'
        ).grid(row=4, column=0, columnspan=4)

        tk.Label(
            content_frame,
            text=f'Дата: {row[1]}'
        ).grid(row=5, column=0, columnspan=4)

        tk.Label(
            content_frame,
            text='План:'
        ).grid(row=6, column=0, sticky='e')

        text = tk.Text(
            content_frame,
            width=40,
            height=6,
            state='normal'
        )

        text.insert('1.0', row[0] or '')
        text.config(state='disabled')
        text.grid(row=6, column=1, pady=5)

    tk.Button(
        content_frame,
        text='Показать', 
        command=show
    ).grid(row=3, column=0, columnspan=4, pady=10)

def add_lesson_result(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Ввод результата и оценки',
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
        text='Результат'
    ).grid(row=3, column=0, sticky='e', padx=5)

    entry_result = tk.Text(
        content_frame,
        width=40, height=6
    )
    entry_result.grid(row=3, column=1, pady=5)

    tk.Label(
        content_frame, 
        text='Оценка (1-5)'
    ).grid(row=4, column=0, sticky='e', padx=5)
    
    entry_rating = tk.Entry(
        content_frame,
        width=5
    )
    entry_rating.grid(row=4, column=1, sticky='w', pady=5)

    def save():
        date = entry_date.get() or None
        time = entry_time.get() or None
        result = entry_result.get('1.0', tk.END).strip() or None
        rating = entry_rating.get() or None

        lesson = get_lesson_by_date(date, time)
        if not lesson:
            tk.Label(
                content_frame,
                text='Занятие не найдено',
                fg='red'
            ).grid(row=6, column=0, columnspan=4)
            return

        lesson_id = lesson[0]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE plan_lesson
                    SET result = %s, rating = %s
                    WHERE lesson_id = %s
                """, (result, rating, lesson_id))
            conn.commit()

        tk.Label(
            content_frame,
            text='Результат сохранён',
            fg='green'
        ).grid(row=6, column=0, columnspan=4)

    tk.Button(
        content_frame,
        text='Сохранить', 
        command=save
    ).grid(row=5, column=0, columnspan=4, pady=10)

def view_lesson_result(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Просмотр результата и оценки'
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='Дата занятия (ГГГГ-ММ-ДД)'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_date = tk.Entry(
        content_frame,
        width=20)
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

        lesson = get_lesson_by_date(date, time)
        if not lesson:
            tk.Label(
                content_frame,
                text='Занятие не найдено',
                fg='red'
            ).grid(row=4, column=0, columnspan=4)
            return

        lesson_id = lesson[0]

        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT pl.result, pl.rating, l.date_lesson, p.first_name, p.last_name
                    FROM plan_lesson pl
                    JOIN lessons l 
                        ON l.id = pl.lesson_id
                    JOIN patients_children p 
                        ON p.id = l.patient_id
                    WHERE pl.lesson_id = %s
                """, (lesson_id,))
                row = cursor.fetchone()

        if not row:
            tk.Label(
                content_frame,
                text='Результат не найден',
                fg='red'
            ).grid(row=4, column=0, columnspan=4)
            return

        tk.Label(
            content_frame,
            text=f'Ребёнок: {row[3]} {row[4]}'
        ).grid(row=4, column=0, columnspan=4)
        tk.Label(
            content_frame,
            text=f'Дата: {row[2]}'
        ).grid(row=5, column=0, columnspan=4)
        tk.Label(
            content_frame,
            text=f'Оценка: {row[1]}'
        ).grid(row=6, column=0, columnspan=4)
        tk.Label(
            content_frame,
            text='Результат:'
        ).grid(row=7, column=0, sticky='e')

        text = tk.Text(
            content_frame,
            width=40,
            height=6,
            state='normal'
        )
        text.insert('1.0', row[0] or '')
        text.config(state='disabled')
        text.grid(row=7, column=1, pady=5)

    tk.Button(
        content_frame,
        text='Показать',
        command=show
    ).grid(row=3, column=0, columnspan=4, pady=10)