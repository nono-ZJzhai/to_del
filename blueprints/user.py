from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models.user import User
from exts import db

bp = Blueprint('user', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('front.index'))
        else:
            return render_template('user/login.html', error='用户名或密码错误')
    return render_template('user/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('front.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('user/register.html', error='用户名已存在')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.login'))
    return render_template('user/register.html')