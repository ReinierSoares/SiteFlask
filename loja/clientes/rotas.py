
from crypt import methods
from pydoc import cli
import secrets
from flask import render_template, session, request, url_for, flash, redirect, session, current_app, make_response
from loja import app, db, photos, login_manager
from .forms import CadastroClienteForm, ClienteLoginForm
from .models import Cadastrar, ClientePedido
from flask_login import login_required, current_user, login_user, logout_user
import pdfkit
import stripe


publishable_key = 'pk_test_51LhyxTKDHMCCpxWoYoENIKWUVZZXuNhpdiQzzZMwF9hcUWyA52zpiFwGWiEByuxMRuhTEZxx8unLo7S67i3fkDBa00WDGzebP5'


@app.route('/obrigado')
def obrigado():
    return render_template('cliente/obrigado.html')


@app.route('/pagamento', methods=['POST'])
def pagamento():

    stripe.api_key = 'sk_test_51LhyxTKDHMCCpxWoaMxb4h4yNHmSOLjQG7I5mZGdzlAylvk9SACsw5FPh0k6nzrsY6WvoWLAsow3UNVAURXNfmWA00l7Qll46t'

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': '{{PRICE_ID}}',
            'quantity': 1,
        }],
        payment_intent_data={
            'application_fee_amount': 200,
        },
        mode='payment',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
        stripe_account='{{CONNECTED_STRIPE_ACCOUNT_ID}}',
    )
    return redirect(url_for('obrigado'))


@app.route('/cliente/cadastrar', methods=['GET', 'POST'])
def cadastrar_clientes():
    form = CadastroClienteForm()
    if form.validate_on_submit():
        cadastrar = Cadastrar(name=form.name.data, username=form.username.data, email=form.email.data, password=form.password.data,
                              country=form.country.data, city=form.city.data, contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(cadastrar)
        db.session.commit()
        flash(f'Obrigado {form.name.data} por registrar!', 'success')
        return redirect(url_for('clientelogin'))
    return render_template('clientes/cliente.html', form=form)


@app.route('/cliente/login', methods=['GET', 'POST'])
def clientelogin():
    form = ClienteLoginForm()
    if form.validate_on_submit():
        user = Cadastrar.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Voce esta logado!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('As credenciais estao erradas!', 'danger')
        return redirect(url_for('clientelogin'))
    return render_template('clientes/login.html', form=form)


def atualizarlojaCarro():
    for _key, produto in session['LojainCarrinho'].items():
        session.modified = True
        del produto['image']
        del produto['colors']
    return atualizarlojaCarro


@app.route('/cliente/logout')
def cliente_logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/pedido_order')
def pedido_order():
    if current_user.is_authenticated:
        cliente_id = current_user.id
        notafiscal = secrets.token_hex(5)
        atualizarlojaCarro()
        try:
            p_order = ClientePedido(
                notafiscal=notafiscal, cliente_id=cliente_id, pedido=session['LojainCarrinho'])
            db.session.add(p_order)
            db.session.commit()
            session.pop('LojainCarrinho')
            flash('Seu pedido foi feito!', 'danger')
            return redirect(url_for('pedidos', notafiscal=notafiscal))
        except Exception as e:
            print(e)
            flash('Nao foi possivel processar seu pedido!', 'danger')
            return redirect(url_for('getCart'))


@app.route('/pedidos/<notafiscal>')
@login_required
def pedidos(notafiscal):
    if current_user.is_authenticated:
        gTotal = 0
        subtotal = 0

        cliente_id = current_user.id
        cliente = Cadastrar.query.filter_by(id=cliente_id).first()
        pedidos = ClientePedido.query.filter_by(
            cliente_id=cliente_id, notafiscal=notafiscal).order_by(ClientePedido.id.desc()).first()
        for _key, produto in pedidos.pedido.items():
            desconto = (produto['discount']/100) * float(produto['price'])
            subtotal += float(produto['price']) * int(produto['quantity'])
            subtotal -= desconto
            imposto = ("%.2f" % (.06 * float(subtotal)))
            gTotal = float("%.2f" % (1.06 * subtotal))
    else:
        return redirect(url_for('clientelogin'))
    return render_template('cliente/pedido.html', notafiscal=notafiscal, imposto=imposto, subtotal=subtotal, gTotal=gTotal, cliente=cliente, pedidos=pedidos)


@app.route('/get_pdf/<notafiscal>', methods=['POST'])
@login_required
def get_pdf(notafiscal):
    if current_user.is_authenticated:
        gTotal = 0
        subtotal = 0
        cliente_id = current_user.id
        if request.method == 'POST':
            cliente = Cadastrar.query.filter_by(id=cliente_id).first()
            pedidos = ClientePedido.query.filter_by(
                cliente_id=cliente_id, notafiscal=notafiscal).order_by(ClientePedido.id.desc()).first()
            for _key, produto in pedidos.pedido.items():
                desconto = (produto['discount']/100) * float(produto['price'])
                subtotal += float(produto['price']) * int(produto['quantity'])
                subtotal -= desconto
                imposto = ("%.2f" % (.06 * float(subtotal)))
                gTotal = float("%.2f" % (1.06 * subtotal))

            rendered = render_template('cliente/pdf.html', notafiscal=notafiscal, imposto=imposto,
                                       subtotal=subtotal, gTotal=gTotal, cliente=cliente, pedidos=pedidos)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'attched;filename=' + \
                notafiscal + '.pdf'
            return response
    return redirect(url_for('pedidos'))
