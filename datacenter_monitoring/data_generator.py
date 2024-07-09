import random
import time
from faker import Faker

fake = Faker()

def generate_data(equipment_types, interval=60):
    while True:
        # Генерация данных для каждого типа оборудования
        for equipment_type in equipment_types:
            data = {
                'type': equipment_type,
                'name': fake.name(),
                'temperature': random.uniform(20, 25),
                'humidity': random.uniform(40, 50),
                'cpu_load': random.uniform(20, 80),
                'ram_usage': random.uniform(30, 70),
                'disk_usage': random.uniform(40, 90)
            }

            # Создание события
            event = {
                'type': random.choice(['warning', 'error', 'reboot']),
                'message': fake.sentence(),
                'timestamp': time.time()
            }

            # Отправка данных в Xata
            yield data, event

        time.sleep(interval)