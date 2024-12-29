import requests
import random
from faker import Faker

BASE_URL = "http://127.0.0.1:5000"


fake = Faker()


def add_archaeologists(count=10):
    url = f"{BASE_URL}/archaeologists"
    for _ in range(count):
        data = {
            "ФИО": fake.name(),
            "Зарплата": round(random.uniform(40000, 100000), 2),
            "Специализация": random.choice(["Египтология", "Антропология", "Археозоология"]),
            "Квалификация": random.choice(["Доктор", "Кандидат наук", "Магистр"])
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"Добавлен археолог: {data['ФИО']}")
        else:
            print(f"Ошибка при добавлении археолога: {response.json()}")

def add_items(count=10):
    url = f"{BASE_URL}/items"
    for _ in range(count):
        data = {
            "Название": fake.word().capitalize(),
            "Стоимость": round(random.uniform(1000, 50000), 2),
            "Эпоха": random.choice(["Древний Рим", "Средневековье", "Неолит"]),
            "Кому_принадлежал": random.choice(["Неизвестно", "Частное лицо", fake.name()])
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"Добавлен предмет: {data['Название']}")
        else:
            print(f"Ошибка при добавлении предмета: {response.json()}")

def add_findings(count=10):
    url_archaeologists = f"{BASE_URL}/archaeologists"
    url_items = f"{BASE_URL}/items"
    url_findings = f"{BASE_URL}/findings"

    archaeologists = requests.get(url_archaeologists).json()
    items = requests.get(url_items).json()

    if not archaeologists or not items:
        print("Необходимо сначала добавить археологов и предметы!")
        return

    for _ in range(count):
        data = {
            "Археолог_id": random.choice(archaeologists)['id'],
            "Предмет_id": random.choice(items)['id'],
            "Место": fake.city(),
            "Дата": fake.date(),
            "Состояние": random.choice(["Хорошее", "Среднее", "Плохое"]),
            "Тип": random.choice(["Фрагмент", "Целое изделие", "Реконструкция"])
        }
        response = requests.post(url_findings, json=data)
        if response.status_code == 201:
            print(f"Добавлена находка: Археолог {data['Археолог_id']}, Предмет {data['Предмет_id']}")
        else:
            print(f"Ошибка при добавлении находки: {response.json()}")

def populate_database():
    print("Добавляем археологов...")
    add_archaeologists(20)

    print("Добавляем предметы...")
    add_items(20)

    print("Добавляем находки...")
    add_findings(30)

if __name__ == "__main__":
    populate_database()
