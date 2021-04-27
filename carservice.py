from flask import Flask, redirect, render_template, request, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, FieldList, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo
from data import db_session
from data.users import User
from data.cars import Cars
from data.history import History
from data.works import Works
from flask_login import LoginManager
import datetime
from werkzeug.utils import secure_filename
import os
from flask_wtf.file import FileAllowed, FileRequired
from sqlalchemy import desc
import base64
import calendar
# from dateutil.relativedelta import *

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class RegForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(message='Заполните поле')])
    email = StringField('Эл. почта', validators=[InputRequired(message='Заполните поле'), Email()])
    password = PasswordField('Придумайте пароль', validators=[InputRequired(message='Заполните поле')])
    repeat_password = PasswordField('Повторите пароль', validators=[InputRequired(message='Заполните поле'),
                                                                    EqualTo('password',
                                                                            message='Пароли не совпадают')])
    name = StringField('Имя')
    next_button = SubmitField('Далее')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(message='Заполните поле')])
    password = PasswordField('Пароль', validators=[InputRequired(message='Заполните поле')])
    submit_button = SubmitField('Войти')


class RegAutoForm(FlaskForm):
    photo = FileField('Прикрепите фото', validators=[FileRequired(message='Прикрепите фото'),
                                                     FileAllowed(['jpg', 'png'], message="Только картинки")])
    mark = StringField('Марка', validators=[InputRequired(message='Заполните поле')])
    model = StringField('Модель')
    gen = StringField('Поколение')
    km = StringField('Пробег', validators=[InputRequired(message='Заполните поле')])
    year = StringField('Год выпуска', validators=[InputRequired(message='Заполните поле')])
    vin = StringField('VIN код')
    add_button = SubmitField('Добавить')


class RegWorks(FlaskForm):
    center = FieldList(StringField('Work', render_kw={'readonly': True}), label="Выбранные вами работы")
    name = StringField('Наименование работы')
    km = StringField('Период замены в км')
    period = StringField('Период замены в мес')
    add_button = SubmitField('Добавить')
    ready_button = SubmitField('Готово')


class MainPage(FlaskForm):
    km = StringField('Пробег')
    mark = StringField('Марка')
    model = StringField('Модель')
    gen = StringField('Поколение')
    year = StringField('Год выпуска')
    vin = StringField('VIN код')
    km_button = SubmitField('Ввести')
    change_button = SubmitField('Изменить')


class ChangeForm(FlaskForm):
    km = StringField('Пробег', validators=[DataRequired()])
    date = StringField('Дата', validators=[DataRequired()])
    price = StringField('Цена')
    link = StringField('Ссылка на магазин')
    text = TextAreaField('Описание')
    photo = FileField('Фото', validators=[FileAllowed(['jpg', 'png'], message="Только картинки")])
    change_button = SubmitField('Заменить')


def get_my_car(user):
    for car in db_sess.query(Cars).filter_by(person_id=user):
        return car.id
    return 0


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    global my_user
    global my_car
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            my_user = form.login.data
            my_car = get_my_car(my_user)
            return redirect('/car_page')
        return render_template('login_page.html', message="Неправильный логин или пароль", form=form)
    return render_template('login_page.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    global my_user
    form = RegForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('registration-page.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('registration-page.html', title='Регистрация', message="Такой пользователь уже есть",
                                   form=form)
        user = User(
            login=form.login.data,
            name=form.name.data,
            email=form.email.data,
        )
        my_user = form.login.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/registration_auto')
    return render_template('registration-page.html', form=form, title='Регистрация')


@app.route('/registration_auto', methods=['GET', 'POST'])
def registration_auto():
    global car_list
    global my_car
    form = RegAutoForm()
    if form.validate_on_submit():
        car = Cars(
            person_id=my_user,
            photo=form.photo.data.read(),
            mark=form.mark.data,
            model=form.model.data,
            gen=form.gen.data,
            km=form.km.data,
            year=form.year.data,
            vin=form.vin.data
        )
        db_sess.add(car)
        db_sess.commit()
        my_car = get_my_car(my_user)
        if form.model.data:
            car_list.append(form.mark.data + ' ' + form.model.data + ' ' + form.year.data)
        else:
            car_list.append(form.mark.data + ' ' + form.year.data)
        return redirect('/registration_auto')
    return render_template('registration_auto_page.html', form=form, title='Регистрация автомобилей')


@app.route('/work_adding', methods=["GET", "POST"])
def work_adding():
    global car_list
    global i
    global work_list
    form = RegWorks()
    if request.method == 'GET' and len(request.args) == 0:
        return render_template('work_adding.html', form=form, car=car_list[i])
    elif request.method == 'GET':
        val = request.args['value']
        lis = val.split('(')
        lis[1] = lis[1].rstrip(')')
        form.name.data = lis[0]
        if 'мес' in lis[1]:
            form.period.data = lis[1]
        else:
            form.km.data = lis[1]
        for u in work_list:
            form.center.append_entry(u)
        return render_template('work_adding.html', form=form, car=car_list[i])
    elif request.method == 'POST' and 'add_button' in request.form:
        if form.period.data and form.km.data:
            return render_template('work_adding.html', form=form, car=car_list[i],
                                   message='Заполните только одно из полей')
        elif form.period.data:
            st = form.name.data + '(' + form.period.data + ')'
        elif form.km.data:
            st = form.name.data + '(' + form.km.data + ')'
        else:
            return render_template('work_adding.html', form=form, car=car_list[i],
                                   message='Заполните одно из полей')
        form.km.data = None
        form.period.data = None
        form.name.data = None
        form.center.append_entry(st)
        work_list.append(st)
        lis = car_list[i].split(' ')
        mark = lis[0]
        if len(lis) == 2:
            year = lis[1]
            for car in db_sess.query(Cars).filter_by(mark=mark, year=year):
                id1 = car.id
        else:
            model = lis[1]
            year = lis[2]
            for car in db_sess.query(Cars).filter_by(mark=mark, model=model, year=year):
                id1 = car.id
        lis = st.split('(')
        lis[1] = lis[1].rstrip(')')
        if 'мес' in lis[1]:
            work = Works(
                car_id=id1,
                name=lis[0],
                km=None,
                date=lis[1]
            )
        else:
            work = Works(
                car_id=id1,
                name=lis[0],
                km=lis[1],
                date=None
            )
        db_sess.add(work)
        db_sess.commit()
        return render_template('work_adding.html', form=form, car=car_list[i])
    else:
        if i + 1 == len(car_list):
            work_list = []
            return redirect('/car_page')
        else:
            i += 1
            work_list = []
            return redirect('/work_adding')


@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    global my_car
    global my_user
    form = MainPage()
    list_no_ready = [
        {'name': my_car, 'km': '1', 'date': '', 'button_name': 'name_1'},
        {'name': my_car, 'km': '', 'date': '00-00-00', 'button_name': 'name_2'},
        {'name': my_car, 'km': '2', 'date': '', 'button_name': 'name_3'}
    ]
    list_will_be = [
        {'name': 'name_1', 'km': '1', 'date': '', 'button_name': 'name_4'},
        {'name': 'name_1', 'km': '', 'date': '00-00-00', 'button_name': 'name_5'},
        {'name': 'name_1', 'km': '2', 'date': '', 'button_name': 'name_6'}
    ]
    list_history = [
        {'name': 'name_1', 'km': '1', 'date': '', 'price': '', 'link': '', 'text': '',
         'photo': ''},
        {'name': 'name_1', 'km': '', 'date': '00-00-00', 'price': '', 'link': '', 'text': '',
         'photo': ''},
        {'name': 'name_1', 'km': '2', 'date': '', 'price': '', 'link': '', 'text': '',
         'photo': ''}
    ]
    if request.method == 'GET':
        my_car = int(request.args['car_id'])
        car = db_sess.query(Cars).filter_by(id=my_car)[0]
        km = car.km
        photo = str(base64.b64encode(car.photo)).lstrip("b'").rstrip("'")
        form.km.data = car.km
        form.mark.data = car.mark
        form.model.data = car.model
        form.gen.data = car.gen
        form.year.data = car.year
        form.vin.data = car.vin
        list_history = []
        list_no_ready = []
        list_will_be = []
        for history in db_sess.query(History).filter_by(car_id=my_car).order_by(desc(History.km)):
            list_history.append(
                {'name': history.name, 'km': str(history.km), 'date': history.date, 'price': history.price,
                 'link': history.link, 'text': history.text, 'photo': ''})
        for work in db_sess.query(Works).filter_by(car_id=my_car):
            hist = db_sess.query(History).filter_by(car_id=my_car, work_id=work.id).order_by(desc(History.km)).limit(1)
            # if not work.km:
            #     a = hist.date
            #     res = a + relativedelta(month+=int(str(work.date).rstrip('мес')))
            #     if res > datetime.datetime.now().date:
            #         list_will_be.append({'name': work.name, 'km': '', 'date': res, 'button_name': 'button_' + str(work.id)})
            #     else:
            #         list_no_ready.append({'name': work.name, 'km': '', 'date': res, 'button_name': 'button_' + str(work.id)})
            # else:            
            target_km = 0
            if hist.count() == 0:
                target_km = work.km
            else:
                target_km = hist[0].km + work.km
            if km > target_km:
                list_no_ready.append(
                    {'name': work.name, 'km': str(target_km), 'date': '', 'button_name': 'button_' + str(work.id)})
            else:
                list_will_be.append(
                    {'name': work.name, 'km': str(target_km), 'date': '', 'button_name': 'button_' + str(work.id)})
    else:
        if 'change_button' in request.form:
            db_sess.query(Cars).filter_by(id=my_car).update(
                {'mark': form.mark.data, 'model': form.model.data, 'gen': form.gen.data, 'year': form.year.data,
                 'vin': form.vin.data})
            db_sess.commit()
        elif 'km_button' in request.form:
            if car.km > form.km.data:
                flash('Некорректный пробег')
                return redirect('/main_page?car_id=' + str(my_car))
            db_sess.query(Cars).filter_by(id=my_car).update({'km': form.km.data})
            db_sess.commit()
        return redirect('/main_page?car_id=' + str(my_car))
    return render_template('main_auto_page.html', form=form, list_no_ready=list_no_ready, list_will_be=list_will_be,
                           list_history=list_history, photo=photo)


@app.route('/change_page', methods=['GET', 'POST'])
def change_page():
    global my_car
    form = ChangeForm()
    km = 0
    btn_name = request.args['button_name']
    work_id = btn_name.split('_')[1]
    for work in db_sess.query(Works).filter_by(id=work_id):
        name = work.name
    if request.method == 'GET':
        for car in db_sess.query(Cars).filter_by(id=my_car):
            km = car.km
        form.km.data = km
        form.date.data = datetime.datetime.now().date()
        return render_template('change_page.html', form=form)
    else:
        if form.validate_on_submit():
            hist = History(
                name=name,
                car_id=my_car,
                work_id=work_id,
                km=form.km.data,
                date=form.date.data,
                price=form.price.data,
                link=form.link.data,
                text=form.text.data,
                photo=form.photo.data.read()
            )
            db_sess.add(hist)
            db_sess.commit()
            return redirect('/main_page?car_id=' + str(my_car))
        return render_template('change_page.html', form=form)


@app.route('/car_page', methods=['GET', 'POST'])
def car_page():
    c = 0
    lis = []
    for car in db_sess.query(Cars).filter_by(person_id=my_user):
        lis.append({})
        lis[c]['photo'] = str(base64.b64encode(car.photo)).lstrip("b'").rstrip("'")
        lis[c]['mark'] = car.mark
        lis[c]['model'] = car.model
        lis[c]['year'] = str(car.year)
        lis[c]['car_id'] = car.id
        c += 1
    rows = c // 2
    r_l = []
    for u in range(rows):
        r_l.append(u)
    if c % 2 == 0:
        extra = False
    else:
        extra = True
    return render_template('car_page.html', list=lis, rows=r_l, extra=extra)


my_user = None
car_list = []
i = 0
my_car = None
work_list = []
db_session.global_init("db/CarService.sqlite")
db_sess = db_session.create_session()

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
