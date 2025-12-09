from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

from models import Street
from models import Building
from models import Apartment
from models import Tenant
from app import db

def get_total_area(street_id):
    result = db.session.query(db.func.sum(Apartment.area))\
        .join(Building, Apartment.building_id == Building.id)\
        .join(Street, Building.street_id == Street.id)\
        .filter(Street.id == street_id)\
        .scalar()
    return result or 0

def generate_district_report_pdf(streets):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Заголовок документа
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1 
    )
    elements.append(Paragraph("District Report", title_style))
    elements.append(Spacer(1, 20))

    # Проходимо по всіх вулицях
    for street in streets:
        street_title_style = ParagraphStyle(
            'StreetTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        elements.append(Paragraph(f"Street: {street.name}", street_title_style))
        elements.append(Spacer(1, 10))

        # Таблиця для будинків
        for building in getattr(street, "buildings", []):
            data = [
                ["Building", building.number],
                ["Number of Apartments", str(len(getattr(building, "apartments", [])))]
            ]
            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))

            # Дані про квартири та мешканців
            for apartment in getattr(building, "apartments", []):
                tenants = getattr(apartment, "tenants", [])
                tenant_names = ", ".join([f"{t.first_name} {t.last_name}" for t in tenants]) or "No tenants"
                status = "Occupied" if getattr(apartment, "is_occupied", False) else "Empty"

                apt_data = [
                    ["Apartment", apartment.number],
                    ["Status", status],
                    ["Tenants", tenant_names],
                    ["Area", f"{apartment.area} m²"],
                    ["Rooms", str(apartment.rooms)],
                    ["Ownership", apartment.ownership_type]
                ]
                apt_table = Table(apt_data, colWidths=[150, 300])
                apt_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(apt_table)
                elements.append(Spacer(1, 15))

        elements.append(PageBreak())  # нова сторінка для наступної вулиці

    # Дата створення
    elements.append(Paragraph(f"Report generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))

    # Генеруємо PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
