from flask import Blueprint, request, render_template, redirect, url_for
from .models import db, Client, Order
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/clients')
def client_list():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@bp.route('/orders')
def order_list():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@bp.route('/add-client', methods=['POST'])
def add_client():
    data = request.form
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
    return redirect(url_for('routes.client_list'))

@bp.route('/add-order', methods=['POST'])
def add_order():
    data = request.form
    order = Order(
        amount=float(data.get('amount', 0)),
        status=data.get('status', 'в работе'),
        client_id=int(data.get('client_id'))
    )
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('routes.order_list'))