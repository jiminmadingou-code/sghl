import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/',                    component: () => import('@/views/HomeView.vue') },
  { path: '/login/patient',       component: () => import('@/views/LoginPatientView.vue') },
  { path: '/login/professionnel', component: () => import('@/views/LoginProfessionnelView.vue') },
  { path: '/login/admin',         component: () => import('@/views/LoginAdminView.vue') },
  { path: '/login',               redirect: '/login/professionnel' },
  { path: '/register',            component: () => import('@/views/RegisterView.vue') },
  { path: '/mfa',                 component: () => import('@/views/MFAView.vue') },
  {
    path: '/dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '',                 redirect: '/dashboard/accueil' },
      { path: 'accueil',          component: () => import('@/views/DashboardView.vue'),        meta: { title: 'Tableau de bord' } },
      { path: 'patients',         component: () => import('@/views/PatientsView.vue'),         meta: { title: 'Patients' } },
      { path: 'patients/:id',     component: () => import('@/views/PatientDetailView.vue'),    meta: { title: 'Dossier Patient' } },
      { path: 'hospitalisations', component: () => import('@/views/HospitalisationsView.vue'), meta: { title: 'Hospitalisations' } },
      { path: 'consultations',    component: () => import('@/views/ConsultationsView.vue'),    meta: { title: 'Consultations' } },
      { path: 'laboratoire',      component: () => import('@/views/LaboratoireView.vue'),      meta: { title: 'Laboratoire' } },
      { path: 'pharmacie',        component: () => import('@/views/PharmacieView.vue'),        meta: { title: 'Pharmacie' } },
      { path: 'facturation',      component: () => import('@/views/FacturationView.vue'),      meta: { title: 'Facturation' } },
      { path: 'soins',            component: () => import('@/views/SoinsView.vue'),            meta: { title: 'Soins Infirmiers' } },
      { path: 'planning',         component: () => import('@/views/PlanningView.vue'),         meta: { title: 'Planning' } },
      { path: 'personnel',        component: () => import('@/views/PersonnelView.vue'),        meta: { title: 'Personnel' } },
      { path: 'rapports',         component: () => import('@/views/RapportsView.vue'),         meta: { title: 'Rapports' } },
      { path: 'parametres',       component: () => import('@/views/ParametresView.vue'),       meta: { title: 'Paramètres' } },
      { path: 'urgences',         component: () => import('@/views/UrgencesView.vue'),         meta: { title: 'Urgences' } },
      { path: 'imagerie',         component: () => import('@/views/ImagerieView.vue'),         meta: { title: 'Imagerie' } },
      { path: 'bloc-operatoire',  component: () => import('@/views/BlocOperatoireView.vue'),   meta: { title: 'Bloc Opératoire' } },
      { path: 'maternite',        component: () => import('@/views/MaterniiteView.vue'),       meta: { title: 'Maternité' } },
      { path: 'teleconsultation', component: () => import('@/views/TeleconsultationView.vue'), meta: { title: 'Téléconsultation' } },
    ]
  },
  {
    path: '/patient',
    component: () => import('@/layouts/PatientLayout.vue'),
    children: [
      { path: '',                 redirect: '/patient/accueil' },
      { path: 'accueil',          component: () => import('@/views/patient/PatientAccueilView.vue'),          meta: { title: 'Mon espace' } },
      { path: 'rendez-vous',      component: () => import('@/views/patient/PatientRendezVousView.vue'),       meta: { title: 'Rendez-vous' } },
      { path: 'resultats',        component: () => import('@/views/patient/PatientResultatsView.vue'),        meta: { title: 'Résultats' } },
      { path: 'ordonnances',      component: () => import('@/views/patient/PatientOrdonnancesView.vue'),      meta: { title: 'Ordonnances' } },
      { path: 'factures',         component: () => import('@/views/patient/PatientFacturesView.vue'),         meta: { title: 'Factures' } },
      { path: 'messagerie',       component: () => import('@/views/patient/PatientMessagerieView.vue'),       meta: { title: 'Messagerie' } },
      { path: 'hospitalisations', component: () => import('@/views/patient/PatientHospitalisationsView.vue'), meta: { title: 'Hospitalisations' } },
      { path: 'admission',        component: () => import('@/views/patient/PatientAdmissionView.vue'),        meta: { title: 'Admission' } },
      { path: 'imagerie',         component: () => import('@/views/patient/PatientImagerieView.vue'),         meta: { title: 'Imagerie' } },
      { path: 'partage',          component: () => import('@/views/patient/PatientPartageView.vue'),          meta: { title: 'Partage' } },
      { path: 'livret',           component: () => import('@/views/patient/PatientLivretView.vue'),           meta: { title: 'Livret' } },
    ]
  },
  { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFoundView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

// Guard MINIMAL — lit uniquement localStorage, aucune dépendance Pinia
router.beforeEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} — DIGNE HOSPITAL`
  }

  // Chemins toujours accessibles sans connexion
  if (
    to.path === '/' ||
    to.path.startsWith('/login') ||
    to.path === '/register' ||
    to.path === '/mfa'
  ) return true

  // Vérifier le token dans localStorage
  const token = localStorage.getItem('sghl_token')
  if (!token) {
    return to.path.startsWith('/patient') ? '/login/patient' : '/login/professionnel'
  }

  // Lire le rôle
  let isPatient = false
  try {
    const u = JSON.parse(localStorage.getItem('sghl_user') || '{}')
    isPatient = String(u.role || '').toLowerCase() === 'patient'
  } catch { /* ignore */ }

  if (to.path.startsWith('/dashboard') && isPatient) return '/patient/accueil'
  if (to.path.startsWith('/patient') && !isPatient) return '/dashboard/accueil'

  return true
})

export default router
