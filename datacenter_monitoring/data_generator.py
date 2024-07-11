import random
import time
from faker import Faker

fake = Faker()

def generate_data(equipment_types, intervals=None, ranges=None):
    """
    Генератор данных о ЦОДе.

    Args:
        equipment_types (list): Список типов оборудования.
        intervals (dict): Словарь с интервалами генерации для каждого типа
            оборудования. Ключ - тип оборудования, значение - интервал в секундах.
        ranges (dict): Словарь с диапазонами значений для каждого типа
            оборудования. Ключ - тип оборудования, значение - словарь с
            диапазонами для каждой метрики.

    Yields:
        tuple: Кортеж из словаря с данными об оборудовании и словаря с событием.
    """
    if intervals is None:
        intervals = {}
    if ranges is None:
        ranges = {}

    while True:
        for equipment_type in equipment_types:
            # Интервал генерации
            interval = intervals.get(equipment_type, 60)

            # Диапазоны значений
            type_ranges = ranges.get(equipment_type, {
                'temperature': (20, 25),
                'humidity': (40, 50),
                'cpu_load': (20, 80),
                'ram_usage': (30, 70),
                'disk_usage': (40, 90)
            })

            # Генерация данных для оборудования
            data = {
                'type': equipment_type,
                'name': fake.name(),
                'temperature': random.uniform(*type_ranges['temperature']),
                'humidity': random.uniform(*type_ranges['humidity']),
                'cpu_load': random.uniform(*type_ranges['cpu_load']),
                'ram_usage': random.uniform(*type_ranges['ram_usage']),
                'disk_usage': random.uniform(*type_ranges['disk_usage'])
            }

            # Создание события
            event = {
                'type': random.choice(['warning', 'error', 'reboot']),
                'message': fake.sentence(),
                'timestamp': time.time(),
                'equipment_id': data['id']  # Добавлено поле equipment_id
            }

            yield data, event

        time.sleep(interval)
