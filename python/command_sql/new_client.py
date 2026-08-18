import tkinter as tk
from tkinter import messagebox
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="db_logoped",
        user="postgres",
        password="root1234",
        host="localhost"
    )

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_add_client():
    clear_content()

    tk.Label(content_frame, text="Добавить клиента", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(content_frame, text="Имя*").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_first_name = tk.Entry(content_frame, width=30)
    entry_first_name.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Фамилия*").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_last_name = tk.Entry(content_frame, width=30)
    entry_last_name.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Телефон*").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_phone = tk.Entry(content_frame, width=30)
    entry_phone.grid(row=3, column=1, padx=10, pady=5)

    def save():
        first_name = entry_first_name.get()
        last_name = entry_last_name.get()
        phone = entry_phone.get()

        if not first_name or not last_name or not phone:
            messagebox.showerror("Ошибка", "Заполните обязательные поля")
            return
        try:
            with connect_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO clients (first_name, last_name, phone_number, status)
                        VALUES (%s, %s, %s, %s)
                    """, (first_name, last_name, phone, 'новый'))
                conn.commit()
            messagebox.showinfo("Успех", "Клиент добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(content_frame, text="Сохранить", command=save).grid(row=4, column=0, columnspan=2, pady=20)

def show_schedule():
    clear_content()
    tk.Label(content_frame, text="Расписание занятий", font=("Arial", 14, "bold")).pack(pady=10)
    # сюда потом добавите логику

# главное окно
root = tk.Tk()
root.title("Логопед")
root.geometry("800x500")

# левая панель навигации
nav_frame = tk.Frame(root, bg="#2c3e50", width=200)
nav_frame.pack(side="left", fill="y")
nav_frame.pack_propagate(False)

tk.Label(nav_frame, text="Меню", bg="#2c3e50", fg="white",
         font=("Arial", 12, "bold")).pack(pady=20)

nav_buttons = [
    ("Добавить клиента", show_add_client),
    ("Расписание", show_schedule),
]

for text, command in nav_buttons:
    tk.Button(nav_frame, text=text, command=command,
              bg="#34495e", fg="white", relief="flat",
              width=20, pady=8).pack(pady=2)

# правая область контента
content_frame = tk.Frame(root, bg="white")
content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

# показать начальный экран
show_add_client()

root.mainloop()