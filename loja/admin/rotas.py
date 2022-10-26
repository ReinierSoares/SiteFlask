
from ast import Add
from flask import render_template, session, request, url_for, flash, redirect
from loja.produtos.models import Addproduto, Marca, Categoria
from loja import app, db, bcrypt
from .formulario import LoginFormulario, RegistrationForm
from .models import User
import os




@app.route('/admin')
def admin():
    if "email" not in session:
        flash('Faça seu login!', 'danger')
        return redirect(url_for('login'))

    produtos = Addproduto.query.all()
    return render_template('admin/index.html', tittle='Pagina Ferronorte', produtos=produtos)


@app.route('/marcas')
def marcas():
    if "email" not in session:
        flash('Faça seu login!', 'danger')
        return redirect(url_for('login'))

    marcas = Marca.query.order_by(Marca.id.desc()).all()
    return render_template('admin/marca.html', tittle='Pagina Marcas', marcas=marcas)


@app.route('/categorias')
def categorias():
    if "email" not in session:
        flash('Faça seu login!', 'danger')
        return redirect(url_for('login'))

    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('admin/marca.html', tittle='Pagina Categoria', categorias=categorias)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Obrigado {form.name.data} por registrar!', 'success')
        return redirect(url_for('login'))
    return render_template('admin/registrar.html', form=form, tittle="Pagina de Registros")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginFormulario(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            session['email'] = form.email.data
            flash(f'Olá {form.email.data} !', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Nao foi possivel entrar no sistema!', 'danger')
    return render_template('admin/login.html', form=form, tittle='Pagina Login')
