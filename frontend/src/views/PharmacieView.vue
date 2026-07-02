<script setup>
import { ref, computed, reactive } from 'vue'

const search = ref('')
const showModal = ref(false)

const newEntree = reactive({ medicamentId: '', quantite: '', lot: '', peremption: '' })

function ajouterEntree() {
  if (!newEntree.medicamentId || !newEntree.quantite) return
  const med = medicaments.value.find(m => m.id === Number(newEntree.medicamentId))
  if (med) {
    med.stock += Number(newEntree.quantite)
    if (newEntree.lot) med.lot = newEntree.lot
    if (newEntree.peremption) med.peremption = newEntree.peremption
    med.statut = med.stock >= med.seuil ? 'Normal' : med.stock > 0 ? 'Alerte' : 'Rupture'
  }
  Object.assign(newEntree, { medicamentId: '', quantite: '', lot: '', peremption: '' })
  showModal.value = false
}

const medicaments = ref([
  { id: 1, nom: 'Artémether 80mg', categorie: 'Antipaludéen', stock: 245, seuil: 50, lot: 'LOT-2025-001', peremption: '2026-08-01', statut: 'Normal' },
  { id: 2, nom: 'Amlodipine 5mg', categorie: 'Antihypertenseur', stock: 32, seuil: 50, lot: 'LOT-2025-002', peremption: '2026-03-15', statut: 'Alerte' },
  { id: 3, nom: 'Metformine 500mg', categorie: 'Antidiabétique', stock: 180, seuil: 40, lot: 'LOT-2025-003', peremption: '2027-01-20', statut: 'Normal' },
  { id: 4, nom: 'Amoxicilline 500mg', categorie: 'Antibiotique', stock: 8, seuil: 30, lot: 'LOT-2025-004', peremption: '2025-12-10', statut: 'Rupture' },
  { id: 5, nom: 'Paracétamol 500mg', categorie: 'Analgésique', stock: 520, seuil: 100, lot: 'LOT-2025-005', peremption: '2026-11-30', statut: 'Normal' },
  { id: 6, nom: 'Ibuprofène 400mg', categorie: 'Anti-inflammatoire', stock: 67, seuil: 60, lot: 'LOT-2025-006', peremption: '2026-06-01', statut: 'Normal' },
])

const filtered = computed(() =>
  medicaments.value.filter(m => m.nom.toLowerCase().includes(search.value.toLowerCase()))
)

const alertes = computed(() => medicaments.value.filter(m => m.statut !== 'Normal'))

const statutColor = { 'Normal': 'badge-success', 'Alerte': 'badge-warning', 'Rupture': 'badge-danger' }

function stockPercent(m) {
  return Math.min(100, Math.round((m.stock / (m.seuil * 5)) * 100))
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Pharmacie</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des stocks et médicaments</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Entrée de stock</button>
    </div>

    <!-- Alertes -->
    <div v-if="alertes.length" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
      <p class="text-sm font-semibold text-amber-800 mb-2">⚠ Alertes stock ({{ alertes.length }})</p>
      <div class="flex flex-wrap gap-2">
        <span v-for="a in alertes" :key="a.id" :class="['text-xs font-medium px-3 py-1 rounded-full', statutColor[a.statut]]">
          {{ a.nom }} — {{ a.stock }} unités
        </span>
      </div>
    </div>

    <div class="stat-card p-4">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍  Rechercher un médicament..." />
    </div>

    <div class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Médicament</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Catégorie</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Stock</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Niveau</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">N° Lot</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Péremption</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in filtered" :key="m.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ m.nom }}</td>
              <td class="px-4 py-3 text-gray-500">{{ m.categorie }}</td>
              <td class="px-4 py-3 font-bold text-gray-900">{{ m.stock }} <span class="text-xs text-gray-400 font-normal">/ seuil {{ m.seuil }}</span></td>
              <td class="px-4 py-3 w-32">
                <div class="w-full bg-gray-100 rounded-full h-2">
                  <div
                    :class="['h-2 rounded-full', m.statut === 'Normal' ? 'bg-green-500' : m.statut === 'Alerte' ? 'bg-amber-500' : 'bg-red-500']"
                    :style="{ width: stockPercent(m) + '%' }"
                  ></div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ m.lot }}</td>
              <td class="px-4 py-3 text-gray-500">{{ m.peremption }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[m.statut]]">{{ m.statut }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-4">📦 Entrée de stock</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Médicament *</label>
            <select v-model="newEntree.medicamentId" class="input-field">
              <option value="">Sélectionner</option>
              <option v-for="m in medicaments" :key="m.id" :value="m.id">{{ m.nom }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Quantité reçue *</label>
              <input v-model="newEntree.quantite" type="number" class="input-field" placeholder="100" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">N° Lot</label>
              <input v-model="newEntree.lot" class="input-field" placeholder="LOT-2025-XXX" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Date de péremption</label>
            <input v-model="newEntree.peremption" type="date" class="input-field" />
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterEntree" class="btn-primary flex-1">✅ Enregistrer</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
