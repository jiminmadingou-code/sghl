/**
 * SGHL — Mock API Service
 * Intercepte toutes les requêtes /api/v1/ et retourne des données réalistes.
 * Fonctionne sans backend Django. Activé automatiquement si le backend est inaccessible.
 */

// ── Données démo persistantes en mémoire ─────────────────────────────────────
const DB = {
  patients: [
    { id: 1, nom: 'Koné',    prenom: 'Fatoumata', date_naissance: '1992-07-22', sexe: 'F', telephone: '+242 06 100 0001', groupe_sanguin: 'O+',  statut: 'Hospitalisé', adresse: 'Avenue Charles de Gaulle, Pointe-Noire', allergies: '',            antecedents: 'Asthme' },
    { id: 2, nom: 'Traoré',  prenom: 'Ibrahim',   date_naissance: '1957-11-08', sexe: 'M', telephone: '+242 06 100 0002', groupe_sanguin: 'B-',  statut: 'Actif',        adresse: 'Rue Bouiti, Pointe-Noire',             allergies: 'Aspirine',    antecedents: 'Cardiopathie' },
    { id: 3, nom: 'Bah',     prenom: 'Aissatou',  date_naissance: '1996-01-30', sexe: 'F', telephone: '+242 06 100 0003', groupe_sanguin: 'AB+', statut: 'Sorti',        adresse: 'Quartier Tié-Tié, Pointe-Noire',      allergies: '',            antecedents: '' },
    { id: 4, nom: 'Camara',  prenom: 'Sekou',     date_naissance: '1970-05-12', sexe: 'M', telephone: '+242 06 100 0004', groupe_sanguin: 'O-',  statut: 'Actif',        adresse: 'Avenue de l\'Indépendance',            allergies: '',            antecedents: 'Drépanocytose' },
    { id: 5, nom: 'Sylla',   prenom: 'Oumou',     date_naissance: '1988-09-03', sexe: 'F', telephone: '+242 06 100 0005', groupe_sanguin: 'A-',  statut: 'Actif',        adresse: 'Rue Poaty Bernard, Pointe-Noire',     allergies: '',            antecedents: '' },
    { id: 6, nom: 'Barry',   prenom: 'Mariama',   date_naissance: '2001-04-18', sexe: 'F', telephone: '+242 06 100 0006', groupe_sanguin: 'B+',  statut: 'Actif',        adresse: 'Quartier Loandjili, Pointe-Noire',    allergies: '',            antecedents: '' },
  ],

  hospitalisations: [
    { id: 1, patient: 'Koné Fatoumata',  patient_id: 1, service: 'Médecine interne', chambre: 'C-12', lit: 'L-02', medecin: 'Dr. Camara', entree: '2025-06-08', sortie_prev: '2025-06-15', statut: 'Actif' },
    { id: 2, patient: 'Traoré Ibrahim',  patient_id: 2, service: 'Cardiologie',      chambre: 'C-05', lit: 'L-01', medecin: 'Dr. Bah',    entree: '2025-06-10', sortie_prev: '2025-06-18', statut: 'Actif' },
    { id: 3, patient: 'Sylla Oumou',     patient_id: 5, service: 'Maternité',        chambre: 'M-03', lit: 'L-04', medecin: 'Dr. Diallo', entree: '2025-06-11', sortie_prev: '2025-06-13', statut: 'Sorti' },
  ],

  examens: [
    { id: 1, patient: 'Koné Fatoumata',  type: 'NFS',          prescripteur: 'Dr. Camara', date: '2025-06-12', priorite: 'Urgent', statut: 'Prélèvement',     technicien: 'Lab. Kouyaté' },
    { id: 2, patient: 'Traoré Ibrahim',  type: 'Glycémie',     prescripteur: 'Dr. Bah',    date: '2025-06-12', priorite: 'Normal', statut: 'Saisie résultats', technicien: 'Lab. Kouyaté' },
    { id: 3, patient: 'Bah Aissatou',    type: 'ECG',          prescripteur: 'Dr. Diallo', date: '2025-06-11', priorite: 'Normal', statut: 'Validé',           technicien: 'Lab. Sylla' },
    { id: 4, patient: 'Camara Sekou',    type: 'Radiographie', prescripteur: 'Dr. Camara', date: '2025-06-11', priorite: 'Urgent', statut: 'Publié',           technicien: 'Lab. Sylla' },
    { id: 5, patient: 'Barry Mariama',   type: 'Urine ECBU',   prescripteur: 'Dr. Bah',    date: '2025-06-10', priorite: 'Normal', statut: 'Commande',         technicien: '-' },
  ],

  medicaments: [
    { id: 1, nom: 'Artémether 80mg',    categorie: 'Antipaludéen',      stock: 245, seuil: 50,  lot: 'LOT-2025-001', peremption: '2026-08-01', statut: 'Normal' },
    { id: 2, nom: 'Amlodipine 5mg',     categorie: 'Antihypertenseur',  stock: 32,  seuil: 50,  lot: 'LOT-2025-002', peremption: '2026-03-15', statut: 'Alerte' },
    { id: 3, nom: 'Metformine 500mg',   categorie: 'Antidiabétique',    stock: 180, seuil: 40,  lot: 'LOT-2025-003', peremption: '2027-01-20', statut: 'Normal' },
    { id: 4, nom: 'Amoxicilline 500mg', categorie: 'Antibiotique',      stock: 8,   seuil: 30,  lot: 'LOT-2025-004', peremption: '2025-12-10', statut: 'Rupture' },
    { id: 5, nom: 'Paracétamol 500mg',  categorie: 'Analgésique',       stock: 520, seuil: 100, lot: 'LOT-2025-005', peremption: '2026-11-30', statut: 'Normal' },
  ],

  factures: [
    { id: 'F-2025-001', patient: 'Koné Fatoumata',  date: '2025-06-12', montant: 450000,  paye: 450000,  statut: 'Payée',      type: 'Consultation'    },
    { id: 'F-2025-002', patient: 'Traoré Ibrahim',  date: '2025-06-10', montant: 2800000, paye: 1400000, statut: 'Partielle',  type: 'Hospitalisation' },
    { id: 'F-2025-003', patient: 'Bah Aissatou',    date: '2025-06-11', montant: 180000,  paye: 0,       statut: 'En attente', type: 'Examens'         },
    { id: 'F-2025-004', patient: 'Camara Sekou',    date: '2025-06-09', montant: 95000,   paye: 95000,   statut: 'Payée',      type: 'Pharmacie'       },
    { id: 'F-2025-005', patient: 'Barry Mariama',   date: '2025-06-08', montant: 320000,  paye: 0,       statut: 'En attente', type: 'Consultation'    },
  ],

  personnel: [
    { id: 1, nom: 'Camara',   prenom: 'Alpha',    role: 'Médecin',    service: 'Médecine interne', email: 'a.camara@sghl.cg',    telephone: '+242 06 200 001', statut: 'Actif' },
    { id: 2, nom: 'Bah',      prenom: 'Oumar',    role: 'Médecin',    service: 'Cardiologie',      email: 'o.bah@sghl.cg',       telephone: '+242 06 200 002', statut: 'Actif' },
    { id: 3, nom: 'Diallo',   prenom: 'Mariama',  role: 'Infirmier',  service: 'Urgences',         email: 'm.diallo@sghl.cg',    telephone: '+242 06 200 003', statut: 'Actif' },
    { id: 4, nom: 'Sylla',    prenom: 'Kadiatou', role: 'Pharmacien', service: 'Pharmacie',        email: 'k.sylla@sghl.cg',     telephone: '+242 06 200 004', statut: 'Actif' },
    { id: 5, nom: 'Kouyaté',  prenom: 'Ibrahima', role: 'Biologiste', service: 'Laboratoire',      email: 'i.kouyate@sghl.cg',   telephone: '+242 06 200 005', statut: 'Actif' },
  ],

  audit: [
    { id: 1, user: 'Dr. Camara',   action: 'CONSULTATION_CREATE', module: 'Patients',      timestamp: '2025-06-12T09:14:22', ip: '192.168.1.10', details: 'Consultation créée pour Koné Fatoumata' },
    { id: 2, user: 'Lab. Kouyaté', action: 'EXAM_VALIDATE',       module: 'Laboratoire',   timestamp: '2025-06-12T10:05:11', ip: '192.168.1.22', details: 'Examen NFS validé' },
    { id: 3, user: 'Inf. Traoré',  action: 'CONSTANTE_SAISIE',    module: 'Soins',         timestamp: '2025-06-12T10:30:00', ip: '192.168.1.15', details: 'Constantes vitales saisies — Traoré Ibrahim' },
    { id: 4, user: 'admin',        action: 'USER_LOGIN',          module: 'Auth',          timestamp: '2025-06-12T08:00:00', ip: '192.168.1.1',  details: 'Connexion administrateur' },
    { id: 5, user: 'Caissier',     action: 'FACTURE_CREATE',      module: 'Facturation',   timestamp: '2025-06-12T11:00:00', ip: '192.168.1.30', details: 'Facture F-2025-005 créée' },
  ],
}

// ── Réponse mock ──────────────────────────────────────────────────────────────
function ok(data) { return Promise.resolve({ data, status: 200 }) }

// ── Table de routage mock ─────────────────────────────────────────────────────
const MOCK_ROUTES = [
  // Auth
  { method: 'POST', pattern: /\/auth\/login\//,                handler: loginHandler },
  { method: 'POST', pattern: /\/auth\/send-confirm-code\//,    handler: () => ok({ status: 'sent' }) },
  { method: 'POST', pattern: /\/auth\/verify-confirm-code\//, handler: () => ok({ status: 'confirmed' }) },

  // Dashboard
  { method: 'GET', pattern: /\/dashboard\/summary/,            handler: () => ok({
    patients_totaux: 248, patients_hospitalises: 87, hospitalisations_actives: 3,
    taux_occupation: 72.5, examens_en_attente: 12, examens_a_valider: 5,
    alertes_stock: 3, chiffre_affaires_jour: 1850000, chiffre_affaires_mois: 24500000,
  })},
  { method: 'GET', pattern: /\/dashboard\/kpi\/hospitalisations/, handler: () => ok({ admissions: 63, sorties: 58, sejour_moyen_jours: 4.2, actives: 3 }) },
  { method: 'GET', pattern: /\/dashboard\/kpi\/laboratoire/,      handler: () => ok({ examens_total: 312, valides: 287, en_cours: 25, temps_moyen_heures: 3.4 }) },
  { method: 'GET', pattern: /\/dashboard\/kpi\/finances/,         handler: () => ok({ factures_total: 142, recette_totale: 24500000, en_attente_paiement: 8200000, taux_recouvrement: 74.9 }) },
  { method: 'GET', pattern: /\/dashboard\/charts\/occupation/,    handler: () => ok({ labels: ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'], values: [68,72,70,75,74,65,60] }) },
  { method: 'GET', pattern: /\/dashboard\/health/,               handler: () => ok({ status: 'ok', database: 'ok', cache: 'ok', patients_total: 248 }) },

  // Patients
  { method: 'GET',  pattern: /\/patients\/$/, handler: (_, p) => {
    let list = [...DB.patients]
    if (p?.search) list = list.filter(x => `${x.nom} ${x.prenom}`.toLowerCase().includes(p.search.toLowerCase()))
    return ok({ results: list, count: list.length })
  }},
  { method: 'POST', pattern: /\/patients\/$/,  handler: (body) => {
    const p = { id: Date.now(), statut: 'Actif', ...body }
    DB.patients.unshift(p); return ok(p)
  }},
  { method: 'GET',  pattern: /\/patients\/\d+$/, handler: (_, __, url) => {
    const id = parseInt(url.split('/').filter(Boolean).pop())
    return ok(DB.patients.find(p => p.id === id) || DB.patients[0])
  }},

  // Hospitalisations
  { method: 'GET',  pattern: /\/hospitalisations\//, handler: () => ok({ results: DB.hospitalisations, count: DB.hospitalisations.length }) },
  { method: 'POST', pattern: /\/hospitalisations\//, handler: (body) => {
    const h = { id: Date.now(), statut: 'Actif', ...body }
    DB.hospitalisations.unshift(h); return ok(h)
  }},

  // Laboratoire
  { method: 'GET',  pattern: /\/laboratoire\/$/,       handler: () => ok({ results: DB.examens, count: DB.examens.length }) },
  { method: 'POST', pattern: /\/laboratoire\/$/,        handler: (body) => {
    const e = { id: Date.now(), statut: 'Commande', technicien: '-', date: new Date().toISOString().slice(0,10), ...body }
    DB.examens.unshift(e); return ok(e)
  }},
  { method: 'PATCH', pattern: /\/laboratoire\/\d+\/avancer/, handler: (_, __, url) => {
    const id = parseInt(url.match(/\/laboratoire\/(\d+)\//)?.[1])
    const workflow = ['Commande','Prélèvement','Affectation','Saisie résultats','Validé','Publié']
    const e = DB.examens.find(x => x.id === id)
    if (e) { const i = workflow.indexOf(e.statut); if (i < workflow.length-1) e.statut = workflow[i+1] }
    return ok(e || {})
  }},

  // Pharmacie
  { method: 'GET',  pattern: /\/pharmacie\/inventaire\//,  handler: () => ok({ results: DB.medicaments }) },
  { method: 'GET',  pattern: /\/pharmacie\/alertes\//,      handler: () => ok(DB.medicaments.filter(m => m.statut !== 'Normal')) },
  { method: 'GET',  pattern: /\/pharmacie\/medicaments\//,  handler: () => ok({ results: DB.medicaments }) },
  { method: 'POST', pattern: /\/pharmacie\/stocks\//,       handler: (body) => {
    const med = DB.medicaments.find(m => m.id === body.medicament_id)
    if (med) { med.stock += body.quantite || 0; med.statut = med.stock >= med.seuil ? 'Normal' : med.stock > 0 ? 'Alerte' : 'Rupture' }
    return ok({ message: 'Stock mis à jour' })
  }},

  // Facturation
  { method: 'GET',  pattern: /\/facturation\/$/,  handler: () => ok({ results: DB.factures, count: DB.factures.length }) },
  { method: 'POST', pattern: /\/facturation\/$/,   handler: (body) => {
    const f = { id: `F-2025-${String(DB.factures.length+1).padStart(3,'0')}`, paye: 0, statut: 'En attente', date: new Date().toISOString().slice(0,10), ...body }
    DB.factures.unshift(f); return ok(f)
  }},
  { method: 'POST', pattern: /\/facturation\/.*\/paiement\//, handler: (body, _, url) => {
    const id = url.split('/').filter(Boolean).find((_, i, a) => a[i-1] === 'facturation')
    const f = DB.factures.find(x => x.id === id)
    if (f) { f.paye = Math.min(f.montant, f.paye + (body.montant || 0)); f.statut = f.paye >= f.montant ? 'Payée' : f.paye > 0 ? 'Partielle' : 'En attente' }
    return ok(f || {})
  }},

  // Personnel
  { method: 'GET',  pattern: /\/personnel\/$/,   handler: () => ok({ results: DB.personnel }) },
  { method: 'GET',  pattern: /\/personnel\/stats/, handler: () => ok({ total: DB.personnel.length, medecins: 2, infirmiers: 1, biologistes: 1, pharmaciens: 1 }) },
  { method: 'POST', pattern: /\/personnel\/$/,    handler: (body) => {
    const p = { id: Date.now(), statut: 'Actif', ...body }
    DB.personnel.push(p); return ok(p)
  }},

  // Soins
  { method: 'GET',  pattern: /\/soins\/planning\//, handler: () => ok({ results: [] }) },
  { method: 'GET',  pattern: /\/soins\/constantes/, handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/soins\/constantes\//, handler: (body) => ok({ id: Date.now(), ...body }) },

  // Rendez-vous
  { method: 'GET',  pattern: /\/rendez-vous\/$/,  handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/rendez-vous\/$/,   handler: (body) => ok({ id: Date.now(), statut: 'Confirmé', ...body }) },

  // Urgences
  { method: 'GET',  pattern: /\/urgences\/$/,    handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/urgences\/$/,     handler: (body) => ok({ id: Date.now(), statut: 'En attente', ...body }) },
  { method: 'GET',  pattern: /\/urgences\/stats/, handler: () => ok({ total: 6, p1: 1, p2: 2, attente_moy: 28 }) },

  // Imagerie
  { method: 'GET',  pattern: /\/imagerie\/$/,   handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/imagerie\/$/,    handler: (body) => ok({ id: Date.now(), statut: 'Prescrit', ...body }) },

  // Bloc opératoire
  { method: 'GET',  pattern: /\/bloc-operatoire\/$/,   handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/bloc-operatoire\/$/,    handler: (body) => ok({ id: Date.now(), statut: 'Programmée', ...body }) },

  // Maternité
  { method: 'GET',  pattern: /\/maternite\/$/,    handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/maternite\/$/,     handler: (body) => ok({ id: Date.now(), statut: 'En cours', ...body }) },
  { method: 'GET',  pattern: /\/maternite\/stats/, handler: () => ok({ en_cours: 4, terme_proche: 1, risque_eleve: 1 }) },

  // Téléconsultation
  { method: 'GET',  pattern: /\/teleconsultation\/$/,   handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/teleconsultation\/$/,    handler: (body) => ok({ id: Date.now(), statut: 'Planifiée', ...body }) },

  // Prescriptions
  { method: 'GET',  pattern: /\/prescriptions\/$/,  handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/prescriptions\/$/,   handler: (body) => ok({ id: Date.now(), statut: 'Active', ...body }) },

  // Gardes
  { method: 'GET',  pattern: /\/gardes\/planning\//, handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/gardes\/planning\//, handler: (body) => ok({ id: Date.now(), ...body }) },

  // Consultations
  { method: 'GET',  pattern: /\/patients\/consultations\//, handler: () => ok({ results: [] }) },
  { method: 'POST', pattern: /\/patients\/consultations\//, handler: (body) => ok({ id: Date.now(), statut: 'En cours', ...body }) },

  // Audit
  { method: 'GET', pattern: /\/audit\/$/, handler: () => ok({ results: DB.audit, count: DB.audit.length }) },
  { method: 'GET', pattern: /\/audit\/stats/, handler: () => ok({ total: DB.audit.length, by_module: { Patients: 12, Laboratoire: 8, Soins: 15, Facturation: 6, Auth: 4 } }) },

  // Santé / Health
  { method: 'GET', pattern: /\/sante\/?$/, handler: () => ok({ status: 'ok', database: 'ok (démo)', cache: 'ok', version: '1.0', timestamp: new Date().toISOString(), patients_total: 248, hospitalisations_actives: 3 }) },
  { method: 'GET', pattern: /\/dashboard\/health/, handler: () => ok({ status: 'ok', database: 'ok', cache: 'ok', version: '1.0', patients_total: 248, hospitalisations_actives: 3 }) },

  // FHIR
  { method: 'GET', pattern: /\/interop\/fhir\//, handler: () => ok({ resourceType: 'Bundle', entry: [] }) },
]

function loginHandler(body) {
  // Vérifier dans les comptes enregistrés
  try {
    const accounts = JSON.parse(localStorage.getItem('sghl_accounts') || '[]')
    const acc = accounts.find(a =>
      (a.email === body.username || a.username === body.username) &&
      a.password === body.password && a.confirmed
    )
    if (acc) {
      return ok({
        access: 'mock_token_' + Date.now(),
        user: { username: acc.username, full_name: acc.full_name, role: acc.role, service: acc.service, email: acc.email, telephone: acc.telephone }
      })
    }
  } catch {}

  // Comptes démo pré-définis
  const DEMO = {
    'medecin':    { password: 'medecin123',    role: 'Médecin',    full_name: 'Dr. Camara Alpha',  service: 'Médecine interne', email: 'medecin@sghl.cg' },
    'infirmier':  { password: 'infirmier123',  role: 'Infirmier',  full_name: 'Kouyaté Ibrahima',  service: 'Urgences',         email: 'infirmier@sghl.cg' },
    'biologiste': { password: 'biologiste123', role: 'Biologiste', full_name: 'Dr. Diallo Oumar',  service: 'Laboratoire',      email: 'biologiste@sghl.cg' },
    'pharmacien': { password: 'pharmacien123', role: 'Pharmacien', full_name: 'Sylla Kadiatou',    service: 'Pharmacie',        email: 'pharmacien@sghl.cg' },
    'chirurgien': { password: 'chirurgien123', role: 'Médecin',    full_name: 'Dr. Barry Mamadou', service: 'Chirurgie',        email: 'chirurgien@sghl.cg' },
    'caissier':   { password: 'caissier123',   role: 'Caissier',   full_name: 'Traoré Aminata',    service: 'Facturation',      email: 'caissier@sghl.cg' },
    'admin':      { password: 'admin123',      role: 'Admin',      full_name: 'Traoré Moussa',     service: 'Direction',        email: 'admin@sghl.cg' },
    'patient':    { password: 'patient123',    role: 'Patient',    full_name: 'Compte Patient',   service: '',                 email: 'patient@sghl.cg' },
  }
  const u = body.username?.toLowerCase()
  const d = DEMO[u]
  if (d && d.password === body.password) {
    return ok({ access: 'mock_token_' + Date.now(), user: { username: u, ...d } })
  }
  return Promise.reject({ response: { status: 401, data: { detail: 'Identifiants incorrects' } } })
}

// ── Résolveur principal ───────────────────────────────────────────────────────
export function mockResolve(method, url, body = null, params = null) {
  const path = url.replace(/^\/api\/v1/, '')
  for (const route of MOCK_ROUTES) {
    if (route.method === method.toUpperCase() && route.pattern.test(path)) {
      return route.handler(body, params, path)
    }
  }
  // Fallback générique
  console.warn(`[MOCK] Route non gérée : ${method} ${path}`)
  return ok({ results: [], count: 0, message: 'Mock: route non définie' })
}
