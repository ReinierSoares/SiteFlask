
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators, DecimalField, PasswordField, SubmitField, ValidationError
from flask_wtf import FlaskForm
from .models import Cadastrar


class CadastroClienteForm(FlaskForm):
    name = StringField('Nome : ')
    username = StringField('Usuario :', [validators.DataRequired()])
    email = StringField('Email :', [validators.DataRequired()])
    password = PasswordField('Senha :', [validators.DataRequired(
    ), validators.EqualTo('confirm', message='As senhas precisam ser iguais!')])
    confirm = PasswordField('Digite novamente :', [validators.DataRequired()])
    country = StringField('País :', [validators.DataRequired()])
    state = StringField('Estado :', [validators.DataRequired()])
    city = StringField('Cidade :', [validators.DataRequired()])
    contact = StringField('Contato :', [validators.DataRequired()])
    address = StringField('Endereço :', [validators.DataRequired()])
    zipcode = StringField('CEP :', [validators.DataRequired()])

    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        if Cadastrar.query.filter_by(username=username.data).first():
            raise ValidationError("Este usuario ja esta cadastrado!")

    def validate_email(self, email):
        if Cadastrar.query.filter_by(email=email.data).first():
            raise ValidationError("Este email ja esta cadastrado!")


class ClienteLoginForm(FlaskForm):
    email = StringField('Email :', [validators.DataRequired()])
    password = PasswordField('Senha :', [validators.DataRequired()])
