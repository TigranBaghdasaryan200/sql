import sqlite3
import os

def initialize_database(db_name="archaeology.db", owner="owner_name"):
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE Археологи (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ФИО TEXT NOT NULL,
            Зарплата REAL,
            Специализация TEXT,
            Квалификация TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE Предметы (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Название TEXT NOT NULL,
            Стоимость REAL,
            Эпоха TEXT,
            Кому_принадлежал TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE Находки (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Археолог_id INTEGER NOT NULL,
            Предмет_id INTEGER NOT NULL,
            Место TEXT,
            Дата TEXT,
            Состояние TEXT,
            Тип TEXT,
            FOREIGN KEY (Археолог_id) REFERENCES Археологи(id),
            FOREIGN KEY (Предмет_id) REFERENCES Предметы(id)
        );
    """)

    cursor.execute(f"PRAGMA user_version = 1;")
    cursor.execute(f"-- Database owner: {owner}")

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' initialized successfully with owner '{owner}'.")

if __name__ == "__main__":
    initialize_database()
