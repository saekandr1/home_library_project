import sqlite3
import os
from datetime import datetime

DB_NAME = "home_library.db"

def init_db():
    """Инициализация базы данных SQLite."""
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

def add_book(title, author, year, genre):
    """Добавление новой книги."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, year, genre) VALUES (?, ?, ?, ?)",
            (title, author, year, genre)
        )
        conn.commit()
    print(f"\n[Успех] Книга '{title}' успешно добавлена!")

def delete_book(book_id):
    """Удаление книги по ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            print(f"\n[Успех] Книга '{row[0]}' (ID: {book_id}) удалена.")
        else:
            print("\n[Ошибка] Книга с таким ID не найдена.")

def edit_book(book_id, title=None, author=None, year=None, genre=None):
    """Редактирование информации о книге."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            print("\n[Ошибка] Книга с таким ID не найдена.")
            return

        fields = []
        values = []
        if title: fields.append("title = ?"); values.append(title)
        if author: fields.append("author = ?"); values.append(author)
        if year: fields.append("year = ?"); values.append(year)
        if genre: fields.append("genre = ?"); values.append(genre)

        if not fields:
            print("\n[Инфо] Изменения не внесены, так как поля не заполнены.")
            return

        values.append(book_id)
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        print(f"\n[Успех] Данные книги с ID {book_id} обновлены!")

def search_books(query, criteria="title"):
    """Поиск книг по различным критериям (title, author, genre)."""
    allowed_criteria = {"title", "author", "genre"}
    if criteria not in allowed_criteria:
        criteria = "title"

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        sql_query = f"SELECT id, title, author, year, genre FROM books WHERE {criteria} LIKE ?"
        cursor.execute(sql_query, (f"%{query}%",))
        rows = cursor.fetchall()
        
        print(f"\n--- Результаты поиска по запросу '{query}' ({criteria}) ---")
        if not rows:
            print("Ничего не найдено.")
        for row in rows:
            print(f"ID: {row[0]} | '{row[1]}' — {row[2]} ({row[3]} г.) | Жанр: {row[4]}")

def display_all_books():
    """Вывод списка всех книг."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, year, genre FROM books")
        rows = cursor.fetchall()
        print("\n--- Список всех книг ---")
        if not rows:
            print("Библиотека пуста.")
        for row in rows:
            print(f"ID: {row[0]} | '{row[1]}' — {row[2]} ({row[3]} г.) | Жанр: {row[4]}")

def get_statistics():
    """Получение статистики по жанрам и авторам."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
        genres_stat = cursor.fetchall()
        
        cursor.execute("SELECT author, COUNT(*) FROM books GROUP BY author")
        authors_stat = cursor.fetchall()
        
    return total_books, genres_stat, authors_stat

def generate_html_report():
    """
    Генерация отчета в формате HTML.
    (Код структуры шаблона сгенерирован с помощью ИИ-ассистента по ТЗ)
    """
    total, genres, authors = get_statistics()
    report_name = "library_report.html"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Отчет по домашней библиотеке</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }}
        h1, h2 {{ color: #2c3e50; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Отчет по домашней библиотеке</h1>
    <p>Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
    
    <div class="card">
        <h2>Общая статистика</h2>
        <p><strong>Всего книг в базе данных:</strong> {total}</p>
    </div>

    <div class="card">
        <h2>Книги по жанрам</h2>
        <table>
            <tr><th>Жанр</th><th>Количество книг</th></tr>
    """
    for genre, count in genres:
        html_content += f"<tr><td>{genre if genre else 'Не указан'}</td><td>{count}</td></tr>"
        
    html_content += """
        </table>
    </div>

    <div class="card">
        <h2>Книги по авторам</h2>
        <table>
            <tr><th>Автор</th><th>Количество книг</th></tr>
    """
    for author, count in authors:
        html_content += f"<tr><td>{author}</td><td>{count}</td></tr>"
        
    html_content += """
        </table>
    </div>
</body>
</html>
    """
    with open(report_name, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n[Успех] HTML-отчет успешно сохранен в файл: {os.path.abspath(report_name)}")

def main_menu():
    """Главный цикл консольного интерфейса."""
    init_db()
    while True:
        print("\n======= ДОМАШНЯЯ БИБЛИОТЕКА =======")
        print("1. Показать все книги")
        print("2. Добавить книгу")
        print("3. Удалить книгу")
        print("4. Редактировать книгу")
        print("5. Поиск книги")
        print("6. Показать статистику")
        print("7. Сгенерировать HTML-отчет")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            display_all_books()
        elif choice == "2":
            title = input("Введите название книги: ")
            author = input("Введите автора: ")
            try:
                year = int(input("Введите год издания: "))
            except ValueError:
                year = None
            genre = input("Введите жанр: ")
            add_book(title, author, year, genre)
        elif choice == "3":
            try:
                book_id = int(input("Введите ID книги для удаления: "))
                delete_book(book_id)
            except ValueError:
                print("[Ошибка] ID должен быть числом.")
        elif choice == "4":
            try:
                book_id = int(input("Введите ID книги для редактирования: "))
                print("Оставьте поле пустым, если не хотите его менять.")
                title = input("Новое название: ") or None
                author = input("Новый автор: ") or None
                year_in = input("Новый год: ")
                year = int(year_in) if year_in else None
                genre = input("Новый жанр: ") or None
                edit_book(book_id, title, author, year, genre)
            except ValueError:
                print("[Ошибка] Некорректный ввод числовых данных.")
        elif choice == "5":
            print("Критерии поиска: 1 - По названию, 2 - По автору, 3 - По жанру")
            c_choice = input("Выберите критерий (1-3): ").strip()
            crit_map = {"1": "title", "2": "author", "3": "genre"}
            criteria = crit_map.get(c_choice, "title")
            query = input("Введите строку поиска: ")
            search_books(query, criteria)
        elif choice == "6":
            total, genres, authors = get_statistics()
            print(f"\n--- Статистика библиотеки ---")
            print(f"Всего книг: {total}")
            print("\nПо жанрам:")
            for g, c in genres: print(f" - {g}: {c}")
            print("\nПо авторам:")
            for a, c in authors: print(f" - {a}: {c}")
        elif choice == "7":
            generate_html_report()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("[Ошибка] Неверный пункт меню.")

if __name__ == "__main__":
    main_menu()
