import sqlite3
import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
DATABASE = 'archaeology.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise

def initialize_database(db_name=DATABASE, owner="owner_name"):
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Археологи (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ФИО TEXT NOT NULL,
            Зарплата REAL,
            Специализация TEXT,
            Квалификация TEXT
        );
    """)
    print("Таблица 'Археологи' успешно создана.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Предметы (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Название TEXT NOT NULL,
            Стоимость REAL,
            Эпоха TEXT,
            Кому_принадлежал TEXT
        );
    """)
    print("Таблица 'Предметы' успешно создана.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Находки (
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
    print("Таблица 'Находки' успешно создана.")

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' initialized successfully with owner '{owner}'.")

@app.before_request
def log_request():
    print(f"Получен запрос: {request.method} {request.path}")

# SELECT ... WHERE (с несколькими условиями)
@app.route('/archaeologists/filter', methods=['GET'])
def filter_archaeologists():
    min_salary = request.args.get('min_salary', default=0, type=float)
    specialization = request.args.get('specialization', default='', type=str)

    conn = get_db_connection()
    query = """
        SELECT * FROM Археологи
        WHERE Зарплата > ? AND Специализация = ?
    """
    archaeologists = conn.execute(query, (min_salary, specialization)).fetchall()
    conn.close()

    return jsonify([dict(row) for row in archaeologists])

# JOIN
@app.route('/findings/details', methods=['GET'])
def get_findings_with_details():
    conn = get_db_connection()
    query = """
        SELECT Находки.id, Археологи.ФИО AS Археолог, Предметы.Название AS Предмет, 
               Находки.Место, Находки.Дата, Находки.Состояние
        FROM Находки
        JOIN Археологи ON Находки.Археолог_id = Археологи.id
        JOIN Предметы ON Находки.Предмет_id = Предметы.id
    """
    findings = conn.execute(query).fetchall()
    conn.close()

    return jsonify([dict(row) for row in findings])

# UPDATE с нетривиальным условием
@app.route('/findings/update-condition', methods=['PUT'])
def update_findings_condition():
    conn = get_db_connection()
    query = """
        UPDATE Находки
        SET Состояние = 'Архивное'
        WHERE Дата < date('now', '-5 years')
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

    return jsonify({'message': f'Обновлено {updated_rows} записей'}), 200

# GROUP BY
@app.route('/findings/group-by-archaeologist', methods=['GET'])
def group_findings_by_archaeologist():
    conn = get_db_connection()
    query = """
        SELECT Археологи.ФИО AS Археолог, COUNT(Находки.id) AS Количество_находок
        FROM Находки
        JOIN Археологи ON Находки.Археолог_id = Археологи.id
        GROUP BY Находки.Археолог_id
    """
    result = conn.execute(query).fetchall()
    conn.close()

    return jsonify([dict(row) for row in result])

# Сортировка выдачи результатов
@app.route('/items/sorted', methods=['GET'])
def get_sorted_items():
    sort_field = request.args.get('sort_by', default='Стоимость', type=str)
    sort_order = request.args.get('order', default='ASC', type=str).upper()

    if sort_field not in ['Название', 'Стоимость', 'Эпоха']:
        return jsonify({'error': 'Invalid sort field'}), 400
    if sort_order not in ['ASC', 'DESC']:
        return jsonify({'error': 'Invalid sort order'}), 400

    conn = get_db_connection()
    query = f"""
        SELECT * FROM Предметы
        ORDER BY {sort_field} {sort_order}
    """
    items = conn.execute(query).fetchall()
    conn.close()

    return jsonify([dict(row) for row in items])

@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_db_connection()
        items = conn.execute('SELECT * FROM Предметы').fetchall()
        conn.close()
        return jsonify([dict(row) for row in items])
    except sqlite3.Error as e:
        return jsonify({'error': f'Ошибка базы данных: {e}'}), 500

@app.route('/archaeologists', methods=['POST'])
def create_archaeologist():
    try:
        data = request.get_json()
        if not data or 'ФИО' not in data or 'Зарплата' not in data:
            return jsonify({'error': 'Некорректные данные'}), 400
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO Археологи (ФИО, Зарплата, Специализация, Квалификация)
            VALUES (?, ?, ?, ?)
        """, (data['ФИО'], data['Зарплата'], data.get('Специализация'), data.get('Квалификация')))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Археолог добавлен'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': f'Ошибка базы данных: {e}'}), 500

@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        if not data or 'Название' not in data or 'Стоимость' not in data:
            return jsonify({'error': 'Некорректные данные'}), 400
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO Предметы (Название, Стоимость, Эпоха, Кому_принадлежал)
            VALUES (?, ?, ?, ?)
        """, (data['Название'], data['Стоимость'], data.get('Эпоха'), data.get('Кому_принадлежал')))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Предмет добавлен'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': f'Ошибка базы данных: {e}'}), 500


if __name__ == '__main__':
    initialize_database()
    from threading import Thread
    def run_flask_app():
        app.run(debug=True, use_reloader=False)
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    import time
    time.sleep(1)

    # Примеры использования
    try:
        response = requests.get('http://127.0.0.1:5000/archaeologists/filter', params={
            'min_salary': 50000,
            'specialization': 'Египтология'
        })
        print("Фильтрация археологов:", response.json())

        response = requests.get('http://127.0.0.1:5000/findings/details')
        print("Детали находок:", response.json())

        response = requests.put('http://127.0.0.1:5000/findings/update-condition')
        print("Обновление состояния находок:", response.json())

        response = requests.get('http://127.0.0.1:5000/findings/group-by-archaeologist')
        print("Группировка находок:", response.json())

        response = requests.get('http://127.0.0.1:5000/items/sorted', params={
            'sort_by': 'Стоимость',
            'order': 'DESC'
        })
        print("Сортировка предметов:", response.json())
    except requests.ConnectionError as e:
        print(f"Ошибка подключения к серверу Flask: {e}")
