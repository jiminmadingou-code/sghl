"""Génération PDF pour factures."""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 13px; color: #1f2937; }}
  .header {{ display: flex; justify-content: space-between; border-bottom: 3px solid #1d4ed8; padding-bottom: 15px; margin-bottom: 25px; }}
  .logo {{ font-size: 22px; font-weight: bold; color: #1d4ed8; }}
  .facture-title {{ font-size: 28px; font-weight: bold; color: #1d4ed8; text-align: right; }}
  .facture-num {{ color: #6b7280; font-size: 14px; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }}
  .info-box {{ background: #f9fafb; padding: 15px; border-radius: 5px; }}
  .info-box h4 {{ margin: 0 0 8px 0; color: #374151; font-size: 12px; text-transform: uppercase; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th {{ background: #1d4ed8; color: white; padding: 10px; text-align: left; }}
  td {{ padding: 9px; border-bottom: 1px solid #e5e7eb; }}
  .total-section {{ text-align: right; margin-top: 20px; }}
  .total-row {{ display: flex; justify-content: flex-end; gap: 40px; padding: 5px 0; }}
  .total-final {{ font-size: 18px; font-weight: bold; color: #1d4ed8; border-top: 2px solid #1d4ed8; padding-top: 8px; }}
  .statut-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }}
  .statut-payee {{ background: #d1fae5; color: #065f46; }}
  .statut-attente {{ background: #fef3c7; color: #92400e; }}
  .statut-partielle {{ background: #dbeafe; color: #1e40af; }}
  .footer {{ margin-top: 50px; font-size: 10px; color: #9ca3af; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 10px; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <div class="logo">HÔPITAL CENTRAL</div>
    <div style="color:#6b7280; font-size:12px;">Système de Gestion Hospitalière et de Laboratoire<br>
    contact@hopital.example | +224 XXX XXX XXX</div>
  </div>
  <div>
    <div class="facture-title">FACTURE</div>
    <div class="facture-num">N° {facture_id}</div>
    <div class="facture-num">Date: {date_emission}</div>
    <div><span class="statut-badge statut-{statut_css}">{statut}</span></div>
  </div>
</div>

<div class="info-grid">
  <div class="info-box">
    <h4>Facturé à</h4>
    <strong>{patient_nom}</strong><br>
    N° Dossier: {patient_numero}<br>
    {patient_telephone}
  </div>
  <div class="info-box">
    <h4>Détails</h4>
    Type: {type_facture}<br>
    Émise le: {date_emission}<br>
    Échéance: {date_emission}
  </div>
</div>

<table>
  <thead><tr><th>Description</th><th style="text-align:right;">Montant</th></tr></thead>
  <tbody>
    <tr><td>{type_facture}</td><td style="text-align:right;">{montant_total} GNF</td></tr>
    {paiements_html}
  </tbody>
</table>

<div class="total-section">
  <div class="total-row"><span>Montant total:</span><span>{montant_total} GNF</span></div>
  <div class="total-row"><span>Montant payé:</span><span style="color:#059669;">{montant_paye} GNF</span></div>
  <div class="total-row total-final"><span>Solde restant:</span><span>{solde} GNF</span></div>
</div>

{notes_html}

<div class="footer">
  Document généré le {generation_date} — SGHL © NLP-Core-Team<br>
  Ce document est généré automatiquement et fait foi.
</div>
</body>
</html>"""


class FacturePDF:
    @staticmethod
    def generate(facture) -> bytes:
        paiements_html = ''.join(
            f"<tr style='color:#059669;'><td>Paiement — {p.mode_paiement} "
            f"({p.date_paiement.strftime('%d/%m/%Y')})</td>"
            f"<td style='text-align:right;'>-{p.montant} GNF</td></tr>"
            for p in facture.paiements.all()
        )
        notes_html = (
            f'<div style="background:#fef3c7;padding:12px;border-left:4px solid #f59e0b;margin-top:20px;">'
            f'<strong>Notes:</strong> {facture.notes}</div>'
            if facture.notes else ''
        )
        statut_css = {'Payée': 'payee', 'En attente': 'attente', 'Partielle': 'partielle'}.get(facture.statut, 'attente')

        html = HTML_TEMPLATE.format(
            facture_id=facture.id,
            date_emission=facture.date_emission.strftime('%d/%m/%Y') if hasattr(facture.date_emission, 'strftime') else str(facture.date_emission),
            statut=facture.statut,
            statut_css=statut_css,
            patient_nom=f"{facture.patient.prenom} {facture.patient.nom}",
            patient_numero=facture.patient.numero_securise,
            patient_telephone=facture.patient.telephone or '',
            type_facture=facture.type_facture,
            montant_total=facture.montant_total,
            montant_paye=facture.montant_paye,
            solde=facture.solde,
            paiements_html=paiements_html,
            notes_html=notes_html,
            generation_date=timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        )

        try:
            from weasyprint import HTML
            return HTML(string=html).write_pdf()
        except ImportError:
            logger.warning("WeasyPrint non disponible")
            return html.encode('utf-8')
