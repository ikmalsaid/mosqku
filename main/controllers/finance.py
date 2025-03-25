from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.finance import Finance
from ..models.mosque import Mosque
from .. import db
from datetime import datetime

finance = Blueprint('finance', __name__)

@finance.route('/finance')
@login_required
def finance_list():
    if current_user.role == 'superadmin':
        mosque_id = request.args.get('mosque_id', type=int)
        if not mosque_id:
            flash('Please select a mosque.', category='error')
            return redirect(url_for('admin.dashboard'))
    else:
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    items = Finance.query.filter_by(mosque_id=mosque_id).order_by(Finance.date_added.desc()).all()
    
    # Calculate totals
    total_income = sum(item.amount for item in items if item.amount > 0)
    total_expenses = abs(sum(item.amount for item in items if item.amount < 0))
    
    return render_template('finance/list.html', 
                         items=items, 
                         mosque=mosque,
                         user=current_user,
                         total_income=total_income,
                         total_expenses=total_expenses)

@finance.route('/finance/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role == 'superadmin':
        mosque_id = request.args.get('mosque_id', type=int)
        if not mosque_id:
            flash('Please select a mosque.', category='error')
            return redirect(url_for('admin.dashboard'))
    else:
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    if request.method == 'POST':
        number = request.form.get('number')
        transaction_name = request.form.get('transaction_name')
        finance_category = request.form.get('finance_category')
        description = request.form.get('description')
        amount = request.form.get('amount', type=float)
        remarks = request.form.get('remarks')
        
        if not number or not transaction_name or not finance_category or amount is None:
            flash('Required fields cannot be empty.', category='error')
        else:
            try:
                new_item = Finance(
                    mosque_id=mosque_id,
                    number=number,
                    transaction_name=transaction_name,
                    finance_category=finance_category,
                    description=description,
                    amount=amount,
                    remarks=remarks
                )
                db.session.add(new_item)
                db.session.commit()
                flash('Transaction added successfully!', category='success')
                return redirect(url_for('finance.finance_list', mosque_id=mosque_id))
            except Exception as e:
                flash('Error adding transaction.', category='error')
                
    return render_template('finance/add.html', mosque=mosque, user=current_user)

@finance.route('/finance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Finance.query.get_or_404(id)
    
    if current_user.role == 'superadmin':
        mosque_id = item.mosque_id
    else:
        if item.mosque_id != current_user.mosque_id:
            flash('Unauthorized access.', category='error')
            return redirect(url_for('mosque.dashboard'))
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    if request.method == 'POST':
        item.number = request.form.get('number')
        item.transaction_name = request.form.get('transaction_name')
        item.finance_category = request.form.get('finance_category')
        item.description = request.form.get('description')
        item.amount = request.form.get('amount', type=float)
        item.remarks = request.form.get('remarks')
        
        if not item.number or not item.transaction_name or not item.finance_category or item.amount is None:
            flash('Required fields cannot be empty.', category='error')
        else:
            try:
                db.session.commit()
                flash('Transaction updated successfully!', category='success')
                return redirect(url_for('finance.finance_list', mosque_id=mosque_id))
            except Exception as e:
                flash('Error updating transaction.', category='error')
                
    return render_template('finance/edit.html', item=item, mosque=mosque, user=current_user)

@finance.route('/finance/delete/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    item = Finance.query.get_or_404(id)
    
    if current_user.role == 'superadmin':
        mosque_id = item.mosque_id
    else:
        if item.mosque_id != current_user.mosque_id:
            flash('Unauthorized access.', category='error')
            return redirect(url_for('mosque.dashboard'))
        mosque_id = current_user.mosque_id
        
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Transaction deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting transaction.', category='error')
        
    return redirect(url_for('finance.finance_list', mosque_id=mosque_id)) 