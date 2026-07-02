// Store centralisé des comptes utilisateurs — persist dans localStorage
import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'sghl_accounts'

function loadAccounts() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
}
function saveAccounts(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

// Simulation envoi email/SMS (console + alert visible)
function simulateEmailNotification(email, nom, type, extra = '') {
  const subject = type === 'register'
    ? `✅ Bienvenue sur DIGNE HOSPITAL — Confirmez votre compte`
    : `🔐 Connexion détectée sur votre compte DIGNE HOSPITAL`
  const body = type === 'register'
    ? `Bonjour ${nom},\n\nVotre compte a été créé avec succès sur DIGNE HOSPITAL.\n\nCliquez sur le lien ci-dessous pour confirmer votre email :\nhttps://digne-hospital.gn/confirm?token=DEMO_TOKEN_${Date.now()}\n\nCe lien expire dans 24 heures.\n\nCordialement,\nL'équipe DIGNE HOSPITAL`
    : `Bonjour ${nom},\n\nUne connexion a été détectée sur votre compte.\n\nDate : ${new Date().toLocaleString('fr-FR')}\nAppareil : Navigateur Web\n${extra}\n\nSi ce n'était pas vous, changez votre mot de passe immédiatement.\n\nCordialement,\nL'équipe DIGNE HOSPITAL`
  
  console.log(`📧 EMAIL SIMULÉ → ${email}\nObjet: ${subject}\n\n${body}`)
  return { subject, body, email }
}

function simulateSMSNotification(phone, nom, type) {
  if (!phone) return
  const msg = type === 'register'
    ? `DIGNE HOSPITAL: Compte créé pour ${nom}. Vérifiez votre email pour activer votre compte.`
    : `DIGNE HOSPITAL: Connexion détectée sur votre compte le ${new Date().toLocaleTimeString('fr-FR')}. Si ce n'est pas vous, contactez le +224 620 000 000.`
  console.log(`📱 SMS SIMULÉ → ${phone}: ${msg}`)
  return msg
}

export const useAccountsStore = defineStore('accounts', () => {
  const accounts = ref(loadAccounts())
  const lastNotification = ref(null)

  function register(userData) {
    // Vérifier doublon email
    if (accounts.value.find(a => a.email === userData.email)) {
      throw new Error('Un compte avec cet email existe déjà.')
    }
    // Vérifier doublon username
    const username = (userData.username || `${userData.prenom}.${userData.nom}`).toLowerCase().replace(/\s/g, '.')
    if (accounts.value.find(a => a.username === username)) {
      throw new Error('Cet identifiant est déjà utilisé.')
    }

    const newAccount = {
      id: Date.now(),
      username,
      password: userData.password,
      email: userData.email,
      telephone: userData.telephone || '',
      prenom: userData.prenom,
      nom: userData.nom,
      full_name: `${userData.prenom} ${userData.nom}`,
      role: userData.role || 'Patient',
      service: userData.service || '',
      matricule: userData.matricule || '',
      confirmed: false, // nécessite confirmation email
      created_at: new Date().toISOString(),
    }

    accounts.value.push(newAccount)
    saveAccounts(accounts.value)

    // Simuler envoi email + SMS
    const notif = simulateEmailNotification(newAccount.email, newAccount.full_name, 'register')
    simulateSMSNotification(newAccount.telephone, newAccount.full_name, 'register')
    lastNotification.value = { type: 'register', email: newAccount.email, username, ...notif }

    return newAccount
  }

  function login(username, password) {
    const id = username.toLowerCase().trim()
    const acc = accounts.value.find(a => a.username === id || a.email === id)
    if (!acc) return null
    if (acc.password !== password) return null

    // Confirmer le compte au 1er login (mode démo)
    acc.confirmed = true
    saveAccounts(accounts.value)

    // Simuler email + SMS de connexion
    const notif = simulateEmailNotification(acc.email, acc.full_name, 'login', `Identifiant : ${acc.username}`)
    simulateSMSNotification(acc.telephone, acc.full_name, 'login')
    lastNotification.value = { type: 'login', email: acc.email, ...notif }

    return acc
  }

  function confirmAccount(username) {
    const acc = accounts.value.find(a => a.username === username)
    if (acc) { acc.confirmed = true; saveAccounts(accounts.value) }
  }

  function getByUsername(username) {
    return accounts.value.find(a => a.username === username.toLowerCase())
  }

  return { accounts, lastNotification, register, login, confirmAccount, getByUsername }
})
