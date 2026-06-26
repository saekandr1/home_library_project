import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

DB_NAME = "home_library_v2.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                genre TEXT
            )
        """)
        conn.commit()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Домашняя библиотека")
        self.root.geometry("750x500")
        
        init_db()
        
        # Поля ввода
        frame_inputs = tk.LabelFrame(root, text="Данные книги", padx=10, pady=10)
        frame_inputs.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_inputs, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(frame_inputs, width=25)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(frame_inputs, text="Автор:").grid(row=0, column=2, sticky="w")
        self.entry_author = tk.Entry(frame_inputs, width=25)
        self.entry_author.grid(row=0, column=3, padx=5, pady=2)
        
        tk.Label(frame_inputs, text="Год:").grid(row=1, column=0, sticky="w")
        self.entry_year = tk.Entry(frame_inputs, width=25)
        self.entry_year.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(frame_inputs, text="Жанр:").grid(row=1, column=2, sticky="w")
        self.entry_genre = tk.Entry(frame_inputs, width=25)
        self.entry_genre.grid(row=1, column=3, padx=5, pady=2)
        
        # Кнопки действий
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(fill="x", padx=15, pady=5)
        
        tk.Button(frame_buttons, text="Добавить", bg="#2ecc71", fg="white", command=self.add_book).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Изменить выбранную", bg="#3498db", fg="white", command=self.edit_book).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Удалить выбранную", bg="#e74c3c", fg="white", command=self.delete_book).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Показать статистику", command=self.show_stats).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Создать HTML-отчет", bg="#9b59b6", fg="white", command=self.make_report).pack(side="left", padx=5)
        
        # Поиск
        frame_search = tk.LabelFrame(root, text="Поиск", padx=10, pady=5)
        frame_search.pack(fill="x", padx=15, pady=5)
        
        self.entry_search = tk.Entry(frame_search, width=30)
        self.entry_search.pack(side="left", padx=5)
        
        self.combo_crit = ttk.Combobox(frame_search, values=["По названию", "По автору", "По жанру"], state="readonly", width=15)
        self.combo_crit.set("По названию")
        self.combo_crit.pack(side="left", padx=5)
        
        tk.Button(frame_search, text="Найти", command=self.search_books).pack(side="left", padx=5)
        tk.Button(frame_search, text="Сбросить", command=self.load_books).pack(side="left", padx=5)
        
        # Таблица книг
        self.tree = ttk.Treeview(root, columns=("ID", "Название", "Автор", "Год", "Жанр"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Жанр", text="Жанр")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Год", width=60, anchor="center")
        self.tree.column("Жанр", width=120)
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.load_books()

    def load_books(self, rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if rows is None:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, author, year, genre FROM books")
                rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_book(self):
        t, a, y, g = self.entry_title.get(), self.entry_author.get(), self.entry_year.get(), self.entry_genre.get()
        if not t or not a:
            messagebox.showerror("Ошибка", "Название и Автор обязательны!")
            return
        try:
            year = int(y) if y else None
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return
            
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author, year, genre) VALUES (?, ?, ?, ?)", (t, a, year, g))
            conn.commit()
        self.load_books()
        self.clear_entries()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], "values")
        self.clear_entries()
        self.entry_title.insert(0, values[1])
        self.entry_author.insert(0, values[2])
        self.entry_year.insert(0, values[3] if values[3] != "None" else "")
        self.entry_genre.insert(0, values[4])

    def edit_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу из таблицы!")
            return
        book_id = self.tree.item(selected[0], "values")[0]
        t, a, y, g = self.entry_title.get(), self.entry_author.get(), self.entry_year.get(), self.entry_genre.get()
        try:
            year = int(y) if y else None
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return
            
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET title=?, author=?, year=?, genre=? WHERE id=?", (t, a, year, g, book_id))
            conn.commit()
        self.load_books()

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу из таблицы!")
            return
        book_id = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Подтверждение", "Удалить эту книгу?"):
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
            self.load_books()
            self.clear_entries()

    def search_books(self):
        q = self.entry_search.get()
        crit_map = {"По названию": "title", "По автору": "author", "По жанру": "genre"}
        crit = crit_map[self.combo_crit.get()]
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, title, author, year, genre FROM books WHERE {crit} LIKE ?", (f"%{q}%",))
            rows = cursor.fetchall()
        self.load_books(rows)

    def show_stats(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
            genres = "\n".join([f" - {g if g else 'Не указан'}: {c}" for g, c in cursor.fetchall()])
        messagebox.showinfo("Статистика", f"Всего книг: {total}\n\nПо жанрам:\n{genres}")

    def make_report(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
            genres = cursor.fetchall()
            cursor.execute("SELECT author, COUNT(*) FROM books GROUP BY author")
            authors = cursor.fetchall()
            
        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Отчет</title>
        <style>body{{font-family:Arial;margin:30px;background:#f4f6f9;}} .card{{background:white;padding:20px;margin-bottom:15px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}} table{{width:100%;border-collapse:collapse;}} th,td{{border:1px solid #ddd;padding:10px;}} th{{background:#34495e;color:white;}}</style></head>
        <body><h1>Отчет по домашней библиотеке</h1><p>Создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <div class='card'><h2>Общее количество: {total}</h2></div>
        <div class='card'><h2>Жанры</h2><table><tr><th>Жанр</th><th>Кол-во</th></tr>"""
        for g, c in genres: html += f"<tr><td>{g if g else 'Не указан'}</td><td>{c}</td></tr>"
        html += "</table></div><div class='card'><h2>Авторы</h2><table><tr><th>Автор</th><th>Кол-во</th></tr>"
        for a, c in authors: html += f"<tr><td>{a}</td><td>{c}</td></tr>"
        html += "</table></div></body></html>"
        
        with open("library_report.html", "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Успех", f"HTML-отчет успешно создан в папке проекта!")

    def clear_entries(self):
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
