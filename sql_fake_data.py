import requests
import random
from faker import Faker
import time

BASE_URL = "http://127.0.0.1:5000"
fake = Faker()

def wait_for_server():
    retries = 5
    while retries > 0:
        try:
            response = requests.get(f"{BASE_URL}/items")
            if response.status_code == 200:
                print("Сервер запущен.")
                return True
        except requests.ConnectionError:
            pass
        retries -= 1
        print("Ожидание запуска сервера...")
        time.sleep(2)
    print("Не удалось подключиться к серверу.")
    return False

def add_archaeologists(count=10):
    url = f"{BASE_URL}/archaeologists"
    success_count = 0
    for _ in range(count):
        data = {
            "ФИО": fake.name(),
            "Зарплата": round(random.uniform(40000, 100000), 2),
            "Специализация": random.choice(["Египтология", "Антропология", "Археозоология"]),
            "Квалификация": random.choice(["Доктор", "Кандидат наук", "Магистр"])
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                success_count += 1
            else:
                print(f"Ошибка при добавлении археолога: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
    print(f"Добавлено археологов: {success_count}/{count}")

def add_items(count=10):
    url = f"{BASE_URL}/items"
    success_count = 0
    for _ in range(count):
        data = {
            "Название": fake.word().capitalize(),
            "Стоимость": round(random.uniform(1000, 50000), 2),
            "Эпоха": random.choice(["Древний Рим", "Средневековье", "Неолит"]),
            "Кому_принадлежал": random.choice(["Неизвестно", "Частное лицо", fake.name()])
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                success_count += 1
            else:
                print(f"Ошибка при добавлении предмета: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
    print(f"Добавлено предметов: {success_count}/{count}")

def add_findings(count=10):
    url_archaeologists = f"{BASE_URL}/archaeologists"
    url_items = f"{BASE_URL}/items"
    url_findings = f"{BASE_URL}/findings"

    archaeologists = requests.get(url_archaeologists)
    items = requests.get(url_items)

    try:
        archaeologists_data = archaeologists.json()
        items_data = items.json()
    except ValueError:
        print("Ошибка: Сервер вернул не JSON данные.")
        return

    if not archaeologists_data or not items_data:
        print("Необходимо сначала добавить археологов и предметы!")
        return

    success_count = 0
    for _ in range(count):
        data = {
            "Археолог_id": random.choice(archaeologists_data)['id'],
            "Предмет_id": random.choice(items_data)['id'],
            "Место": fake.city(),
            "Дата": fake.date(),
            "Состояние": random.choice(["Хорошее", "Среднее", "Плохое"]),
            "Тип": random.choice(["Фрагмент", "Целое изделие", "Реконструкция"])
        }
        try:
            response = requests.post(url_findings, json=data)
            if response.status_code == 201:
                success_count += 1
            else:
                print(f"Ошибка при добавлении находки: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
    print(f"Добавлено находок: {success_count}/{count}")



def populate_database():
    if not wait_for_server():
        return
    print("Добавляем археологов...")
    add_archaeologists(10)

    print("Добавляем предметы...")
    add_items(10)

    print("Добавляем находки...")
    add_findings(10)

if __name__ == "__main__":
    populate_database()
