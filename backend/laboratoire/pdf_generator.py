"""
Génération de PDF pour les résultats de laboratoire
Utilisation de WeasyPrint ou ReportLab
"""
from django.template import Template, Context
from django.http import HttpResponse
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint non installé. Installer avec: pip install weasyprint")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab non installé. Installer avec: pip install reportlab")


class ResultatLaboratoirePDF:
    """Générateur de PDF pour résultats de laboratoire"""
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .logo { font-size: 24px; font-weight: bold; color: #2563eb; }
            .hospital-info { margin-top: 10px; font-size: 12px; color: #666; }
            .patient-info { background: #f3f4f6; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .exam-info { margin-bottom: 20px; }
            .result-section { margin: 20px 0; }
            .result-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            .result-table th { background: #2563eb; color: white; padding: 10px; text-align: left; }
            .result-table td { padding: 8px; border-bottom: 1px solid #ddd; }
            .normal { color: #059669; }
            .abnormal { color: #dc2626; font-weight: bold; }
            .signature { margin-top: 50px; display: flex; justify-content: flex-end; }
            .signature-box { text-align: center; }
            .signature-line { border-top: 1px solid #333; width: 200px; margin: 10px auto; }
            .footer { margin-top: 50px; text-align: center; font-size: 10px; color: #999; }
            .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); 
                         font-size: 80px; color: rgba(0,0,0,0.05); z-index: 0; }
            .validated { color: #059669; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="watermark">VALIDÉ</div>
        
        <div class="header">
            <div class="logo">{{ hospital_name }}</div>
            <div class="hospital-info">
                {{ hospital_address }}<br>
                Tél: {{ hospital_phone }} | Email: {{ hospital_email }}<br>
                N° SIRET: {{ hospital_siret }}
            </div>
        </div>
        
        <h2 style="text-align: center; color: #374151;">RÉSULTATS D'EXAMENS DE LABORATOIRE</h2>
        
        <div class="patient-info">
            <strong>Patient:</strong> {{ patient_nom }} {{ patient_prenom }}<br>
            <strong>Date de naissance:</strong> {{ patient_naissance }}<br>
            <strong>Sexe:</strong> {{ patient_sexe }}<br>
            <strong>Numéro patient:</strong> {{ patient_numero }}
        </div>
        
        <div class="exam-info">
            <strong>Numéro d'examen:</strong> {{ examen_numero }}<br>
            <strong>Date de prescription:</strong> {{ date_prescription }}<br>
            <strong>Date de validation:</strong> {{ date_validation }}<br>
            <strong>Prescripteur:</strong> {{ prescripteur_nom }} {{ prescripteur_prenom }}<br>
            <strong>Biologiste validateur:</strong> {{ biologiste_nom }} {{ biologiste_prenom }}
        </div>
        
        <div class="result-section">
            <h3 style="color: #374151; border-bottom: 1px solid #ddd; padding-bottom: 5px;">RÉSULTATS</h3>
            
            <table class="result-table">
                <thead>
                    <tr>
                        <th>Paramètre</th>
                        <th>Valeur</th>
                        <th>Unité</th>
                        <th>Normale</th>
                        <th>Statut</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in resultats %}
                    <tr>
                        <td>{{ item.parameter }}</td>
                        <td class="{% if item.abnormal %}abnormal{% else %}normal{% endif %}">
                            {{ item.value }}
                        </td>
                        <td>{{ item.unit }}</td>
                        <td>{{ item.normal_range }}</td>
                        <td class="{% if item.abnormal %}abnormal{% else %}normal{% endif %}">
                            {% if item.abnormal %}ANORMAL{% else %}NORMAL{% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        {% if commentaires %}
        <div class="result-section">
            <h3 style="color: #374151; border-bottom: 1px solid #ddd; padding-bottom: 5px;">COMMENTAIRES</h3>
            <p style="background: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b;">
                {{ commentaires }}
            </p>
        </div>
        {% endif %}
        
        <div class="signature">
            <div class="signature-box">
                <div>{{ biologiste_nom }} {{ biologiste_prenom }}</div>
                <div>Biologiste Médical</div>
                <div class="signature-line"></div>
                <div style="font-size: 10px; color: #059669;">SIGNATURE ÉLECTRONIQUE</div>
                <div style="font-size: 10px;">{{ date_validation }}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Ce document est signé électroniquement et fait foi. Toute modification non tracée le rend nul.</p>
            <p>Document généré le {{ generation_date }} | N° de contrôle: {{ controle_number }}</p>
            <p>© {{ hospital_name }} - Système de Gestion Hospitalière et de Laboratoire</p>
        </div>
    </body>
    </html>
    """
    
    @staticmethod
    def generate(examen, resultats: list, commentaires: str = "") -> bytes:
        """
        Générer un PDF de résultats de laboratoire
        
        Args:
            examen: Instance ExamenLaboratoire
            resultats: Liste de dict avec les résultats
            commentaires: Commentaires du biologiste
        
        Returns:
            Bytes du PDF généré
        """
        if not WEASYPRINT_AVAILABLE and not REPORTLAB_AVAILABLE:
            raise ImportError("Veuillez installer WeasyPrint ou ReportLab")
        
        # Récupérer les informations du patient et du personnel
        patient = examen.patient
        prescripteur = examen.prescripteur
        biologiste = examen.valide_par
        
        # Contexte du template
        context = Context({
            'hospital_name': 'HÔPITAL CENTRAL',
            'hospital_address': '123 Avenue de la Santé, 75000 Ville',
            'hospital_phone': '+33 1 23 45 67 89',
            'hospital_email': 'contact@hopital.fr',
            'hospital_siret': '123 456 789 00012',
            'patient_nom': patient.nom,
            'patient_prenom': patient.prenom,
            'patient_naissance': patient.date_naissance.strftime('%d/%m/%Y'),
            'patient_sexe': 'M' if patient.sexe == 'M' else 'F',
            'patient_numero': patient.numero_securise,
            'examen_numero': examen.id,
            'date_prescription': examen.date_prescription.strftime('%d/%m/%Y %H:%M'),
            'date_validation': examen.date_validation.strftime('%d/%m/%Y %H:%M') if examen.date_validation else '',
            'prescripteur_nom': prescripteur.nom,
            'prescripteur_prenom': prescripteur.prenom,
            'biologiste_nom': biologiste.nom if biologiste else 'N/A',
            'biologiste_prenom': biologiste.prenom if biologiste else 'N/A',
            'resultats': resultats,
            'commentaires': commentaires,
            'generation_date': examen.date_validation.strftime('%d/%m/%Y %H:%M:%S') if examen.date_validation else '',
            'controle_number': f"CTRL-{examen.id}-{examen.date_validation.strftime('%Y%m%d')}" if examen.date_validation else '',
        })
        
        # Rendu du template HTML
        template = Template(ResultatLaboratoirePDF.HTML_TEMPLATE)
        html_content = template.render(context)
        
        if WEASYPRINT_AVAILABLE:
            # Génération avec WeasyPrint
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        
        elif REPORTLAB_AVAILABLE:
            # Génération avec ReportLab (fallback simple)
            return ResultatLaboratoirePDF._generate_reportlab(examen, resultats, commentaires)
    
    @staticmethod
    def _generate_reportlab(examen, resultats: list, commentaires: str = "") -> bytes:
        """Génération PDF fallback avec ReportLab"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre
        elements.append(Paragraph("RÉSULTATS D'EXAMENS DE LABORATOIRE", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Informations patient
        patient_info = [
            f"Patient: {examen.patient.nom} {examen.patient.prenom}",
            f"Numéro: {examen.patient.numero_securise}",
            f"Date de naissance: {examen.patient.date_naissance.strftime('%d/%m/%Y')}",
        ]
        elements.append(Paragraph("<b>Informations Patient</b>", styles['Heading2']))
        for info in patient_info:
            elements.append(Paragraph(info, styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Tableau des résultats
        if resultats:
            table_data = [['Paramètre', 'Valeur', 'Unité', 'Normale', 'Statut']]
            for item in resultats:
                status = 'ANORMAL' if item.get('abnormal', False) else 'NORMAL'
                table_data.append([
                    item['parameter'],
                    str(item['value']),
                    item.get('unit', ''),
                    item.get('normal_range', ''),
                    status
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        
        # Signature
        elements.append(Paragraph(f"Validé par: {examen.valide_par.nom} {examen.valide_par.prenom}" if examen.valide_par else "", styles['Normal']))
        
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    
    @staticmethod
    def generate_response(examen, resultats: list, commentaires: str = "") -> HttpResponse:
        """
        Générer une réponse HTTP avec le PDF
        
        Returns:
            HttpResponse avec le PDF en téléchargement
        """
        pdf_bytes = ResultatLaboratoirePDF.generate(examen, resultats, commentaires)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resultat_laboratoire_{examen.id}.pdf"'
        
        return response
