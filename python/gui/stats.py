from db import connect_db
import tkinter as tk
from tkinter import ttk

def clear(frame):
    for wid in frame.winfo_children():
        wid.destroy()

def show_stats(content_frame):
    clear(content_frame)

    stats_buttons = [
        ('Пропуски по пациенту', lambda: skip_patients(content_frame)),
        ('Статистика по пациенту', lambda: stats_patient(content_frame)),
    ]

    for text, comm in stats_buttons:
        tk.Button(
            content_frame,
            text=text,
            command=comm
        ).pack(pady=2)

def get_patient_skips(patient_id, interval):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT p.first_name, c.first_name, c.phone_number,
                    COUNT(l.id) FILTER (WHERE l.status = 'пропущено')
                FROM patients_children p
                JOIN lessons l
                    ON l.patient_id = p.id
                JOIN LATERAL (
                    SELECT c.first_name, c.phone_number
                    FROM clients_children cc
                    JOIN clients c
                        ON c.id = cc.client_id
                    WHERE cc.children_id = p.id
                    ORDER BY c.id
                    LIMIT 1
                ) c ON TRUE
                WHERE p.id = %s AND l.date_lesson >= CURRENT_DATE - INTERVAL '{interval}'
                GROUP BY p.id, p.first_name, c.first_name, c.phone_number
            """, (patient_id,))
            return cursor.fetchone()

def get_patient_stats(patient_id):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.first_name, c.first_name, c.phone_number,
                    COUNT(l.id) FILTER (WHERE l.status = 'завершилось') AS completed,
                    COUNT(l.id) FILTER (WHERE l.status IN ('завершилось', 'пропущено')) AS total, 
                    ROUND(AVG(pl.rating) FILTER (WHERE pl.rating IS NOT NULL), 2) AS avg_rating,
                    ROUND(COUNT(l.id) FILTER (WHERE l.status = 'завершилось') * 100.0 /
                        NULLIF(COUNT(l.id) FILTER (WHERE l.status IN ('завершилось', 'пропущено')),0),1) AS attendance_percent
                FROM patients_children p
                JOIN lessons l
                    ON l.patient_id = p.id
                LEFT JOIN plan_lesson pl
                    ON pl.lesson_id = l.id
                JOIN LATERAL (
                    SELECT c.first_name, c.phone_number
                    FROM clients_children cc
                    JOIN clients c
                        ON c.id = cc.client_id
                    WHERE cc.children_id = p.id
                    ORDER BY c.id
                    LIMIT 1
                ) c ON TRUE
                WHERE p.id = %s
                GROUP BY p.id, p.first_name, c.first_name, c.phone_number
            """, (patient_id,))

            return cursor.fetchone()

def skip_patients(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Пропуски по пациенту',
        font=('Arial', 14, 'bold')
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='ID ребёнка'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_id = tk.Entry(
        content_frame,
        width=20
    )
    entry_id.grid(row=1, column=1, pady=5)

    tk.Label(
        content_frame,
        text='Период'
    ).grid(row=2, column=0, sticky='e', padx=5)

    combo_period = ttk.Combobox(
        content_frame,
        values=['месяц', '4 месяца', 'год'],
        state='readonly',
        width=18
    )
    combo_period.grid(row=2, column=1, pady=5)
    combo_period.current(0)

    def show():
        patient_id = entry_id.get() or None
        period = combo_period.get()

        if patient_id is None:
            return

        if period == 'месяц':
            interval = '1 month'
            period_label = 'за месяц'

        elif period == '4 месяца':
            interval = '4 months'
            period_label = 'за 4 месяца'

        else:
            interval = '1 year'
            period_label = 'за год'

        data = get_patient_skips(patient_id, interval)

        for wid in content_frame.grid_slaves():
            if int(wid.grid_info()['row']) >= 4:
                wid.destroy()

        if not data:
            tk.Label(
                content_frame,
                text='Пациент не найден',
                fg='red'
            ).grid(row=4, column=0, columnspan=4)

            return

        columns = (
            'Имя ребёнка',
            'Имя клиента',
            'Телефон',
            f'Пропуски ({period_label})'
        )

        tree = ttk.Treeview(
            content_frame,
            columns=columns,
            show='headings'
        )
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.insert('', tk.END, values=data)

        tree.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=10)

    tk.Button(
        content_frame,
        text='Показать',
        command=show
    ).grid(row=3, column=0, columnspan=4, pady=5)

def stats_patient(content_frame):
    clear(content_frame)

    tk.Label(
        content_frame,
        text='Статистика по пациенту',
        font=('Arial', 14, 'bold')
    ).grid(row=0, column=0, columnspan=4, pady=10)

    tk.Label(
        content_frame,
        text='ID ребёнка'
    ).grid(row=1, column=0, sticky='e', padx=5)

    entry_id = tk.Entry(
        content_frame,
        width=20
    )
    entry_id.grid(row=1, column=1, pady=5)

    def show():
        patient_id = entry_id.get() or None
        if patient_id is None:
            return

        data = get_patient_stats(patient_id)
        
        for wid in content_frame.grid_slaves():
            if int(wid.grid_info()['row']) >= 3:
                wid.destroy()

        if not data:
            tk.Label(
                content_frame,
                text='Пациент не найден',
                fg='red'
            ).grid(row=3, column=0, columnspan=4)

            return

        columns = (
            'Имя ребёнка',
            'Имя клиента',
            'Телефон',
            'Прошедших занятий',
            'Всего занятий',
            'Динамика прогресса',
            '% посещаемости'
        )

        tree = ttk.Treeview(
            content_frame,
            columns=columns,
            show='headings'
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.insert('', tk.END, values=data)
        tree.grid(row=3, column=0, columnspan=4, sticky='nsew', pady=10)

    tk.Button(
        content_frame,
        text='Показать',
        command=show
    ).grid(row=2, column=0, columnspan=4, pady=5)