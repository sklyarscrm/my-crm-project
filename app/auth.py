from flask import Blueprint, request, render_template, redirect, url_for, session

bp = Blueprint('auth', __name__)

# Простейшая авторизация — один логин и пароль
VALID_USERNAME = 'admin'
VALID_PASSWORD = '1234'

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('routes.index'))
        else:
            return render_template('login.html', error='Неверные данные')
    return render_template('login.html')

@bp.before_app_request
def require_login():
    allowed_routes = ['auth.login', 'static']
    if not session.get('logged_in') and request.endpoint not in allowed_routes:
        return redirect(url_for('auth.login'))

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('auth.login'))