from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from xata import Client
from data_generator import generate_data
from models import User, Equipment, Event
from utils import send_email
import plotly.graph_objects as go
import config

app = Flask(__name__)
app.config.from_object(config)

# Xata Client
xata_client = Client(api_key=config.XATA_API_KEY, database_name=config.XATA_DATABASE_NAME)

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
        # Получение пользователя из Xata
        user = xata_client.collection('users').find_one(user_id)
        if user:
            return User(user['id'], user['username'], user['role'])
        return None

# Маршруты

@app.route('/')
@login_required
def index():
    # Получение данных из Xata
    equipment_data = xata_client.collection('equipment').find()
    events_data = xata_client.collection('events').find().sort('timestamp', 'desc').limit(10)

    # Визуализация данных
    temp_graph = create_temperature_graph(equipment_data)
    cpu_graph = create_cpu_graph(equipment_data)

    # Передача данных в шаблон
    return render_template('index.html', equipment=equipment_data, events=events_data, temp_graph=temp_graph, cpu_graph=cpu_graph)

@app.route('/equipment/<equipment_id>')
@login_required
def equipment_details(equipment_id):
    # Получение данных о конкретном оборудовании
    equipment_data = xata_client.collection('equipment').find_one(equipment_id)
    return render_template('equipment.html', equipment=equipment_data)

@app.route('/events')
@login_required
def events():
    # Получение данных о событиях
    events_data = xata_client.collection('events').find().sort('timestamp', 'desc')
    return render_template('events.html', events=events_data)

@app.route('/user_management')
@login_required
def user_management():
    # Получение данных о пользователях
    users_data = xata_client.collection('users').find()
    return render_template('user_management.html', users=users_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Аутентификация пользователя
        user = xata_client.collection('users').find_one({'username': username, 'password': password})
        if user:
            user = User(user['id'], user['username'], user['role'])
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
        xata_client.collection('users').create({'username': username, 'password': password, 'role': role})
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/settings')
@login_required
def settings():
    # Получение настроек из Xata
    settings_data = xata_client.collection('settings').find_one({'id': 1})
    return render_template('settings.html', settings=settings_data)

@app.route('/settings', methods=['POST'])
@login_required
def update_settings():
    # Обновление настроек в Xata
    xata_client.collection('settings').update({'id': 1}, {'email_sender': request.form['email_sender'], 'email_password': request.form['email_password']})
    return redirect(url_for('settings'))

# Функции для визуализации
def create_temperature_graph(equipment_data):
    # Сбор данных о температуре
    temps = []
    for equipment in equipment_data:
        temps.append(equipment['temperature'])

    # Создание графика
    fig = go.Figure(data=[go.Scatter(x=list(range(len(temps))), y=temps)])
    fig.update_layout(title='Температура', xaxis_title='Время', yaxis_title='Температура (°C)')
    return fig

def create_cpu_graph(equipment_data):
    # Сбор данных о загрузке CPU
    cpu_loads = []
    for equipment in equipment_data:
        cpu_loads.append(equipment['cpu_load'])

    # Создание графика
    fig = go.Figure(data=[go.Scatter(x=list(range(len(cpu_loads))), y=cpu_loads)])
    fig.update_layout(title='Загрузка CPU', xaxis_title='Время', yaxis_title='Загрузка (%)')
    return fig

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)