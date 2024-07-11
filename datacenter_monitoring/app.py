import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from data_generator import generate_data
from models import User, Equipment, Event
from utils import send_email
import plotly.graph_objects as go
import plotly  # Import plotly

import config
import os
import psycopg2
import threading

app = Flask(__name__)
app.config.from_object(config)
# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модели пользователей
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    @login_manager.user_loader
    def load_user(user_id):
        # Получение пользователя из Postgres
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
            user = cur.fetchone()
            conn.close()
        if user:
            return User(user[0], user[1], user[2])  # Индексы в соответствии с столбцами в таблице 'users'
        return None


# Маршруты

@app.route('/')
@login_required
def index():
    # Получение данных из Postgres
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM equipment")
        equipment_data = cur.fetchall()
        cur.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 10")
        events_data = cur.fetchall()
        conn.close()

    # Преобразование данных оборудования в список словарей
    equipment_data_as_dicts = [
        {
            'id': equipment[0],
            'type': equipment[1],
            'name': equipment[2],
            'temperature': equipment[3],
            'humidity': equipment[4],
            'cpu_load': equipment[5],
            'ram_usage': equipment[6],
            'disk_usage': equipment[7],
        } for equipment in equipment_data
    ]

    temp_graph = create_temperature_graph(equipment_data_as_dicts)
    cpu_graph = create_cpu_graph(equipment_data_as_dicts)


    temp_data = [equipment['temperature'] for equipment in equipment_data_as_dicts]
    cpu_data = [equipment['cpu_load'] for equipment in equipment_data_as_dicts]

    return render_template('index.html', equipment=equipment_data_as_dicts, temp_data=temp_data, cpu_data=cpu_data)

     



    # Передача данных в шаблон


@app.route('/equipment/<equipment_id>')
@login_required
def equipment_details(equipment_id):
    # Получение данных о конкретном оборудовании
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM equipment WHERE id = '{equipment_id}'")
        equipment_data = cur.fetchone()
        conn.close()
    # Преобразование данных в словарь для удобства использования
    equipment_data = {
        'id': equipment_data[0],
        'type': equipment_data[1],
        'name': equipment_data[2],
        'temperature': equipment_data[3],
        'humidity': equipment_data[4],
        'cpu_load': equipment_data[5],
        'ram_usage': equipment_data[6],
        'disk_usage': equipment_data[7],
    }
    return render_template('equipment.html', equipment=equipment_data)

@app.route('/events')
@login_required
def events():
    # Получение данных о событиях
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM events ORDER BY timestamp DESC")
        events_data = cur.fetchall()
        conn.close()

    # Преобразование данных событий в список словарей
    events_data_as_dicts = [
        {
            'id': event[0],
            'type': event[1],
            'message': event[2],
            'timestamp': event[3],
        } for event in events_data
    ]

    return render_template('events.html', events=events_data_as_dicts) 


@app.route('/user_management')
@login_required
def user_management():
    # Получение данных о пользователях
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        users_data = cur.fetchall()
        conn.close()

    # Преобразуем данные в список словарей 
    users_data_as_dicts = [
        {
            'id': user[0],
            'username': user[1],
            'role': user[2],
        } for user in users_data
    ]

    return render_template('user_management.html', users=users_data_as_dicts) 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Аутентификация пользователя
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
            user = cur.fetchone()
            conn.close()
        if user:
            user = User(user[0], user[1], user[2])  # Индексы в соответствии с столбцами в таблице 'users'
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Неверный логин или пароль'

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Создание нового пользователя
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO users (username, password, role) VALUES ('{username}', '{password}', '{role}')")
            conn.commit()
            conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/settings')
@login_required
def settings():
    # Получение настроек из Postgres
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM settings WHERE id = 1")
        settings_data = cur.fetchone()
        conn.close()
    return render_template('settings.html', settings=settings_data)

@app.route('/settings', methods=['POST'])
@login_required
def update_settings():
    # Обновление настроек в Postgres
    email_sender = request.form['email_sender']
    email_password = request.form['email_password']
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE settings SET email_sender = '{email_sender}', email_password = '{email_password}' WHERE id = 1")
        conn.commit()
        conn.close()
    return redirect(url_for('settings'))

# Функции для визуализации
def create_temperature_graph(equipment_data):
    # Сбор данных о температуре
    temps = [equipment['temperature'] for equipment in equipment_data]

    # Создание графика
    fig = go.Figure(data=[go.Scatter(x=list(range(len(temps))), y=temps)])
    fig.update_layout(title='Температура', xaxis_title='Время', yaxis_title='Температура (°C)')
    return fig

def create_cpu_graph(equipment_data):
    # Сбор данных о загрузке CPU
    cpu_loads = [equipment['cpu_load'] for equipment in equipment_data]

    # Создание графика
    fig = go.Figure(data=[go.Scatter(x=list(range(len(cpu_loads))), y=cpu_loads)])
    fig.update_layout(title='Загрузка CPU', xaxis_title='Время', yaxis_title='Загрузка (%)')
    return fig

def connect_to_postgres():
    conn_str = f"postgresql://f7mc9j:xau_644tECdUHtb10oWbZBVVA2xpCT6zAwne@eu-central-1.sql.xata.sh:5432/DataCheap:main?sslmode=require"
    conn = psycopg2.connect(conn_str, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("SET NAMES 'utf8'")  # Set the client encoding to UTF-8
    return conn
@app.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Получение данных о пользователе из Postgres
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
        user_data = cur.fetchone()
        conn.close()

    # Если пользователь не найден, перенаправляем на управление пользователями
    if not user_data:
        return redirect(url_for('user_management'))

    if request.method == 'POST':
        # Обновление данных пользователя в Postgres
        username = request.form['username']
        role = request.form['role']
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute(f"UPDATE users SET username = '{username}', role = '{role}' WHERE id = '{user_id}'")
            conn.commit()
            conn.close()
        return redirect(url_for('user_management'))

    return render_template('edit_user.html', user=user_data)

@app.route('/delete_user/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    # Удаление пользователя из Postgres
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM users WHERE id = '{user_id}'")
        conn.commit()
        conn.close()
    return '', 204  # Пустой ответ с кодом 204 (No Content)


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)

