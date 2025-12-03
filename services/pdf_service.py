from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_tenant_certificate(tenant):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # center
    )
    elements.append(Paragraph('HOUSING CERTIFICATE', title_style))
    elements.append(Spacer(1, 20))

    # Tenant data
    data = [
        ['Full Name:', tenant.full_name],
        ['Passport:', f"{tenant.passport_series or ''} №{tenant.passport_number}"],
        ['Address:', f"st. {tenant.apartment.building.street.name}, bld. {tenant.apartment.building.number}, apt. {tenant.apartment.number}"],
        ['Area:', f"{tenant.apartment.area} m²"],
        ['Number of Rooms:', str(tenant.apartment.rooms)],
        ['Ownership Type:', tenant.apartment.ownership_type],
        ['Registration Date:', tenant.registration_date.strftime('%d.%m.%Y')]
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('Issue Date: ' + datetime.now().strftime('%d.%m.%Y'), styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('Signature: _________________', styles['Normal']))

    # Generate PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
