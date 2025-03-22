from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.user import User
from ..models.mosque import Mosque
from .. import db
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['admin', 'superadmin']:
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
    
    if current_user.role == 'superadmin':
        mosques = Mosque.query.all()
        admins = User.query.filter_by(role='admin').all()
    else:
        mosques = [Mosque.query.get(current_user.mosque_id)]
        admins = User.query.filter_by(mosque_id=current_user.mosque_id).all()
        
    # Get mosque names for all admins in one query to avoid N+1 problem
    mosque_dict = {m.id: m.name for m in Mosque.query.all()}
        
    return render_template(
        "admin/dashboard.html",
        user=current_user,
        mosques=mosques,
        admins=admins,
        mosque_dict=mosque_dict
    )

@admin.route('/mosque/add', methods=['GET', 'POST'])
@login_required
def add_mosque():
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        phone = request.form.get('phone')
        email = request.form.get('email')
        capacity = request.form.get('capacity')
        
        try:
            mosque = Mosque(
                name=name,
                address=address,
                city=city,
                state=state,
                country=country,
                phone=phone,
                email=email,
                capacity=capacity
            )
            db.session.add(mosque)
            db.session.commit()
            flash('Mosque added successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash('Error adding mosque.', category='error')
            
    return render_template("admin/add_mosque.html", user=current_user)

@admin.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_admin():
    if current_user.role not in ['admin', 'superadmin']:
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        mosque_id = request.form.get('mosque_id')
        
        if current_user.role == 'admin' and int(mosque_id) != current_user.mosque_id:
            flash('Unauthorized access.', category='error')
            return redirect(url_for('admin.dashboard'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            try:
                new_admin = User(
                    email=email,
                    name=name,
                    password=generate_password_hash(password, method='sha256'),
                    role='admin',
                    mosque_id=mosque_id
                )
                db.session.add(new_admin)
                db.session.commit()
                flash('Admin added successfully!', category='success')
                return redirect(url_for('admin.dashboard'))
            except Exception as e:
                flash('Error adding admin.', category='error')
                
    if current_user.role == 'superadmin':
        mosques = Mosque.query.all()
    else:
        mosques = [Mosque.query.get(current_user.mosque_id)]
        
    return render_template("admin/add_admin.html", user=current_user, mosques=mosques)

@admin.route('/mosque/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mosque(id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(id)
    
    if request.method == 'POST':
        mosque.name = request.form.get('name')
        mosque.address = request.form.get('address')
        mosque.city = request.form.get('city')
        mosque.state = request.form.get('state')
        mosque.country = request.form.get('country')
        mosque.phone = request.form.get('phone')
        mosque.email = request.form.get('email')
        mosque.capacity = request.form.get('capacity')
        
        try:
            db.session.commit()
            flash('Mosque updated successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash('Error updating mosque.', category='error')
            
    return render_template("admin/edit_mosque.html", user=current_user, mosque=mosque) 