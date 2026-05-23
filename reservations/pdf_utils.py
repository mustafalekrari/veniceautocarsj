from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_receipt_pdf(response, reservation):
    """Génère un reçu PDF professionnel pour une réservation"""
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Couleurs Venice Autocars
    gold = colors.HexColor('#D4AF37')
    dark = colors.HexColor('#1a1a2e')
    gray = colors.HexColor('#6b7280')

    # Style titre
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=dark,
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=gray,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=12,
        textColor=dark,
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        'Normal2',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4
    )

    # En-tête
    story.append(Paragraph("VENICE AUTOCARS - MAROC", title_style))
    story.append(Paragraph("Agence de Location de Voitures Premium | Casablanca, Maroc", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=gold))
    story.append(Spacer(1, 0.5*cm))

    # Titre reçu
    receipt_title = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=gold,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=10
    )
    story.append(Paragraph(f"REÇU DE RÉSERVATION #{reservation.pk}", receipt_title))

    status_map = {
        'pending': 'EN ATTENTE',
        'confirmed': 'CONFIRMÉE',
        'active': 'EN COURS',
        'completed': 'TERMINÉE',
        'cancelled': 'ANNULÉE',
    }
    story.append(Paragraph(f"Statut: {status_map.get(reservation.status, reservation.status)}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))

    # Infos client
    story.append(Paragraph("INFORMATIONS CLIENT", section_style))
    client_data = [
        ['Nom complet:', reservation.client_name],
        ['Email:', reservation.client_email],
        ['Téléphone:', reservation.client_phone],
        ['Adresse:', reservation.client_address or '-'],
        ['N° Permis:', reservation.client_license or '-'],
    ]
    client_table = Table(client_data, colWidths=[5*cm, 12*cm])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), dark),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(client_table)

    # Infos voiture
    story.append(Paragraph("VÉHICULE LOUÉ", section_style))
    car = reservation.car
    car_data = [
        ['Véhicule:', f"{car.brand} {car.model} ({car.year})"],
        ['Carburant:', car.get_fuel_display()],
        ['Transmission:', car.get_transmission_display()],
        ['Prix/jour:', f"{car.price_per_day}  DH"],
    ]
    car_table = Table(car_data, colWidths=[5*cm, 12*cm])
    car_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), dark),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(car_table)

    # Détails réservation
    story.append(Paragraph("DÉTAILS DE LA LOCATION", section_style))
    res_data = [
        ['Date de début:', str(reservation.start_date)],
        ['Date de fin:', str(reservation.end_date)],
        ['Lieu de prise en charge:', reservation.pickup_location],
        ['Lieu de retour:', reservation.return_location],
        ['Nombre de jours:', str(reservation.total_days)],
    ]
    res_table = Table(res_data, colWidths=[5*cm, 12*cm])
    res_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), dark),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(res_table)

    # Total
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=gold))
    total_data = [['TOTAL À PAYER:', f"{reservation.total_price}  DH"]]
    total_table = Table(total_data, colWidths=[14*cm, 3*cm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('TEXTCOLOR', (0, 0), (0, 0), dark),
        ('TEXTCOLOR', (1, 0), (1, 0), gold),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
    ]))
    story.append(total_table)

    # Pied de page
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=gray,
        alignment=TA_CENTER,
        spaceBefore=10
    )
    story.append(Paragraph("Venice Autocars | Agence de Location Premium - Maroc", footer_style))
    story.append(Paragraph("Merci de votre confiance. Ce document fait office de reçu officiel.", footer_style))
    story.append(Paragraph("Tél: +212 5 22 00 00 00 | contact@venice-autocars.ma | Casablanca, Maroc", footer_style))

    doc.build(story)
