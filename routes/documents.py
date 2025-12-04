from flask import Blueprint, render_template, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from models import db, Tenant, Apartment, Building, Street
from couchdb_client import CouchDBClient
from services.pdf_service import generate_tenant_certificate

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/tenant/<int:tenant_id>/certificate')
@login_required
def tenant_certificate(tenant_id):
    tenant = Tenant.query.join(Apartment).join(Building).join(Street).filter(
        Tenant.id == tenant_id
    ).first()

    if not tenant:
        flash("Tenant not found!")
        return redirect(url_for('tenants.tenants_list'))

    pdf = generate_tenant_certificate(tenant)

    couch = CouchDBClient()
    couch.save_certificate(tenant_id, pdf)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=certificate_{tenant_id}.pdf'
    return response


@documents_bp.route('/certificates')
@login_required
def certificates():
    if current_user.role != 'admin':
        flash("Access denied")
        return redirect(url_for('tenants.tenants_list'))

    couch = CouchDBClient()
    docs = [couch.db[d] for d in couch.db]
    return render_template("certificates.html", docs=docs)


@documents_bp.route('/certificates/<doc_id>')
@login_required
def get_certificate(doc_id):
    couch = CouchDBClient()
    doc = couch.db.get(doc_id)
    if not doc:
        flash("Document not found")
        return redirect(url_for('documents.certificates'))

    attachment_name = next(iter(doc["_attachments"]))
    pdf = couch.db.get_attachment(doc, attachment_name)

    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename={attachment_name}"
    return response


@documents_bp.route('/district_report')
@login_required
def district_report():
    if current_user.role != 'admin':
        flash("Access denied")
        return redirect(url_for('tenants.tenants_list'))

    streets_data = Street.query.order_by(Street.name).all()
    result = []

    for street in streets_data:
        street_info = {
            'street': street,
            'buildings': [],
            'total_tenants': 0
        }

        buildings = Building.query.filter_by(street_id=street.id).order_by(Building.number).all()
        for building in buildings:
            building_info = {
                'building': building,
                'apartments': []
            }
            apartments = Apartment.query.filter_by(building_id=building.id).order_by(Apartment.number).all()
            for apartment in apartments:
                tenants = Tenant.query.filter_by(apartment_id=apartment.id).all()
                building_info['apartments'].append({
                    'apartment': apartment,
                    'tenants': tenants
                })
                street_info['total_tenants'] += len(tenants)

            street_info['buildings'].append(building_info)

        result.append(street_info)

    return render_template("district_report.html", streets_data=result)
