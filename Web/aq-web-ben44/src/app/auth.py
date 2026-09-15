from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Account
from . import db

identity_bp = Blueprint('identity', __name__)

@identity_bp.route('/signin', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        login_name = request.form['username']
        secret = request.form['password']
        
        account = Account.query.filter_by(login_name=login_name).first()
        
        if account and account.verify_secret(secret):
            session['account_id'] = account.id
            session['login_name'] = account.login_name
            session['has_admin_rights'] = account.has_admin_rights
            flash('Authentication successful!', 'success')
        
            return redirect(url_for('workspace.home'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('identity/signin.html')

@identity_bp.route('/signup', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        login_name = request.form['username']
        email_address = request.form['email']
        secret = request.form['password']
        secret_confirm = request.form['confirm_password']
        
        if secret != secret_confirm:
            flash('Secrets do not match!', 'error')
            return render_template('identity/signup.html')
        
        if Account.query.filter_by(login_name=login_name).first():
            flash('Login name already exists!', 'error')
            return render_template('identity/signup.html')
        
        if Account.query.filter_by(email_address=email_address).first():
            flash('Email already exists!', 'error')
            return render_template('identity/signup.html')
        
        account = Account(login_name=login_name, email_address=email_address)
        account.update_secret(secret)
        db.session.add(account)
        db.session.commit()
        
        flash('Account creation successful! Please sign in.', 'success')
        return redirect(url_for('identity.authenticate'))
    
    return render_template('identity/signup.html')

@identity_bp.route('/signout')
def terminate_session():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('identity.authenticate'))

def access_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'account_id' not in session:
            flash('Please sign in to access this page.', 'error')
            return redirect(url_for('identity.authenticate'))
        return f(*args, **kwargs)
    return decorated_function

def admin_access_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'account_id' not in session:
            flash('Please sign in to access this page.', 'error')
            return redirect(url_for('identity.authenticate'))
        if not session.get('has_admin_rights'):
            flash('Administrator access required.', 'error')
            return redirect(url_for('workspace.home'))
        return f(*args, **kwargs)
    return decorated_function
