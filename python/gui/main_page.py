import tkinter as tk
from tkinter import messagebox
import psycopg2
from clients import show_clients
from lessons import show_lessons
from payments import show_payments
from schedule import show_schedule
from stats import show_stats


root = tk.Tk()
root.title('Кабинет логопеда')
root.geometry("800x600")
root.resizable(True, True)


nav_menu = tk.Frame(root, borderwidth=2, bg='#30704D')
nav_menu.pack(side='left', fill='y')

tk.Label(nav_menu, text='Меню', bg="#30704D", fg='white',
         font=('Arial', 12, 'bold')).pack(pady=20)


nav_buttons = [
    ('Клиенты', lambda: show_clients(content_frame)),
    ('Расписание занятий', lambda: show_schedule(content_frame)),
    ('Занятия', lambda: show_lessons(content_frame)),
    ('Статистика', lambda: show_stats(content_frame)),
    ('Платежная ведомость', lambda: show_payments(content_frame))

]

for text, comm in nav_buttons:
    tk.Button(
        nav_menu,
        text=text,
        command=comm,
        ).pack(pady=2)


content_frame = tk.Frame(root, bg="white")
content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
root.mainloop()