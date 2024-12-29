import sqlite3
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE = 'archaeology.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_name=DATABASE, owner="owner_name"):
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

@app.route('/archaeologists', methods=['GET'])
def get_archaeologists():
    conn = get_db_connection()
    archaeologists = conn.execute('SELECT * FROM Археологи').fetchall()
    conn.close()
    return jsonify([dict(row) for row in archaeologists])

@app.route('/archaeologists', methods=['POST'])
def create_archaeologist():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Археологи (ФИО, Зарплата, Специализация, Квалификация)
        VALUES (?, ?, ?, ?)
    """, (data['ФИО'], data['Зарплата'], data['Специализация'], data['Квалификация']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Археолог добавлен'}), 201

@app.route('/archaeologists/<int:id>', methods=['GET'])
def get_archaeologist(id):
    conn = get_db_connection()
    archaeologist = conn.execute('SELECT * FROM Археологи WHERE id = ?', (id,)).fetchone()
    conn.close()
    if archaeologist is None:
        return jsonify({'error': 'Археолог не найден'}), 404
    return jsonify(dict(archaeologist))

@app.route('/archaeologists/<int:id>', methods=['PUT'])
def update_archaeologist(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("""
        UPDATE Археологи
        SET ФИО = ?, Зарплата = ?, Специализация = ?, Квалификация = ?
        WHERE id = ?
    """, (data['ФИО'], data['Зарплата'], data['Специализация'], data['Квалификация'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Данные археолога обновлены'})

@app.route('/archaeologists/<int:id>', methods=['DELETE'])
def delete_archaeologist(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Археологи WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Археолог удален'})

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Предметы').fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Предметы (Название, Стоимость, Эпоха, Кому_принадлежал)
        VALUES (?, ?, ?, ?)
    """, (data['Название'], data['Стоимость'], data['Эпоха'], data['Кому_принадлежал']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Предмет добавлен'}), 201

@app.route('/items/<int:id>', methods=['GET'])
def get_item(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM Предметы WHERE id = ?', (id,)).fetchone()
    conn.close()
    if item is None:
        return jsonify({'error': 'Предмет не найден'}), 404
    return jsonify(dict(item))

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
