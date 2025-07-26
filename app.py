from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Создаём Flask приложение с указанием папки шаблонов
app = Flask(__name__, template_folder=os.path.join(basedir, 'app', 'templates'))

# Включаем автообновление шаблонов и отключаем кеш статики (для разработки)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель Клиента
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    messengers = db.Column(db.String(150))
    region = db.Column(db.String(100))
    client_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    orders = db.relationship('Order', backref='client', lazy=True)

# Модель Заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# API Клиентов
@app.route('/api/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'GET':
        clients = Client.query.all()
        return jsonify([{
            'id': c.id,
            'fio': c.fio,
            'phone': c.phone,
            'messengers': c.messengers,
            'region': c.region,
            'client_type': c.client_type,
            'status': c.status
        } for c in clients])

    data = request.json
    client = Client(
        fio=data.get('fio'),
        phone=data.get('phone'),
        messengers=data.get('messengers'),
        region=data.get('region'),
        client_type=data.get('client_type'),
        status=data.get('status', 'новый')
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'Клиент добавлен', 'id': client.id})

# API Заказов
@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        return jsonify([{
            'id': o.id,
            'date': o.date.isoformat(),
            'amount': o.amount,
            'status': o.status,
            'client_id': o.client_id,
            'client_fio': o.client.fio
        } for o in orders])

    data = request.json
    order = Order(
        date=datetime.fromisoformat(data.get('date')) if data.get('date') else datetime.utcnow(),
        amount=data.get('amount'),
        status=data.get('status', 'в работе'),
        client_id=data.get('client_id')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Заказ добавлен', 'id': order.id})

# API Воронки продаж
@app.route('/api/pipeline')
def pipeline():
    stages = ["Заявка", "Переговоры", "Счёт", "Оплата", "Доставка"]
    result = []
    for stage in stages:
        count = Order.query.filter_by(status=stage).count()
        result.append({'stage': stage, 'count': count})
    return jsonify(result)

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Запуск приложения на порту {port}")
    app.run(host='0.0.0.0', port=port)