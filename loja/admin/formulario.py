from wtforms import Form, BooleanField, StringField, PasswordField, validators


class RegistrationForm(Form):
    name = StringField('Nome', [validators.Length(min=4, max=25)])
    username = StringField('Usuario', [validators.Length(min=4, max=25)])
    email = StringField(
        'Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Sua senha', [
        validators.DataRequired(),
        validators.EqualTo(
            'confirm', message='Senha e Confirmacao nao sao iguais')
    ])
    confirm = PasswordField('Repete a senha')


class LoginFormulario(Form):
    email = StringField(
        'Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Sua senha', [validators.DataRequired()])
