import random
import time
import datetime
from faker import Faker
import psycopg2
import config

fake = Faker()

def generate_equipment_data(equipment_type, count, ranges=None):
    """Генерирует данные об оборудовании."""
    if ranges is None:
        ranges = {
            'temperature': (20, 25),
            'humidity': (40, 50),
            'cpu_load': (20, 80),
            'ram_usage': (30, 70),
            'disk_usage': (40, 90)
        }

    data = []
    for _ in range(count):
        equipment = {
            'id': fake.uuid4(),
            'type': equipment_type,
            'name': f"{equipment_type} {fake.word()} {fake.random_int(1, 100)}",
            'temperature': round(random.uniform(*ranges['temperature']), 2),
            'humidity': round(random.uniform(*ranges['humidity']), 2),
            'cpu_load': round(random.uniform(*ranges['cpu_load']), 2),
            'ram_usage': round(random.uniform(*ranges['ram_usage']), 2),
            'disk_usage': round(random.uniform(*ranges['disk_usage']), 2)
        }
        data.append(equipment)
    return data

def generate_events(equipment_data, count, event_types=['warning', 'error', 'reboot']):
    """Генерирует данные о событиях."""
    events = []
    for _ in range(count):
        equipment_id = random.choice(equipment_data)['id']
        event = {
            'id': fake.uuid4(),
            'type': random.choice(event_types),
            'message': fake.sentence(),
            'timestamp': int(time.time() - random.randint(0, 3600 * 24 * 30)),  # Случайное время за последние 30 дней
            'equipment_id': equipment_id
        }
        events.append(event)
    return events

def generate_users(count, roles=['user', 'engineer', 'admin']):
    """Генерирует данные о пользователях."""
    users = []
    for _ in range(count):
        user = {
            'id': fake.uuid4(),
            'username': fake.user_name(),
            'password': fake.password(),
            'role': random.choice(roles)
        }
        users.append(user)
    return users

def generate_settings():
    """Генерирует данные о настройках."""
    settings = {
        'id': 'settings_id',
        'email_sender': 'your_email@example.com',
        'email_password': 'your_password'
    }
    return settings

def print_data(data, table_name):
    """Печатает данные в формате SQL."""
    print(f"INSERT INTO {table_name} VALUES")
    for row in data:
        values = ', '.join(f"'{value}'" for value in row.values())
        print(f"({values}),")

def update_equipment_data(conn, equipment_id, new_data):
    """Обновляет данные об оборудовании в базе данных."""
    with conn.cursor() as cur:
        # Используйте prepared statements для предотвращения SQL injection
        cur.execute(
            "UPDATE equipment SET temperature = %s, humidity = %s, cpu_load = %s, ram_usage = %s, disk_usage = %s WHERE id = %s",
            (new_data['temperature'], new_data['humidity'], new_data['cpu_load'], new_data['ram_usage'], new_data['disk_usage'], equipment_id)
        )
        conn.commit()

def simulate_data_changes(conn):
    """Эмулирует изменение данных об оборудовании."""
    while True:
        # Получаем список ID оборудования из базы данных
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM equipment")
            equipment_ids = [row[0] for row in cur.fetchall()]

        # Случайно выбираем оборудование для изменения
        equipment_id = random.choice(equipment_ids)

        # Генерируем новые данные
        new_data = {
            'temperature': round(random.uniform(20, 25), 2),
            'humidity': round(random.uniform(40, 50), 2),
            'cpu_load': round(random.uniform(20, 80), 2),
            'ram_usage': round(random.uniform(30, 70), 2),
            'disk_usage': round(random.uniform(40, 90), 2)
        }

        # Обновляем данные в базе данных
        update_equipment_data(conn, equipment_id, new_data)

        print(f"Обновлены данные для оборудования с ID: {equipment_id}")

        # Ждем случайное время
        time.sleep(random.randint(5, 15))

if __name__ == '__main__':
    # Создаем соединение с PostgreSQL
    conn = psycopg2.connect("postgresql://f7mc9j:xau_644tECdUHtb10oWbZBVVA2xpCT6zAwne@eu-central-1.sql.xata.sh:5432/DataCheap:main?sslmode=require", connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("SET NAMES 'utf8'")  # Устанавливаем кодировку UTF-8

    # Запускаем эмуляцию изменения данных
    simulate_data_changes(conn)

    # Закрываем соединение
    conn.close()
