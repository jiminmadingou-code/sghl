"""Génération PDF pour ordonnances électroniques."""
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 13px; }}
  .header {{ text-align: center; border-bottom: 2px solid #1d4ed8; padding-bottom: 15px; margin-bottom: 20px; }}
  .logo {{ font-size: 22px; font-weight: bold; color: #1d4ed8; }}
  .section {{ margin-bottom: 15px; }}
  .label {{ font-weight: bold; color: #374151; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th {{ background: #1d4ed8; color: white; padding: 8px; text-align: left; }}
  td {{ padding: 7px; border-bottom: 1px solid #e5e7eb; }}
  .signature {{ margin-top: 60px; text-align: right; }}
  .sig-line {{ border-top: 1px solid #333; width: 200px; display: inline-block; margin-top: 40px; }}
  .footer {{ margin-top: 40px; font-size: 10px; color: #9ca3af; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 10px; }}
  .stamp {{ color: #059669; font-weight: bold; font-size: 14px; }}
</style>
</head>
<body>
<div class="header">
  <div class="logo">HÔPITAL CENTRAL — SGHL</div>
  <div>Système de Gestion Hospitalière et de Laboratoire</div>
</div>
<h2 style="text-align:center; color:#1d4ed8;">ORDONNANCE MÉDICALE</h2>
<div class="section">
  <span class="label">N° Ordonnance:</span> {prescription_id}<br>
  <span class="label">Date:</span> {date_prescription}<br>
  <span class="label">Validité:</span> {date_validite}
</div>
<div class="section">
  <span class="label">Patient:</span> {patient_nom}<br>
  <span class="label">Date de naissance:</span> {patient_naissance}<br>
  <span class="label">N° Dossier:</span> {patient_numero}
</div>
<div class="section">
  <span class="label">Prescripteur:</span> Dr {medecin_nom}<br>
  <span class="label">Service:</span> {medecin_service}
</div>
<table>
  <thead><tr><th>Médicament</th><th>Posologie</th><th>Durée</th><th>Qté</th><th>Instructions</th></tr></thead>
  <tbody>{lignes_html}</tbody>
</table>
{notes_html}
<div class="signature">
  <div class="stamp">✓ SIGNÉ ÉLECTRONIQUEMENT</div>
  <div>Dr {medecin_nom}</div>
  <div class="sig-line"></div>
  <div style="font-size:10px;">Hash: {signature_hash}</div>
</div>
<div class="footer">
  Document généré le {generation_date} — Ce document est signé électroniquement et fait foi légale.<br>
  © SGHL — NLP-Core-Team
</div>
</body>
</html>"""


class OrdonnancePDF:
    @staticmethod
    def generate(prescription) -> bytes:
        from django.utils import timezone

        lignes_html = ''.join(
            f"<tr><td>{l.medicament.nom}</td><td>{l.posologie}</td>"
            f"<td>{l.duree_jours}j</td><td>{l.quantite}</td><td>{l.instructions}</td></tr>"
            for l in prescription.lignes.all()
        )
        notes_html = (
            f'<div class="section"><span class="label">Notes:</span> {prescription.notes}</div>'
            if prescription.notes else ''
        )

        html = HTML_TEMPLATE.format(
            prescription_id=prescription.id,
            date_prescription=prescription.date_prescription.strftime('%d/%m/%Y %H:%M'),
            date_validite=prescription.date_validite.strftime('%d/%m/%Y') if prescription.date_validite else 'Non définie',
            patient_nom=f"{prescription.patient.prenom} {prescription.patient.nom}",
            patient_naissance=prescription.patient.date_naissance.strftime('%d/%m/%Y'),
            patient_numero=prescription.patient.numero_securise,
            medecin_nom=prescription.medecin.full_name,
            medecin_service=prescription.medecin.service or 'N/A',
            lignes_html=lignes_html,
            notes_html=notes_html,
            signature_hash=prescription.signature_hash or 'Non signé',
            generation_date=timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        )

        try:
            from weasyprint import HTML
            return HTML(string=html).write_pdf()
        except ImportError:
            logger.warning("WeasyPrint non disponible, retour HTML brut")
            return html.encode('utf-8')
