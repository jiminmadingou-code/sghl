// Service utilitaire pour générer et télécharger des PDF via impression HTML
export function generateAndDownloadPDF(title, htmlContent, filename) {
  const win = window.open('', '_blank', 'width=900,height=700')
  if (!win) {
    alert('Veuillez autoriser les popups pour télécharger le PDF.')
    return
  }
  win.document.write(`
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <title>${title}</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }
        body { padding: 30px; color: #111; background: white; font-size: 13px; }
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #1d4ed8; padding-bottom: 16px; margin-bottom: 24px; }
        .hospital-name { font-size: 20px; font-weight: 900; color: #1d4ed8; }
        .hospital-sub { font-size: 11px; color: #6b7280; margin-top: 2px; }
        .doc-title { font-size: 16px; font-weight: 700; color: #111; margin-bottom: 4px; }
        .doc-date { font-size: 11px; color: #6b7280; }
        .section { margin-bottom: 20px; }
        .section-title { font-size: 13px; font-weight: 700; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.05em; border-left: 3px solid #1d4ed8; padding-left: 8px; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th { background: #eff6ff; color: #1e40af; font-weight: 700; padding: 8px 10px; text-align: left; border-bottom: 2px solid #bfdbfe; }
        td { padding: 7px 10px; border-bottom: 1px solid #f1f5f9; color: #374151; }
        tr:nth-child(even) td { background: #f8faff; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 700; }
        .badge-green { background: #dcfce7; color: #166534; }
        .badge-red { background: #fee2e2; color: #991b1b; }
        .badge-amber { background: #fef9c3; color: #854d0e; }
        .badge-blue { background: #dbeafe; color: #1e40af; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
        .info-box { background: #f8faff; border: 1px solid #dbeafe; border-radius: 8px; padding: 12px; }
        .info-label { font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600; margin-bottom: 3px; }
        .info-value { font-size: 14px; font-weight: 700; color: #111; }
        .footer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #9ca3af; display: flex; justify-content: space-between; }
        .watermark { color: #1d4ed8; font-weight: 700; }
        .alert-box { background: #fef9c3; border: 1px solid #fcd34d; border-left: 3px solid #f59e0b; border-radius: 6px; padding: 10px; margin: 10px 0; font-size: 11px; color: #854d0e; }
        .signature-zone { margin-top: 40px; display: flex; justify-content: space-between; }
        .sig-box { text-align: center; width: 160px; }
        .sig-line { border-top: 1px solid #374151; margin-top: 50px; padding-top: 5px; font-size: 11px; color: #6b7280; }
        @media print {
          body { padding: 15px; }
          button { display: none !important; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <div class="hospital-name">🏥 DIGNE HOSPITAL</div>
          <div class="hospital-sub">Centre Hospitalier Universitaire · SGHL v2.0</div>
          <div class="hospital-sub">Avenue de la République, Kaloum — Conakry, Guinée</div>
        </div>
        <div style="text-align:right">
          <div class="doc-title">${title}</div>
          <div class="doc-date">Généré le ${new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })} à ${new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
      </div>
      ${htmlContent}
      <div class="footer">
        <span>DIGNE HOSPITAL — Document généré par SGHL v2.0</span>
        <span class="watermark">Document officiel — Confidentiel</span>
        <span>Page 1/1</span>
      </div>
      <script>
        setTimeout(() => { window.print(); }, 400);
      <\/script>
    </body>
    </html>
  `)
  win.document.close()
}

// PDF Livret d'accueil
export function downloadLivretPDF(patientName = 'Patient') {
  const html = `
    <div class="info-grid">
      <div class="info-box">
        <div class="info-label">Patient</div>
        <div class="info-value">${patientName}</div>
      </div>
      <div class="info-box">
        <div class="info-label">Établissement</div>
        <div class="info-value">DIGNE HOSPITAL — CHU</div>
      </div>
    </div>
    <div class="section">
      <div class="section-title">Bienvenue</div>
      <p style="line-height:1.7;color:#374151">L'ensemble du personnel médical, soignant et administratif vous souhaite la bienvenue et met tout en œuvre pour assurer votre confort et la qualité de votre prise en charge au DIGNE HOSPITAL.</p>
    </div>
    <div class="section">
      <div class="section-title">Informations pratiques</div>
      <table>
        <tr><td style="font-weight:700;width:40%">Horaires d'accueil</td><td>Lun–Ven : 07h00 – 18h00 · Urgences : 24h/24 – 7j/7</td></tr>
        <tr><td style="font-weight:700">Standard général</td><td>+224 620 000 000</td></tr>
        <tr><td style="font-weight:700">Urgences</td><td>+224 620 000 001</td></tr>
        <tr><td style="font-weight:700">Rendez-vous</td><td>+224 620 000 004</td></tr>
        <tr><td style="font-weight:700">Wi-Fi patient</td><td>Réseau : CHU-Patient (gratuit)</td></tr>
        <tr><td style="font-weight:700">Parking</td><td>Gratuit — devant le bâtiment principal</td></tr>
      </table>
    </div>
    <div class="section">
      <div class="section-title">Vos droits fondamentaux</div>
      <table>
        <tr><td>✓ Droit à l'information sur votre état de santé</td></tr>
        <tr><td>✓ Droit au consentement libre et éclairé</td></tr>
        <tr><td>✓ Droit à la confidentialité et au secret médical</td></tr>
        <tr><td>✓ Droit d'accès à votre dossier médical (délai : 8 jours)</td></tr>
        <tr><td>✓ Droit à la prise en charge de la douleur</td></tr>
      </table>
    </div>
    <div class="section">
      <div class="section-title">Horaires des repas</div>
      <table>
        <tr><th>Repas</th><th>Horaire</th></tr>
        <tr><td>Petit-déjeuner</td><td>07h00 – 08h30</td></tr>
        <tr><td>Déjeuner</td><td>12h00 – 13h30</td></tr>
        <tr><td>Dîner</td><td>18h30 – 20h00</td></tr>
      </table>
    </div>
    <div class="alert-box">⚠ Ce document est fourni à titre informatif. Pour toute urgence médicale, composez le +224 620 000 001 ou appelez le SAMU : 15</div>
    <div class="signature-zone">
      <div class="sig-box"><div class="sig-line">Direction médicale</div></div>
      <div class="sig-box"><div class="sig-line">Cachet de l'établissement</div></div>
    </div>
  `
  generateAndDownloadPDF('Livret d\'accueil patient', html, 'livret_accueil.pdf')
}

// PDF Résultat d'examen
export function downloadResultatPDF(resultat) {
  const alertes = resultat.valeurs.filter(v => v.alerte)
  const html = `
    <div class="info-grid">
      <div class="info-box"><div class="info-label">Type d'examen</div><div class="info-value">${resultat.type}</div></div>
      <div class="info-box"><div class="info-label">Date</div><div class="info-value">${resultat.date}</div></div>
      <div class="info-box"><div class="info-label">Prescripteur</div><div class="info-value">${resultat.prescripteur}</div></div>
      <div class="info-box"><div class="info-label">Biologiste valideur</div><div class="info-value">${resultat.biologiste}</div></div>
    </div>
    ${alertes.length ? `<div class="alert-box">⚠ ${alertes.length} valeur(s) hors normes détectée(s) — Consultez votre médecin</div>` : ''}
    <div class="section">
      <div class="section-title">Résultats détaillés</div>
      <table>
        <tr><th>Paramètre</th><th>Valeur</th><th>Unité</th><th>Valeurs de référence</th><th>Statut</th></tr>
        ${resultat.valeurs.map(v => `
          <tr>
            <td style="font-weight:600">${v.nom}</td>
            <td style="font-weight:700;color:${v.alerte ? '#dc2626' : '#111'}">${v.val}</td>
            <td>${v.unite}</td>
            <td>${v.ref}</td>
            <td><span class="badge ${v.alerte ? 'badge-red' : 'badge-green'}">${v.alerte ? '⚠ Anormal' : '✓ Normal'}</span></td>
          </tr>`).join('')}
      </table>
    </div>
    <div class="section">
      <div class="section-title">Commentaire</div>
      <p style="color:#374151;line-height:1.6">Ces résultats ont été validés par ${resultat.biologiste}. Tout résultat hors norme doit être interprété dans le contexte clinique du patient par un médecin qualifié.</p>
    </div>
    <div class="signature-zone">
      <div class="sig-box"><div class="sig-line">Biologiste valideur<br>${resultat.biologiste}</div></div>
      <div class="sig-box"><div class="sig-line">Cachet laboratoire</div></div>
    </div>
  `
  generateAndDownloadPDF(`Résultat — ${resultat.type}`, html, `resultat_${resultat.type.replace(/\s/g,'_')}_${resultat.date}.pdf`)
}

// PDF Ordonnance
export function downloadOrdonnancePDF(ordonnance) {
  const html = `
    <div class="info-grid">
      <div class="info-box"><div class="info-label">Médecin prescripteur</div><div class="info-value">${ordonnance.medecin}</div></div>
      <div class="info-box"><div class="info-label">Service</div><div class="info-value">${ordonnance.service}</div></div>
      <div class="info-box"><div class="info-label">Date de prescription</div><div class="info-value">${ordonnance.date}</div></div>
      <div class="info-box"><div class="info-label">Valide jusqu'au</div><div class="info-value" style="color:${ordonnance.statut==='Expirée'?'#dc2626':'#16a34a'}">${ordonnance.valide_jusqu} <span class="badge ${ordonnance.statut==='Valide'?'badge-green':'badge-red'}">${ordonnance.statut}</span></div></div>
    </div>
    <div class="section">
      <div class="section-title">Médicaments prescrits</div>
      <table>
        <tr><th>#</th><th>Médicament</th><th>Posologie</th><th>Durée</th><th>Quantité</th></tr>
        ${ordonnance.medicaments.map((m, i) => `
          <tr>
            <td>${i + 1}</td>
            <td style="font-weight:700">${m.nom}</td>
            <td>${m.posologie}</td>
            <td>${m.duree}</td>
            <td style="font-weight:700;text-align:center">${m.qte}</td>
          </tr>`).join('')}
      </table>
    </div>
    <div class="alert-box">⚠ Ne jamais interrompre un traitement sans l'accord de votre médecin. En cas d'effets indésirables, contactez immédiatement votre médecin.</div>
    <div class="signature-zone">
      <div class="sig-box"><div class="sig-line">Signature du médecin<br>${ordonnance.medecin}</div></div>
      <div class="sig-box"><div class="sig-line">Cachet médical</div></div>
    </div>
  `
  generateAndDownloadPDF(`Ordonnance du ${ordonnance.date}`, html, `ordonnance_${ordonnance.date}.pdf`)
}

// PDF Facture
export function downloadFacturePDF(facture) {
  const reste = facture.montant - facture.paye
  const html = `
    <div class="info-grid">
      <div class="info-box"><div class="info-label">N° Facture</div><div class="info-value" style="font-family:monospace">${facture.id}</div></div>
      <div class="info-box"><div class="info-label">Date</div><div class="info-value">${facture.date}</div></div>
      <div class="info-box"><div class="info-label">Type de prestation</div><div class="info-value">${facture.type}</div></div>
      <div class="info-box"><div class="info-label">Statut</div><div class="info-value"><span class="badge ${facture.statut==='Payée'?'badge-green':facture.statut==='Partielle'?'badge-amber':'badge-red'}">${facture.statut}</span></div></div>
    </div>
    <div class="section">
      <div class="section-title">Détail de la facture</div>
      <table>
        <tr><th>Désignation</th><th style="text-align:right">Montant</th></tr>
        <tr><td>${facture.detail}</td><td style="text-align:right;font-weight:700">${facture.montant.toLocaleString('fr-FR')} GNF</td></tr>
        ${facture.assurance_nom ? `<tr><td style="color:#16a34a">🏦 Prise en charge ${facture.assurance_nom}</td><td style="text-align:right;color:#16a34a;font-weight:700">- ${facture.assurance.toLocaleString('fr-FR')} GNF</td></tr>` : ''}
        <tr style="background:#f8faff"><td style="font-weight:700">Déjà réglé</td><td style="text-align:right;color:#16a34a;font-weight:700">${facture.paye.toLocaleString('fr-FR')} GNF</td></tr>
        <tr style="background:#fef9c3"><td style="font-weight:900;font-size:14px">RESTE À PAYER</td><td style="text-align:right;font-weight:900;font-size:14px;color:${reste>0?'#dc2626':'#16a34a'}">${reste.toLocaleString('fr-FR')} GNF</td></tr>
      </table>
    </div>
    ${reste > 0 ? `<div class="alert-box">⚠ Solde restant : ${reste.toLocaleString('fr-FR')} GNF. Modes de paiement : Orange Money, Airtel Money, virement bancaire ou paiement à la caisse.</div>` : '<div style="background:#dcfce7;border:1px solid #86efac;border-radius:6px;padding:10px;color:#166534;font-weight:700;margin:10px 0">✅ Facture entièrement réglée. Merci !</div>'}
    <div class="signature-zone">
      <div class="sig-box"><div class="sig-line">Service facturation</div></div>
      <div class="sig-box"><div class="sig-line">Cachet comptable</div></div>
    </div>
  `
  generateAndDownloadPDF(`Facture ${facture.id}`, html, `facture_${facture.id}.pdf`)
}
