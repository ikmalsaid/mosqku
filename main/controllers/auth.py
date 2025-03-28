from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from ..models.user import User
from .. import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('mosque.dashboard'))
        else:
            flash('Username or password is incorrect.', category='error')
            
    return render_template("auth/login.html", user=current_user)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.filter_by(email=email).first()
        
        if not email or not name or not password or not confirm_password:
            flash('All fields are required.', category='error')
        elif user:
            flash('User already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password != confirm_password:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            recovery_key = User.generate_recovery_key()
            new_user = User(
                email=email,
                name=name,
                password=generate_password_hash(password, method='scrypt'),
                role='user',
                recovery_key=recovery_key
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'{name} account created!', category='success')
            return redirect(url_for('mosque.dashboard'))
            
    return render_template("auth/register.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', category='error')
        elif not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', category='error')
        elif new_password != confirm_password:
            flash('Passwords don\'t match.', category='error')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            current_user.password = generate_password_hash(new_password, method='scrypt')
            db.session.commit()
            flash('Password updated successfully!', category='success')
            return redirect(url_for('mosque.dashboard'))
            
    return render_template("auth/change_password.html", user=current_user)

@auth.route('/view_recovery_key')
@login_required
def view_recovery_key():
    return render_template("auth/view_recovery_key.html", user=current_user)

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        recovery_key = request.form.get('recovery_key')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.filter_by(email=email).first()
        
        if not email or not recovery_key or not new_password or not confirm_password:
            flash('All fields are required.', category='error')
        elif not user:
            flash('Email not found.', category='error')
        elif recovery_key != user.recovery_key:
            flash('Invalid recovery key.', category='error')
        elif new_password != confirm_password:
            flash('Passwords don\'t match.', category='error')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            user.password = generate_password_hash(new_password, method='scrypt')
            # Generate a new recovery key after password reset
            user.recovery_key = User.generate_recovery_key()
            db.session.commit()
            flash('Password reset successfully! You can now login with your new password.', category='success')
            return redirect(url_for('auth.login'))
            
    return render_template("auth/forgot_password.html", user=current_user) 