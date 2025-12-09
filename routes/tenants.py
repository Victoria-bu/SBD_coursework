from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Tenant, Apartment, Building, Street

tenants_bp = Blueprint('tenants', __name__, url_prefix='/tenants')

@tenants_bp.route('/tenants')
@login_required
def tenants_list():
    if current_user.role == 'admin':
        tenants = Tenant.query.all()
    else:
        if not current_user.tenant_id:
            flash("Your account is not linked to any tenant.")
            return render_template("tenants.html", tenants=[])
        tenants = Tenant.query.filter_by(id=current_user.tenant_id).all()
    return render_template("tenants.html", tenants=tenants)

@tenants_bp.route('/tenant/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            # Розділяємо повне ім'я
            full_name = request.form['full_name']
            parts = full_name.strip().split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
            
            tenant = Tenant(
                first_name=first_name,  
                last_name=last_name,  
                passport_series=request.form.get('passport_series'),
                passport_number=request.form['passport_number'],
                phone=request.form.get('phone'),
                registration_date=request.form['registration_date'],
                apartment_id=request.form['apartment_id']
            )
            db.session.add(tenant)
            db.session.commit() 
            flash("Tenant added!")
            return redirect(url_for('tenants.tenants_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}")

    apartments = Apartment.query.options(
        db.joinedload(Apartment.building).joinedload(Building.street)
    ).all()
    
    return render_template("tenant_form.html", apartments=apartments)

@tenants_bp.route('/tenant/delete/<int:tenant_id>', methods=['POST'])
@login_required
def delete_tenant(tenant_id):
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('tenants.tenants_list'))

    tenant = Tenant.query.get_or_404(tenant_id)
    try:
        db.session.delete(tenant)
        db.session.commit()
        flash("Tenant deleted!")
    except Exception as e:
        db.session.rollback()
        flash(f"Delete error: {e}")

    return redirect(url_for('tenants.tenants_list'))

@tenants_bp.route('/tenant/edit/<int:tenant_id>', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('tenants.tenants_list'))

    tenant = Tenant.query.get_or_404(tenant_id)

    if request.method == 'POST':
        try:
            # Розділяємо повне ім'я
            full_name = request.form['full_name']
            parts = full_name.strip().split(' ', 1)
            tenant.first_name = parts[0]
            tenant.last_name = parts[1] if len(parts) > 1 else ""
            
            tenant.passport_series = request.form.get('passport_series')
            tenant.passport_number = request.form['passport_number']
            tenant.phone = request.form.get('phone')
            tenant.registration_date = request.form['registration_date']
            tenant.apartment_id = request.form['apartment_id']

            db.session.commit()
            flash("Tenant updated!")
            return redirect(url_for('tenants.tenants_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}")

    apartments = Apartment.query.options(
        db.joinedload(Apartment.building).joinedload(Building.street)
    ).all()
    
    # Додати додаткові атрибути до кожного об'єкта
    for apt in apartments:
        apt.building_number = apt.building.number if apt.building else ''
        apt.street_name = apt.building.street.name if apt.building and apt.building.street else ''
    
    return render_template("tenant_form.html", tenant=tenant, apartments=apartments)