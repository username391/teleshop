import json
import random
import flask_admin


from flask import Flask, request, render_template, redirect, url_for, flash
from models import User, Admin, Tariff, Task, Setting
from string import digits, ascii_lowercase
from flask_admin.contrib.peewee import ModelView
from flask_login import login_user, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import PasswordField
from peewee import DoesNotExist


chars = digits + ascii_lowercase

app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join([random.choice(chars) for _ in range(20)])


login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def before_request():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))


def check_pass_hash(password_hash, password) -> bool:
    return check_password_hash(password_hash, password)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = Admin.get(Admin.email == request.form['email'])
            if check_pass_hash(user.password_hash, request.form['password']):
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                pass
        except DoesNotExist:
            pass
        flash('Неверный логин или пароль', category='error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/payment_success', methods=['GET', 'POST'])
def get_payment():
    print(request.form)
    print(request.args)
    response = request.json
    with open('response_payment.json', 'w', encoidng='utf-8') as f:
        json.dump(response, f, indent=4, ensure_ascii=False)


@app.route('/yoomoney_token_handler')
def yoomoney_token_handler():
    args = dict(request.args)
    code = dict(request.args).get('code')
    with open('yoomoney_token_args.json', 'w', encoding='utf-8') as f:
        json.dump(args, f, indent=4, ensure_ascii=False)
    return str(dict(request.args) + f'\nYour code = {code}')


@login_manager.user_loader
def load_user(user_id):
    return Admin.get(Admin.id == user_id)


class AdminAuthView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class AdminModelView(AdminAuthView):
    form_overrides = dict(password=PasswordField)

    def on_model_change(self, form, model, is_created):
        if form.password_hash.data:
            model.password_hash = generate_password_hash(form.password_hash.data)


def run() -> None:
    admin = flask_admin.Admin(app, name='Админка', template_mode='bootstrap2')
    admin.base_template = 'admin/my_base.html'

    admin.add_view(AdminAuthView(User, name="Пользователи"))
    admin.add_view(AdminModelView(Admin, name='Админы', endpoint="admins"))
    admin.add_view(AdminAuthView(Tariff, name='Тарифы'))
    admin.add_view(AdminAuthView(Task, name='Заказы'))
    admin.add_view(AdminAuthView(Setting, name='Настройки'))

    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    run()
