class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

class Equipment:
    def __init__(self, id, type, name, temperature, humidity, cpu_load, ram_usage, disk_usage):
        self.id = id
        self.type = type
        self.name = name
        self.temperature = temperature
        self.humidity = humidity
        self.cpu_load = cpu_load
        self.ram_usage = ram_usage
        self.disk_usage = disk_usage

class Event:
    def __init__(self, id, type, message, timestamp, equipment_id):
        self.id = id
        self.type = type
        self.message = message
        self.timestamp = timestamp
        self.equipment_id = equipment_id
