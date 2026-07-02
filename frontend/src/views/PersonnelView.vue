<script setup>
import { ref, computed, onMounted } from 'vue'
import { personnelService } from '@/services/sghl'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const search = ref('')
const showModal = ref(false)
const loading = ref(true)
const saving = ref(false)
const filterRole = ref('')

const personnel = ref([])
const stats = ref({ total_actifs: 0, total_inactifs: 0, par_role: [], mfa_actif: 0 })
const roles = ref([])

const form = ref({ username: '', email: '', first_name: '', last_name: '', role: 'Médecin', service: '', telephone: '', password: '' })

const DEMO = [
  { id: 1, full_name: 'Camara Alpha',    role: 'Médecin',       service: 'Médecine interne', email: 'a.camara@sghl.gn',    actif: true, mfa_active: true,  last_login_at: '2025-06-12T08:30:00' },
  { id: 2, full_name: 'Bah Mariama',     role: 'Médecin',       service: 'Cardiologie',      email: 'm.bah@sghl.gn',       actif: true, mfa_active: true,  last_login_at: '2025-06-12T09:00:00' },
  { id: 3, full_name: 'Diallo Oumar',    role: 'Biologiste',    service: 'Laboratoire',      email: 'o.diallo@sghl.gn',    actif: true, mfa_active: false, last_login_at: '2025-06-11T14:00:00' },
  { id: 4, full_name: 'Kouyaté Ibrahima',role: 'Infirmier',     service: 'Urgences',         email: 'i.kouyate@sghl.gn',   actif: true, mfa_active: false, last_login_at: '2025-06-12T07:00:00' },
  { id: 5, full_name: 'Sylla Kadiatou',  role: 'Pharmacien',    service: 'Pharmacie',        email: 'k.sylla@sghl.gn',     actif: true, mfa_active: false, last_login_at: '2025-06-11T10:00:00' },
  { id: 6, full_name: 'Traoré Moussa',   role: 'Admin',         service: 'Direction',        email: 'm.traore@sghl.gn',    actif: true, mfa_active: true,  last_login_at: '2025-06-12T08:00:00' },
]

onMounted(async () => {
  await Promise.all([loadPersonnel(), loadStats(), loadRoles()])
})

async function loadPersonnel() {
  loading.value = true
  try {
    const { data } = await personnelService.list(filterRole.value)
    personnel.value = Array.isArray(data) ? data : (data.results || DEMO)
  } catch { personnel.value = DEMO }
  finally { loading.value = false }
}

async function loadStats() {
  try {
    const { data } = await personnelService.stats()
    stats.value = data
  } catch {
    stats.value = { total_actifs: DEMO.length, total_inactifs: 0, par_role: [], mfa_actif: 2 }
  }
}

async function loadRoles() {
  try {
    const { data } = await personnelService.roles()
    roles.value = data
  } catch {
    roles.value = [
      { code: 'Médecin', label: 'Médecin' }, { code: 'Infirmier', label: 'Infirmier' },
      { code: 'Biologiste', label: 'Biologiste' }, { code: 'Pharmacien', label: 'Pharmacien' },
      { code: 'Admin', label: 'Administrateur' }, { code: 'Caissier', label: 'Caissier' },
    ]
  }
}

const filtered = computed(() =>
  personnel.value.filter(p =>
    p.full_name?.toLowerCase().includes(search.value.toLowerCase()) &&
    (!filterRole.value || p.role === filterRole.value)
  )
)

async function savePersonnel() {
  saving.value = true
  try {
    const { data } = await personnelService.create(form.value)
    personnel.value.unshift(data)
    toast.success('Membre du personnel créé avec succès')
    showModal.value = false
    resetForm()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Erreur lors de la création')
  } finally { saving.value = false }
}

function resetForm() {
  form.value = { username: '', email: '', first_name: '', last_name: '', role: 'Médecin', service: '', telephone: '', password: '' }
}

const roleColor = { 'Médecin': 'badge-violet', 'Biologiste': 'badge-info', 'Infirmier': 'badge-success', 'Pharmacien': 'badge-warning', 'Admin': 'badge-danger', 'Caissier': 'badge-teal', 'Receptionniste': 'badge-orange' }

const roleStats = computed(() => {
  const counts = {}
  personnel.value.forEach(p => { counts[p.role] = (counts[p.role] || 0) + 1 })
  return Object.entries(counts).map(([role, count]) => ({ role, count }))
})
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Personnel</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des utilisateurs et accès (RBAC)</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Ajouter membre</button>
    </div>

    <!-- Stats par rôle -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div v-for="s in roleStats" :key="s.role" class="stat-card p-4 text-center card-hover">
        <p class="text-2xl font-bold text-violet-700">{{ s.count }}</p>
        <p class="text-xs text-gray-500 mt-0.5">{{ s.role }}</p>
      </div>
    </div>

    <!-- MFA info -->
    <div class="alert-info-banner flex items-center gap-3">
      <span class="text-blue-600 text-lg">🔐</span>
      <p class="text-sm text-blue-800">
        <strong>{{ stats.mfa_actif }}</strong> membre(s) avec MFA activé sur <strong>{{ stats.total_actifs }}</strong> actifs.
        <RouterLink to="/dashboard/parametres" class="ml-2 underline font-semibold">Configurer la politique MFA →</RouterLink>
      </p>
    </div>

    <!-- Filtres -->
    <div class="stat-card p-4 flex flex-col sm:flex-row gap-3">
      <input v-model="search" class="input-field sm:max-w-xs" placeholder="🔍  Rechercher..." />
      <select v-model="filterRole" @change="loadPersonnel" class="input-field sm:max-w-[180px]">
        <option value="">Tous les rôles</option>
        <option v-for="r in roles" :key="r.code" :value="r.code">{{ r.label }}</option>
      </select>
      <button @click="loadPersonnel" class="btn-secondary">↻ Actualiser</button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Membre</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Rôle</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Service</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Email</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">MFA</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Dernière connexion</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 font-bold text-xs">
                    {{ p.full_name?.split(' ').map(n => n[0]).join('').slice(0,2) }}
                  </div>
                  <span class="font-medium text-gray-900">{{ p.full_name }}</span>
                </div>
              </td>
              <td class="px-4 py-3"><span :class="['text-xs font-medium px-2.5 py-1 rounded-full', roleColor[p.role] || 'badge-info']">{{ p.role }}</span></td>
              <td class="px-4 py-3 text-gray-600">{{ p.service }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ p.email }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', p.mfa_active ? 'badge-success' : 'badge-warning']">
                  {{ p.mfa_active ? '✓ Actif' : '✗ Inactif' }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">
                {{ p.last_login_at ? new Date(p.last_login_at).toLocaleDateString('fr-FR') : '—' }}
              </td>
              <td class="px-4 py-3"><span :class="['text-xs font-medium px-2.5 py-1 rounded-full', p.actif ? 'badge-success' : 'badge-danger']">{{ p.actif ? 'Actif' : 'Inactif' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal création -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Nouveau membre du personnel</h3>
          <form @submit.prevent="savePersonnel" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Prénom *</label><input v-model="form.first_name" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Nom *</label><input v-model="form.last_name" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Identifiant *</label><input v-model="form.username" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Email *</label><input v-model="form.email" type="email" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Rôle *</label>
                <select v-model="form.role" class="input-field">
                  <option v-for="r in roles" :key="r.code" :value="r.code">{{ r.label }}</option>
                </select>
              </div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Service</label><input v-model="form.service" class="input-field" /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Téléphone</label><input v-model="form.telephone" class="input-field" /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Mot de passe *</label><input v-model="form.password" type="password" class="input-field" required /></div>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1" :disabled="saving">
                <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block mr-2"></span>
                Créer le compte
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
