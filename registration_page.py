from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired
from flask_wtf import FlaskForm
from flask import Flask, redirect, render_template


class RegForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(message='Заполните поле')])
    email = StringField('Эл. почта', validators=[InputRequired(message='Заполните поле'), Email()])
    password = PasswordField('Придумайте пароль',
                             validators=[InputRequired(message='Заполните поле'),
                                         EqualTo('repeat_password', 'Пароли не совпадают')])
    repeat_password = PasswordField('Повторите пароль', validators=[InputRequired(message='Заполните поле')])
    name = StringField('Имя')
    next_button = SubmitField('Далее')


def registration():
    form = RegForm()
    if not form.validate_on_submit():
        return redirect('/registration_auto')
    return render_template('registration_page.html', form=form)
