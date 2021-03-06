# -*- coding: utf-8 -*-
"""View functions for the authentication routes."""
import unidecode
import secrets
import os
import subprocess
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, \
    login_required, fresh_login_required
from app import db, login
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


def gen_password(length=8,
                 charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                 "0123456789!@#$%^&*()"):
    """Generate user password."""
    return "".join([secrets.choice(charset) for _ in range(0, length)])


def create_pdf(first_name, last_name, grad_class, username, password):
    """Generate the PDF file with user credientials."""
    with open(os.path.join('latex', 'model.tex'), 'r') as f:
        model = f.read()

    with open(os.path.join('latex', str(grad_class), username + '.tex'),
              'w') as f:
        f.write(model % (
             first_name + ' ' + last_name,
             grad_class,
             username,
             '\\texttt{'+password.
             replace('&', r'\&').
             replace('%', r'\%').
             replace('$', r'\$').
             replace('#', r'\#').
             replace('^', r'\\textasciicircum{}')+'}',))

    subprocess.check_call(['pdflatex', '-output-directory=' +
                           os.path.join('pdf', str(grad_class)),
                           os.path.join('latex', str(grad_class),
                                        username+'.tex')])
    subprocess.check_call(['rm', os.path.join('pdf', str(grad_class),
                                              username+'.aux')])
    subprocess.check_call(['rm', os.path.join('pdf', str(grad_class),
                                              username+'.log')])
    subprocess.check_call(['rm', os.path.join('pdf', str(grad_class),
                                              username+'.out')])


@login.needs_refresh_handler
@login_required
def refresh():
    """Log out user and redirect to login page."""
    logout_user()
    flash('To protect your account, please reauthenticate to access this '
          'page.', 'warning')
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Render the login page and log user in."""
    if current_user.is_authenticated:
        flash("You can't access this page while being logged in.", 'danger')
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if current_user.is_observer or current_user.is_bartender or\
                    current_user.is_admin:
                next_page = url_for('main.dashboard')
            else:
                next_page = url_for('main.user',
                                    username=current_user.username)
        flash('You were successfully logged in.', 'primary')
        return redirect(next_page)
    return render_template('auth/login.html.j2', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Log out user."""
    logout_user()
    flash('You were successfully logged out.', 'primary')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
@fresh_login_required
def register():
    """Render the register page."""
    if not (current_user.is_bartender or current_user.is_admin):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Get user information from form and generate username, email and
        # password
        grad_class = form.grad_class.data or 0  # 0 if extern
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = first_name[0].lower() + \
            unidecode.unidecode(last_name.
                                replace(' ', '').
                                replace("'", '').
                                lower()).partition('-')[0][:7]
        password = gen_password()

        # Set account type
        is_customer = form.account_type.data == 'customer'
        is_observer = form.account_type.data == 'observer'
        is_bartender = form.account_type.data == 'bartender'
        is_admin = form.account_type.data == 'admin'

        # Generate pdf
        # create_pdf(cols[1], cols[0], gc, username, password)

        # Test if username already exists
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('User ' + username + ' already exists.', 'danger')
            return redirect(request.referrer)

        # Create user
        user = User(first_name=first_name,
                    last_name=last_name,
                    birthdate=form.birthdate.data,
                    grad_class=grad_class,
                    username=username, email=form.email.data.lower(),
                    is_observer=is_observer,
                    is_customer=is_customer,
                    is_bartender=is_bartender,
                    is_admin=is_admin)
        user.set_password(password)
        user.set_qrcode()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, the user ' + user.username +
              ' has been added with password '+password+'.',
              'primary')
        return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html.j2', title='Register',
                           form=form)
