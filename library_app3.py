import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

DB_NAME = "home_library_v3.db"

DEFAULT_GENRES = [
    "Русская классика", "Зарубежная классика", "Фантастика и фэнтези", 
    "Детектив", "Исторический роман", "Детская литература", 
    "Сказки и мифы", "Приключения для детей", "Научпоп и развитие", "Поэзия"
]

DEFAULT_BOOKS = [
    ("Мастер и Маргарита", "Михаил Булгаков", 1967, "Русская классика"),
    ("Евгений Онегин", "Александр Пушкин", 1833, "Русская классика"),
    ("Преступление и наказание", "Фёдор Достоевский", 1866, "Русская классика"),
    ("Война и мир", "Лев Толстой", 1869, "Русская классика"),
    ("Отцы и дети", "Иван Тургенев", 1862, "Русская классика"),
    ("Мёртвые души", "Николай Гоголь", 1842, "Русская классика"),
    ("Герой нашего времени", "Михаил Лермонтов", 1840, "Русская классика"),
    ("Собачье сердце", "Михаил Булгаков", 1925, "Русская классика"),
    ("1984", "Джордж Оруэлл", 1949, "Зарубежная классика"),
    ("Великий Гэтсби", "Фрэнсис Скотт Фицджеральд", 1925, "Зарубежная классика"),
    ("Гордость и предубеждение", "Джейн Остин", 1813, "Зарубежная классика"),
    ("Три товарища", "Эрих Мария Ремарк", 1936, "Зарубежная классика"),
    ("Сто лет одиночества", "Габриэль Гарсиа Маркес", 1967, "Зарубежная классика"),
    ("Граф Монте-Кристо", "Александр Дюма", 1844, "Зарубежная классика"),
    ("Хоббит", "Джон Р. Р. Толкин", 1937, "Фантастика и фэнтези"),
    ("Властелин Колец", "Джон Р. Р. Толкин", 1954, "Фантастика и фэнтези"),
    ("Гарри Поттер", "Джоан Роулинг", 1997, "Фантастика и фэнтези"),
    ("Дюна", "Фрэнк Герберт", 1965, "Фантастика и фэнтези"),
    ("451 градус по Фаренгейту", "Рэй Брэдбери", 1953, "Фантастика и фэнтези"),
    ("Трудно быть богом", "А. и Б. Стругацкие", 1964, "Фантастика и фэнтези"),
    ("Приключения Шерлока Холмса", "Артур Конан Дойл", 1892, "Детектив"),
    ("Убийство в Восточном экспрессе", "Агата Кристи", 1934, "Детектив"),
    ("Айвенго", "Вальтер Скотт", 1819, "Исторический роман"),
    ("Приключения Незнайки", "Николай Носов", 1954, "Детская литература"),
    ("Витя Малеев в школе и дома", "Николай Носов", 1951, "Детская литература"),
    ("Сказка о царе Салтане", "Александр Пушкин", 1832, "Сказки и мифы"),
    ("Конёк-Горбунок", "Пётр Ершов", 1834, "Сказки и мифы"),
    ("Приключения Тома Сойера", "Марк Твен", 1876, "Приключения для детей"),
    ("Остров сокровищ", "Р. Л. Стивенсон", 1883, "Приключения для детей"),
    ("Таинственный остров", "Жюль Верн", 1874, "Приключения для детей"),
    ("Денискины рассказы", "Виктор Драгунский", 1959, "Детская литература"),
    ("Маленький принц", "Антуан де Сент-Экзюпери", 1943, "Детская литература"),
    ("Винни-Пух", "Алан Милн", 1926, "Детская литература"),
    ("Краткая история времени", "Стивен Хокинг", 1988, "Научпоп и развитие"),
    ("Sapiens", "Юваль Ной Харари", 2011, "Научпоп и развитие"),
    ("Стихотворения", "Сергей Есенин", 1925, "Поэзия"),
    ("Понедельник начинается в субботу", "А. и Б. Стругацкие", 1965, "Фантастика и фэнтези")
]

class AdvancedCombobox(tk.Entry):
    """Умное поле ввода со всплывающим окном подсказок, не блокирующее печать букв."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.completion_list = []
        self.popup = None
        self.bind('<KeyRelease>', self.on_keyrelease)
        self.bind('<FocusOut>', self.on_focus_out)

    def set_completion_list(self, completion_list):
        # Жесткая очистка от кортежей, скобок, кавычек и запятых из БД
        cleaned = []
        for item in completion_list:
            if isinstance(item, (tuple, list)) and len(item) > 0:
                cleaned.append(str(item[0]))
            else:
                cleaned.append(str(item))
        self.completion_list = sorted(list(set([x for x in cleaned if x.strip()])))

    def on_keyrelease(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            if self.popup and event.keysym == "Down":
                self.popup.focus_set()
                self.popup.selection_set(0)
            return

        value = self.get().strip()
        if not value:
            self.close_popup()
            return

        # Ищем совпадения без учета регистра по всей длине слова
        matches = [item for item in self.completion_list if value.lower() in item.lower()]
        
        if matches:
            self.show_popup(matches)
        else:
            self.close_popup()

    def show_popup(self, matches):
        if not self.popup:
            # Создаем всплывающее окно строго под полем ввода
            self.popup = tk.Listbox(self.master, font=self['font'], bd=1, bg="white", selectbackground="#4a76a8", height=5)
            self.popup.bind('<ButtonRelease-1>', self.on_select_popup)
            self.popup.bind('<Return>', self.on_select_popup)
            
        self.popup.delete(0, tk.END)
        for item in matches:
            self.popup.insert(tk.END, item)
            
        # Позиционируем окно подсказок под текстовым полем
        info = self.grid_info()
        self.popup.grid(row=int(info['row'])+1, column=info['column'], columnspan=2, sticky="ew", padx=8, pady=0)
        self.popup.tkraise()

    def close_popup(self):
        if self.popup:
            self.popup.grid_forget()
            self.popup = None

    def on_select_popup(self, event):
        if self.popup:
            selected = self.popup.get(tk.ACTIVE)
            if selected:
                self.delete(0, tk.END)
                self.insert(0, selected)
            self.close_popup()
            self.focus_set()

    def on_focus_out(self, event):
        # Закрываем подсказки с небольшой задержкой, чтобы успел пройти клик мышки
        self.after(200, self.close_popup)

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("CREATE TABLE IF NOT EXISTS genres (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);")
        cursor.execute("CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author_id INTEGER NOT NULL, year INTEGER, genre_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE, FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM genres")
        if cursor.fetchone()[0] == 0:
            for g in DEFAULT_GENRES: cursor.execute("INSERT INTO genres (name) VALUES (?)", (g,))
            conn.commit()
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            for title, author, year, genre in DEFAULT_BOOKS:
                cursor.execute("INSERT OR IGNORE INTO authors (name) VALUES (?)", (author,))
                cursor.execute("SELECT id FROM authors WHERE name = ?", (author,))
                a_id = cursor.fetchone()[0]
                cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre,))
                cursor.execute("SELECT id FROM genres WHERE name = ?", (genre,))
                g_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO books (title, author_id, year, genre_id) VALUES (?, ?, ?, ?)", (title, a_id, year, g_id))
            conn.commit()

class AdvancedCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted([str(item) for item in completion_list], key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def handle_keyrelease(self, event):
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Escape', 'Return', 'Tab'):
            return
        typed = self.get()
        if typed == '':
            self['values'] = self._completion_list
            return
        self._hits = [item for item in self._completion_list if typed.lower() in item.lower()]
        if self._hits:
            self['values'] = self._hits
            self.event_generate('<Down>')
        else:
            self['values'] = []

class ReferenceEditor(tk.Toplevel):
    def __init__(self, parent, table_name, title_text, callback):
        super().__init__(parent)
        self.table_name = table_name
        self.callback = callback
        self.title(title_text)
        self.geometry("440x440")
        self.configure(bg="#f0f2f5")
        self.grab_set()
        
        self.sort_states = {"ID": False, "Name": False}
        self.primary_col = None
        self.ctrl_pressed = False
        
        self.bind("<KeyPress-Control_L>", lambda e: self.set_ctrl(True))
        self.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))
        self.bind("<KeyPress-Control_R>", lambda e: self.set_ctrl(True))
        self.bind("<KeyRelease-Control_R>", lambda e: self.set_ctrl(False))
        
        frame_top = tk.Frame(self, pady=10, bg="#f0f2f5")
        frame_top.pack(fill="x", padx=15)
        tk.Label(frame_top, text="Наименование:", bg="#f0f2f5", font=("Arial", 10)).pack(side="left")
        self.entry_val = tk.Entry(frame_top, width=28, font=("Arial", 10))
        self.entry_val.pack(side="left", padx=8)
        
        frame_btns = tk.Frame(self, pady=5, bg="#f0f2f5")
        frame_btns.pack(fill="x", padx=15)
        
        b1 = tk.Button(frame_btns, text="➕ Добавить", bg="#4a76a8", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=8, command=self.add_item)
        b1.pack(side="left", padx=2)
        b1.bind("<Return>", lambda e: self.add_item())
        
        b2 = tk.Button(frame_btns, text="✏️ Изменить", bg="#627382", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=8, command=self.edit_item)
        b2.pack(side="left", padx=2)
        b2.bind("<Return>", lambda e: self.edit_item())
        
        b3 = tk.Button(frame_btns, text="❌ Удалить", bg="#a35151", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=8, command=self.delete_item)
        b3.pack(side="left", padx=2)
        b3.bind("<Return>", lambda e: self.delete_item())
        
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Наименование")
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Name", width=320)
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)
        
        for col in ["ID", "Name"]:
            self.tree.heading(col, command=lambda c=col: self.sort_click(c))
            
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_item_id = None
        self.load_items()
        
    def set_ctrl(self, status):
        self.ctrl_pressed = status

    def sort_click(self, col):
        # Переключаем состояние направления (True - убывание, False - возрастание)
        self.sort_states[col] = not self.sort_states[col]
        
        if self.ctrl_pressed and self.primary_col and self.primary_col != col:
            self.secondary_col = col
            self.apply_multi_sort()
        else:
            self.primary_col = col
            self.secondary_col = None
            self.apply_single_sort(col)
            
        # Обновляем заголовки со стрелочками и номерами
        self.update_sort_headers()

    def apply_single_sort(self, col):
        # Извлекаем все элементы из таблицы: (значение, уникальный_id_строки)
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Сортируем с учетом типов данных (числа или текст)
        if col in ("ID", "Year"):
            items.sort(key=lambda t: int(t[0]) if str(t[0]).isdigit() else 0, reverse=self.sort_states[col])
        else:
            items.sort(key=lambda t: str(t[0]).lower(), reverse=self.sort_states[col])
            
        # Фиксируем новый порядок в интерфейсе
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

    def apply_multi_sort(self):
        p_col = self.primary_col
        s_col = self.secondary_col
        p_rev = self.sort_states[p_col]
        s_rev = self.sort_states[s_col]
        
        # Собираем данные: (основное_значение, вторичное_значение, id_строки)
        items = []
        for k in self.tree.get_children(''):
            p_val = self.tree.set(k, p_col)
            s_val = self.tree.set(k, s_col)
            
            p_val_proc = int(p_val) if p_col in ("ID", "Year") and str(p_val).isdigit() else str(p_val).lower()
            s_val_proc = int(s_val) if s_col in ("ID", "Year") and str(s_val).isdigit() else str(s_val).lower()
            items.append((p_val_proc, s_val_proc, k))
            
        # Стабильная многоуровневая сортировка: сначала по второму столбцу, затем по первому
        items.sort(key=lambda t: t[1], reverse=s_rev)
        items.sort(key=lambda t: t[0], reverse=p_rev)
        
        # Перемещаем строки в таблице Treeview
        for index, (p_v, s_v, k) in enumerate(items):
            self.tree.move(k, '', index)

    def load_items(self):
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, name FROM {self.table_name} ORDER BY name")
            for row in cursor.fetchall(): 
                self.tree.insert("", "end", values=row)
        self.callback()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: 
            return
        values = self.tree.item(selected, "values")
        self.selected_item_id = values[0]
        self.entry_val.delete(0, tk.END)
        self.entry_val.insert(0, values[1])

    def add_item(self):
        val = self.entry_val.get().strip()
        if not val: 
            return
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO {self.table_name} (name) VALUES (?)", (val,))
                conn.commit()
            self.load_items()
            self.entry_val.delete(0, tk.END)
            self.selected_item_id = None
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такая запись уже существует!")

    def edit_item(self):
        if not self.selected_item_id: 
            return
        val = self.entry_val.get().strip()
        if not val: 
            return
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {self.table_name} SET name=? WHERE id=?", (val, self.selected_item_id))
                conn.commit()
            self.load_items()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Дубликат!")

    def delete_item(self):
        if not self.selected_item_id: 
            return
        if messagebox.askyesno("Внимание", "Удаление сотрет связанные книги! Продолжить?"):
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (self.selected_item_id,))
                conn.commit()
            self.load_items()
            self.entry_val.delete(0, tk.END)
            self.selected_item_id = None

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📜 Домашняя библиотека")
        self.root.geometry("960x660")
        self.root.configure(bg="#f0f2f5")
        init_db()
        
        self.sort_states = {"ID": False, "Title": False, "Author": False, "Year": False, "Genre": False}
        self.primary_col = None
        self.secondary_col = None
        self.ctrl_pressed = False
        
        self.root.bind("<KeyPress-Control_L>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))
        self.root.bind("<KeyPress-Control_R>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_R>", lambda e: self.set_ctrl(False))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"), background="#e4e7eb")
        
        frame_inputs = tk.LabelFrame(root, text=" 📖 Карточка книги ", padx=15, pady=10, bg="#f0f2f5", font=("Arial", 10, "bold"), fg="#4a76a8")
        frame_inputs.pack(fill="x", padx=15, pady=8)
        
        tk.Label(frame_inputs, text="Название:", bg="#f0f2f5").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_title = tk.Entry(frame_inputs, width=32, font=("Arial", 10))
        self.entry_title.grid(row=0, column=1, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Автор:", bg="#f0f2f5").grid(row=0, column=2, sticky="w", pady=4)
        self.combo_author = AdvancedCombobox(frame_inputs, width=28, font=("Arial", 10))
        self.combo_author.grid(row=0, column=3, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Название:", bg="#f0f2f5").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_title = tk.Entry(frame_inputs, width=32, font=("Arial", 10))
        self.entry_title.grid(row=0, column=1, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Автор:", bg="#f0f2f5").grid(row=0, column=2, sticky="w", pady=4)
        self.combo_author = AdvancedCombobox(frame_inputs, width=28, font=("Arial", 10))
        self.combo_author.grid(row=0, column=3, padx=8, pady=4)
        
        # Кнопка «Справочник авторов» справа от списка авторов
        b_auth = tk.Button(frame_inputs, text="📂", bg="#718191", fg="white", font=("Arial", 9), relief="flat", padx=5,
                           command=lambda: ReferenceEditor(self.root, "authors", "Авторы", self.update_comboboxes))
        b_auth.grid(row=0, column=4, padx=4, pady=4)
        b_auth.bind("<Return>", lambda e: b_auth.invoke())

        tk.Label(frame_inputs, text="Год издания:", bg="#f0f2f5").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_year = tk.Entry(frame_inputs, width=32, font=("Arial", 10))
        self.entry_year.grid(row=1, column=1, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Жанр:", bg="#f0f2f5").grid(row=1, column=2, sticky="w", pady=4)
        self.combo_genre = AdvancedCombobox(frame_inputs, width=28, font=("Arial", 10))
        self.combo_genre.grid(row=1, column=3, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Год издания:", bg="#f0f2f5").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_year = tk.Entry(frame_inputs, width=32, font=("Arial", 10))
        self.entry_year.grid(row=1, column=1, padx=8, pady=4)
        
        tk.Label(frame_inputs, text="Жанр:", bg="#f0f2f5").grid(row=1, column=2, sticky="w", pady=4)
        self.combo_genre = AdvancedCombobox(frame_inputs, width=28, font=("Arial", 10))
        self.combo_genre.grid(row=1, column=3, padx=8, pady=4)
        
        # Кнопка «Справочник жанров» справа от списка жанров
        b_gen = tk.Button(frame_inputs, text="📂", bg="#718191", fg="white", font=("Arial", 9), relief="flat", padx=5,
                          command=lambda: ReferenceEditor(self.root, "genres", "Жанры", self.update_comboboxes))
        b_gen.grid(row=1, column=4, padx=4, pady=4)
        b_gen.bind("<Return>", lambda e: b_gen.invoke())

        frame_buttons = tk.Frame(root, bg="#f0f2f5")
        frame_buttons.pack(fill="x", padx=15, pady=4)
        btns_data = [
            ("➕ Добавить", "#4a76a8", self.add_book),
            ("✏️ Изменить", "#627382", self.edit_book),
            ("❌ Удалить", "#a35151", self.delete_book),
            ("📊 Статистика", "#5181b8", self.show_stats)
        ]
        
        for text, color, cmd in btns_data:
            b = tk.Button(frame_buttons, text=text, bg=color, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=10, pady=3, command=cmd)
            b.pack(side="left", padx=3)
            b.bind("<Return>", lambda e, btn=b: btn.invoke())
            
        b_report = tk.Button(frame_buttons, text="💾 HTML-отчет", bg="#5f7a68", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=12, pady=3, command=self.make_report)
        b_report.pack(side="right", padx=3)
        b_report.bind("<Return>", lambda e, btn=b_report: btn.invoke())
        
        frame_search = tk.LabelFrame(root, text=" 🔍 Быстрый поиск ", padx=15, pady=8, bg="#f0f2f5", font=("Arial", 9, "bold"), fg="#627382")
        frame_search.pack(fill="x", padx=15, pady=8)
        
        self.entry_search = tk.Entry(frame_search, width=35, font=("Arial", 10))
        self.entry_search.pack(side="left", padx=5)
        # Привязка обычного Enter на клавиатуре к функции поиска
        self.entry_search.bind("<Return>", lambda e: self.search_books())
        
        self.combo_crit = ttk.Combobox(frame_search, values=["По названию", "По автору", "По жанру"], state="readonly", width=15, font=("Arial", 9))
        self.combo_crit.set("По названию")
        self.combo_crit.pack(side="left", padx=5)
        
        b_src = tk.Button(frame_search, text="🔍 Найти", bg="#627382", fg="white", font=("Arial", 9), relief="flat", padx=10, command=self.search_books)
        b_src.pack(side="left", padx=3)
        b_src.bind("<Return>", lambda e: self.search_books())
        
        b_rst = tk.Button(frame_search, text="🔄 Сбросить", bg="#919fae", fg="white", font=("Arial", 9), relief="flat", padx=10, command=self.load_data)
        b_rst.pack(side="left", padx=3)
        b_rst.bind("<Return>", lambda e: self.load_data())
        
        self.tree = ttk.Treeview(root, columns=("ID", "Title", "Author", "Year", "Genre"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название книги")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Year", text="Год")
        self.tree.heading("Genre", text="Жанр")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Title", width=280)
        self.tree.column("Author", width=200)
        self.tree.column("Year", width=70, anchor="center")
        self.tree.column("Genre", width=180)
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Принудительно связываем клики по заголовкам с функцией сортировки
        for col in ["ID", "Title", "Author", "Year", "Genre"]:
            self.tree.heading(col, command=lambda c=col: self.sort_click(c))
        
        for col in ["ID", "Title", "Author", "Year", "Genre"]:
            self.tree.heading(col, command=lambda c=col: self.sort_click(c))
            
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_book_id = None
        self.load_data()

    def set_ctrl(self, status):
        self.ctrl_pressed = status

    def sort_click(self, col):
        if self.ctrl_pressed and self.primary_col and self.primary_col != col:
            self.secondary_col = col
            self.sort_states[col] = not self.sort_states[col]
            self.apply_multi_sort()
        else:
            self.primary_col = col
            self.secondary_col = None
            self.sort_states[col] = not self.sort_states[col]
            self.apply_single_sort(col)

    def apply_single_sort(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col in ("ID", "Year"):
            items.sort(key=lambda t: int(t[0]) if str(t[0]).isdigit() else 0, reverse=self.sort_states[col])
        else:
            items.sort(key=lambda t: str(t[0]).lower(), reverse=self.sort_states[col])
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

    def apply_multi_sort(self):
        p_col = self.primary_col
        s_col = self.secondary_col
        p_rev = self.sort_states[p_col]
        s_rev = self.sort_states[s_col]
        items = []
        
        for k in self.tree.get_children(''):
            p_val = self.tree.set(k, p_col)
            s_val = self.tree.set(k, s_col)
            p_val_proc = int(p_val) if p_col in ("ID", "Year") and str(p_val).isdigit() else str(p_val).lower()
            s_val_proc = int(s_val) if s_col in ("ID", "Year") and str(s_val).isdigit() else str(s_val).lower()
            items.append((p_val_proc, s_val_proc, k))
            
        items.sort(key=lambda t: t[1], reverse=s_rev)
        items.sort(key=lambda t: t[0], reverse=p_rev)
        for index, (p_v, s_v, k) in enumerate(items):
            self.tree.move(k, '', index)

    def update_comboboxes(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # Принудительно извлекаем строку из кортежа [r[0]], убирая скобки и кавычки
            cursor.execute("SELECT name FROM genres ORDER BY name")
            genres = [r[0] for r in cursor.fetchall() if r[0]]
            self.combo_genre.set_completion_list(genres)
            
            cursor.execute("SELECT name FROM authors ORDER BY name")
            authors = [r[0] for r in cursor.fetchall() if r[0]]
            self.combo_author.set_completion_list(authors)

    def load_data(self, rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.update_comboboxes()
        if rows is None:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT books.id, books.title, authors.name, books.year, genres.name FROM books
                    JOIN authors ON books.author_id = authors.id 
                    JOIN genres ON books.genre_id = genres.id 
                    ORDER BY books.id DESC
                """)
                rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
            self.update_sort_headers()

    def add_book(self):
        t, a, y, g = self.entry_title.get().strip(), self.combo_author.get(), self.entry_year.get().strip(), self.combo_genre.get()
        if not t or not a or not g:
            messagebox.showerror("Ошибка", "Заполните ключевые поля!")
            return
        try:
            year = int(y) if y else None
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return
            
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO authors (name) VALUES (?)", (a,))
            cursor.execute("SELECT id FROM authors WHERE name = ?", (a,))
            a_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (g,))
            cursor.execute("SELECT id FROM genres WHERE name = ?", (g,))
            g_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO books (title, author_id, year, genre_id) VALUES (?, ?, ?, ?)", (t, a_id, year, g_id))
            conn.commit()
        self.load_data()
        self.clear_entries()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_book_id = values[0]
        self.clear_entries()
        
        # Заполняем текстовые карточки книги без скобок и кавычек
        self.entry_title.insert(0, values[1])
        self.combo_author.insert(0, values[2])
        self.entry_year.insert(0, values[3] if values[3] != "None" else "")
        self.combo_genre.insert(0, values[4])

    def edit_book(self):
        if not self.selected_book_id:
            return
        t, a, y, g = self.entry_title.get().strip(), self.combo_author.get(), self.entry_year.get().strip(), self.combo_genre.get()
        try:
            year = int(y) if y else None
        except ValueError:
            return
            
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO authors (name) VALUES (?)", (a,))
            cursor.execute("SELECT id FROM authors WHERE name = ?", (a,))
            a_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (g,))
            cursor.execute("SELECT id FROM genres WHERE name = ?", (g,))
            g_id = cursor.fetchone()[0]
            
            cursor.execute("UPDATE books SET title=?, author_id=?, year=?, genre_id=? WHERE id=?", (t, a_id, year, g_id, self.selected_book_id))
            conn.commit()
        self.load_data()

    def delete_book(self):
        if not self.selected_book_id:
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранную книгу?"):
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id=?", (self.selected_book_id[0],))
                conn.commit()
            self.load_data()
            self.clear_entries()
            self.selected_book_id = None

    def search_books(self):
        # Получаем запрос в нижнем регистре
        q = self.entry_search.get().strip().lower()
        if not q:
            self.load_data()
            return

        crit_map = {"По названию": 1, "По автору": 2, "По жанру": 4}
        col_index = crit_map[self.combo_crit.get()]
        
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # Берем все книги из базы напрямую, без ломающих фильтров SQL
            cursor.execute("""
                SELECT books.id, books.title, authors.name, books.year, genres.name FROM books
                JOIN authors ON books.author_id = authors.id 
                JOIN genres ON books.genre_id = genres.id
                ORDER BY books.id DESC
            """)
            all_rows = cursor.fetchall()
            
        # Надежная регистронезависимая фильтрация силами самого Python
        filtered_rows = []
        for row in all_rows:
            if q in str(row[col_index]).lower():
                filtered_rows.append(row)
                
        self.load_data(filtered_rows)

    def show_stats(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total = cursor.fetchone()[0]
            cursor.execute("""
                SELECT genres.name, COUNT(books.id) FROM genres 
                LEFT JOIN books ON genres.id = books.genre_id 
                GROUP BY genres.name 
                ORDER BY COUNT(books.id) DESC
            """)
            genres = "\n".join([f" • {g}: {c} кн." for g, c in cursor.fetchall()])
        messagebox.showinfo("Статистика", f"Всего книг: {total}\n\nПо жанрам:\n{genres}")

    def make_report(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT genres.name, COUNT(books.id) FROM genres LEFT JOIN books ON genres.id = books.genre_id GROUP BY genres.name")
            genres_data = cursor.fetchall()
            cursor.execute("SELECT authors.name, COUNT(books.id) FROM authors JOIN books ON authors.id = books.author_id GROUP BY authors.name ORDER BY COUNT(books.id) DESC")
            authors_data = cursor.fetchall()
            cursor.execute("SELECT books.id, books.title, authors.name, books.year, genres.name FROM books JOIN authors ON books.author_id = authors.id JOIN genres ON books.genre_id = genres.id")
            all_books = cursor.fetchall()
            
        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Отчет библиотеки</title>
        <style>body{{font-family:Arial;margin:40px;background:#f8f9fa;}} .card{{background:white;padding:20px;margin-bottom:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.05);}} table{{width:100%;border-collapse:collapse;}} th,td{{border:1px solid #ddd;padding:10px;}} th{{background:#2c3e50;color:white;}}</style></head>
        <body><h1>Отчет: Домашняя библиотека</h1><p>Создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <div class='card'><h2>Всего книг: {total}</h2></div>
        <div class='card'><h2>По жанрам</h2><table><tr><th>Жанр</th><th>Количество</th></tr>"""
        for g, c in genres_data: 
            html += f"<tr><td>{g}</td><td>{c}</td></tr>"
        html += "</table></div><div class='card'><h2>По авторам</h2><table><tr><th>Автор</th><th>Книг</th></tr>"
        for a, c in authors_data: 
            html += f"<tr><td>{a}</td><td>{c}</td></tr>"
        html += "</table></div><div class='card'><h2>Все книги</h2><table><tr><th>ID</th><th>Название</th><th>Автор</th><th>Год</th><th>Жанр</th></tr>"
        for r in all_books: 
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
        html += "</table></div></body></html>"
        
        with open("library_report.html", "w", encoding="utf-8") as f: 
            f.write(html)
        messagebox.showinfo("Успех", "Отчет успешно создан!")

    def clear_entries(self):
        self.entry_title.delete(0, tk.END)
        self.combo_author.set("")
        self.entry_year.delete(0, tk.END)
        self.combo_genre.set("")

    def update_sort_headers(self):
        headers_text = {"ID": "ID", "Title": "Название книги", "Author": "Автор", "Year": "Год", "Genre": "Жанр"}
        p_col = getattr(self, 'primary_col', None)
        s_col = getattr(self, 'secondary_col', None)
        
        for col, base_text in headers_text.items():
            if p_col and col == p_col:
                # Используем стандартный надежный текст вместо графических стрелок
                arrow = " (вниз)" if self.sort_states[col] else " (вверх)"
                num = "" if s_col else ""
                new_text = f"{base_text}{arrow}{num}"
            elif s_col and col == s_col:
                arrow = " (вниз)" if self.sort_states[col] else " (вверх)"
                new_text = f"{base_text}{arrow}"
            else:
                new_text = base_text
                
            self.tree.heading(col, text=new_text, command=lambda c=col: self.sort_click(c))

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

