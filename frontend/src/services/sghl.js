import api from './api'

// ── Patients ──────────────────────────────────────────────────────────────────
export const patientsService = {
  list:   (search = '') => api.get('/patients/', { params: search ? { search } : {} }),
  get:    (id)          => api.get(`/patients/${id}`),
  create: (data)        => api.post('/patients/', data),
  update: (id, data)    => api.put(`/patients/${id}`, data),
  delete: (id)          => api.delete(`/patients/${id}`),
}

// ── Hospitalisations ──────────────────────────────────────────────────────────
export const hospitalisationsService = {
  list:   (statut = '') => api.get('/hospitalisations/', { params: statut ? { statut } : {} }),
  create: (data)        => api.post('/hospitalisations/', data),
  sortie: (id, date)    => api.patch(`/hospitalisations/${id}/sortie`, null, { params: { date_sortie: date } }),
}

// ── Consultations ─────────────────────────────────────────────────────────────
export const consultationsService = {
  list:   (params = {}) => api.get('/patients/consultations/', { params }),
  create: (data)        => api.post('/patients/consultations/', data),
  valider:(id)          => api.patch(`/patients/consultations/${id}/valider`),
}

// ── Laboratoire ───────────────────────────────────────────────────────────────
export const laboService = {
  list:       (params = {}) => api.get('/laboratoire/', { params }),
  avancer:    (id)          => api.patch(`/laboratoire/${id}/avancer`),
  saisirRes:  (id, res)     => api.patch(`/laboratoire/${id}/resultat`, null, { params: { resultat: res } }),
  valider:    (id)          => api.patch(`/laboratoire/${id}/valider`),
  pdf:        (id)          => api.get(`/laboratoire/${id}/pdf`, { responseType: 'blob' }),
}

// ── Pharmacie ─────────────────────────────────────────────────────────────────
export const pharmacieService = {
  inventaire:  ()           => api.get('/pharmacie/inventaire/'),
  alertes:     ()           => api.get('/pharmacie/alertes/'),
  stocks:      (medId)      => api.get('/pharmacie/stocks/', { params: medId ? { medicament_id: medId } : {} }),
  creerLot:    (data)       => api.post('/pharmacie/stocks/', data),
  mouvement:   (data)       => api.post('/pharmacie/mouvements/', data),
  medicaments: (search='')  => api.get('/pharmacie/medicaments/', { params: search ? { search } : {} }),
}

// ── Facturation ───────────────────────────────────────────────────────────────
export const facturationService = {
  list:       (statut = '') => api.get('/facturation/', { params: statut ? { statut } : {} }),
  create:     (data)        => api.post('/facturation/', data),
  paiement:   (id, data)    => api.post(`/facturation/${id}/paiement/`, data),
  pdf:        (id)          => api.get(`/facturation/${id}/pdf`, { responseType: 'blob' }),
}

// ── Personnel ─────────────────────────────────────────────────────────────────
export const personnelService = {
  list:   (role = '') => api.get('/personnel/', { params: role ? { role } : {} }),
  create: (data)      => api.post('/personnel/', data),
  update: (id, data)  => api.patch(`/personnel/${id}`, data),
  stats:  ()          => api.get('/personnel/stats/rh'),
  roles:  ()          => api.get('/personnel/roles/liste'),
}

// ── Rendez-vous ───────────────────────────────────────────────────────────────
export const rdvService = {
  list:      (params = {}) => api.get('/rendez-vous/', { params }),
  create:    (data)        => api.post('/rendez-vous/', data),
  confirmer: (id)          => api.patch(`/rendez-vous/${id}/confirmer`),
  annuler:   (id, motif='')=> api.patch(`/rendez-vous/${id}/annuler`, null, { params: { motif } }),
  terminer:  (id)          => api.patch(`/rendez-vous/${id}/terminer`),
  creneaux:  (medId, date) => api.get(`/rendez-vous/creneaux-libres/${medId}`, { params: { date_rdv: date } }),
}

// ── Soins ─────────────────────────────────────────────────────────────────────
export const soinsService = {
  planning:    (hospitId)       => api.get('/soins/planning/', { params: { hospitalisation_id: hospitId } }),
  constantes:  (hospitId)       => api.get(`/soins/constantes/${hospitId}`),
  trend:       (hospitId, type) => api.get(`/soins/constantes/${hospitId}/trend`, { params: { type_constante: type } }),
  saisirConst: (data)           => api.post('/soins/constantes/', data),
  realiserSoin:(id, notes='')   => api.put(`/soins/planning/${id}/realiser`, null, { params: { notes } }),
  alertes:     ()               => api.get('/soins/constantes/alertes'),
}

// ── Gardes ────────────────────────────────────────────────────────────────────
export const gardesService = {
  planning:      (params = {}) => api.get('/gardes/planning/', { params }),
  creer:         (data)        => api.post('/gardes/planning/', data),
  confirmer:     (id)          => api.put(`/gardes/planning/${id}/confirm`),
  annuler:       (id, motif='')=> api.put(`/gardes/planning/${id}/cancel`, null, { params: { motif } }),
  disponibilites:(params = {}) => api.get('/gardes/disponibilites/', { params }),
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardService = {
  summary:          ()        => api.get('/dashboard/summary'),
  kpiPatients:      (days=30) => api.get('/dashboard/kpi/patients', { params: { days } }),
  kpiHospitalisations:(days=30)=>api.get('/dashboard/kpi/hospitalisations', { params: { days } }),
  kpiLabo:          (days=7)  => api.get('/dashboard/kpi/laboratoire', { params: { days } }),
  kpiFinances:      (days=30) => api.get('/dashboard/kpi/finances', { params: { days } }),
  chartOccupation:  (days=7)  => api.get('/dashboard/charts/occupation', { params: { days } }),
  health:           ()        => api.get('/dashboard/health'),
  // Endpoint /sante/ — health check système complet (DB + Cache + compteurs)
  sante:            ()        => api.get('/sante/'),
}

// ── Audit ─────────────────────────────────────────────────────────────────────
export const auditService = {
  list:  (params = {}) => api.get('/audit/', { params }),
  stats: ()            => api.get('/audit/stats/'),
}

// ── Urgences ──────────────────────────────────────────────────────────────────
export const urgencesService = {
  list:        (statut = '') => api.get('/urgences/', { params: statut ? { statut } : {} }),
  creer:       (data)        => api.post('/urgences/', data),
  get:         (id)          => api.get(`/urgences/${id}`),
  updateStatut:(id, statut)  => api.patch(`/urgences/${id}/statut`, null, { params: { statut } }),
  stats:       ()            => api.get('/urgences/stats/temps-attente'),
}

// ── Imagerie ──────────────────────────────────────────────────────────────────
export const imagerieService = {
  list:          (params = {}) => api.get('/imagerie/', { params }),
  prescrire:     (data)        => api.post('/imagerie/', data),
  compteRendu:   (id, cr, ccl) => api.patch(`/imagerie/${id}/compte-rendu`, null, { params: { compte_rendu: cr, conclusion: ccl } }),
  valider:       (id)          => api.post(`/imagerie/${id}/valider`),
}

// ── Bloc opératoire ───────────────────────────────────────────────────────────
export const blocService = {
  list:        (statut = '') => api.get('/bloc-operatoire/', { params: statut ? { statut } : {} }),
  programmer:  (data)        => api.post('/bloc-operatoire/', data),
  demarrer:    (id)          => api.post(`/bloc-operatoire/${id}/demarrer`),
  terminer:    (id, cr='', compl='') => api.post(`/bloc-operatoire/${id}/terminer`, null, { params: { compte_rendu: cr, complications: compl } }),
  planning:    (salleId, date) => api.get(`/bloc-operatoire/planning-salle/${salleId}`, { params: { date } }),
}

// ── Maternité ─────────────────────────────────────────────────────────────────
export const materniteService = {
  list:   (statut = '') => api.get('/maternite/', { params: statut ? { statut } : {} }),
  creer:  (data)        => api.post('/maternite/', data),
  get:    (id)          => api.get(`/maternite/${id}`),
  stats:  ()            => api.get('/maternite/stats/maternite'),
}

// ── Téléconsultation ──────────────────────────────────────────────────────────
export const teleconsultService = {
  list:     (statut = '') => api.get('/teleconsultation/', { params: statut ? { statut } : {} }),
  creer:    (data)        => api.post('/teleconsultation/', data),
  demarrer: (id)          => api.post(`/teleconsultation/${id}/demarrer`),
  terminer: (id, notes='', diag='') => api.post(`/teleconsultation/${id}/terminer`, null, { params: { notes, diagnostic: diag } }),
}

// ── Prescriptions ─────────────────────────────────────────────────────────────
export const prescriptionsService = {
  list:     (params = {}) => api.get('/prescriptions/', { params }),
  create:   (data)        => api.post('/prescriptions/', data),
  valider:  (id)          => api.patch(`/prescriptions/${id}/valider`),
  dispenser:(prescId, ligneId) => api.patch(`/prescriptions/${prescId}/dispenser/${ligneId}`),
  pdf:      (id)          => api.get(`/prescriptions/${id}/pdf`, { responseType: 'blob' }),
}

// ── FHIR ──────────────────────────────────────────────────────────────────────
export const fhirService = {
  patient:     (id)          => api.get(`/interop/fhir/Patient/${id}`),
  observations:(patientId)   => api.get('/interop/fhir/Observation', { params: { patient_id: patientId } }),
  encounters:  (patientId)   => api.get('/interop/fhir/Encounter', { params: { patient_id: patientId } }),
  metadata:    ()            => api.get('/interop/fhir/metadata'),
}

// ── Utilitaire : télécharger un blob PDF ──────────────────────────────────────
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href    = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
