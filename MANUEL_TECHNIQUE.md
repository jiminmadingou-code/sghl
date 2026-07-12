# MANUEL TECHNIQUE
# Système de Gestion Hospitalière et de Laboratoire
# **SGHL — CHU DIGNE HOSPITAL**

---

**Projet** : ERP Médical Full-Stack  
**Équipe** : NLP-Core-Team  
**Année** : 2024–2025  
**Hébergement** : Railway (Backend + Frontend + Base de données)  
**Distribution mobile** : Sideloading APK via site web dédié

---

## TABLE DES MATIÈRES

1. [Vue d'ensemble du projet](#1-vue-densemble)
2. [Architecture globale](#2-architecture-globale)
3. [Backend — Django REST API](#3-backend)
4. [Frontend — Vue.js 3](#4-frontend)
5. [Application Mobile — Flutter](#5-mobile)
6. [Base de données — PostgreSQL](#6-base-de-données)
7. [Sécurité](#7-sécurité)
8. [Déploiement Railway](#8-déploiement)
9. [Distribution Mobile (Sideloading)](#9-sideloading)
10. [Guide d'utilisation](#10-guide-dutilisation)

---

## 1. VUE D'ENSEMBLE

Le SGHL est un **ERP médical complet** qui digitalise l'intégralité du parcours patient dans un établissement hospitalier, de l'admission jusqu'au suivi post-hospitalisation.

### Trois composantes principales

| Composante | Technologie | URL de production |
|---|---|---|
| **Backend API** | Python / Django | `https://sghl-production.up.railway.app` |
| **Frontend Web** | Vue.js 3 | Hébergé sur Railway |
| **Application Mobile** | Flutter (Android) | Téléchargement APK via site dédié |

### Utilisateurs cibles

| Profil | Interface | Accès |
|---|---|---|
| **Médecin / Infirmier** | Frontend Web | `/dashboard` |
| **Administrateur** | Frontend Web + Admin Django | `/admin` |
| **Patient** | Frontend Web + Application Mobile | `/patient` ou APK |

---

## 2. ARCHITECTURE GLOBALE

```
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY (Cloud)                          │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  Frontend    │   │   Backend    │   │  Download Site │  │
│  │  Vue.js 3    │   │   Django     │   │  Node.js/APK   │  │
│  │  Port 5173   │◄──►  Port 8000  │   │  Port 3000     │  │
│  └──────────────┘   └──────┬───────┘   └────────────────┘  │
│                            │                                │
│              ┌─────────────┼──────────────┐                 │
│              │             │              │                 │
│  ┌───────────▼──┐  ┌───────▼──────┐       │                 │
│  │  PostgreSQL  │  │    Redis     │       │                 │
│  │  Port 5432   │  │  Port 6379   │       │                 │
│  └──────────────┘  └──────────────┘       │                 │
└─────────────────────────────────────────────────────────────┘
                                            │
                              ┌─────────────▼──────────────┐
                              │   Application Mobile        │
                              │   Flutter — Android APK     │
                              │   Connexion via HTTPS API   │
                              └────────────────────────────┘
```

### Flux de communication

- Le **Frontend** et le **Mobile** communiquent avec le **Backend** via des requêtes HTTP/HTTPS avec authentification JWT.
- Le **Backend** lit et écrit dans **PostgreSQL** (données persistantes) et **Redis** (cache, sessions temps réel).
- Le **Chat temps réel** utilise **WebSockets** via Django Channels + Redis.

---

## 3. BACKEND — DJANGO REST API

### 3.1 Stack technique

| Élément | Technologie | Rôle |
|---|---|---|
| Langage | Python 3.11 | Langage principal |
| Framework | Django 4.2 | ORM, Admin, Auth |
| API REST | Django Ninja | Routes typées Pydantic |
| Auth | JWT (SimpleJWT) | Tokens stateless |
| WebSocket | Django Channels | Chat temps réel |
| Cache | Redis / LocMemCache | Performance |
| Serveur | Gunicorn | Production WSGI |
| Fichiers statiques | WhiteNoise | Servir CSS/JS sans Nginx |

### 3.2 Modules applicatifs (21 modules)

Chaque module est une application Django indépendante avec ses propres modèles, API et migrations.

| Module | Endpoint API | Fonctionnalité |
|---|---|---|
| `patients` | `/api/v1/patients/` | Dossiers patients, antécédents |
| `hospitalisations` | `/api/v1/hospitalisations/` | Admissions, lits, transferts |
| `laboratoire` | `/api/v1/laboratoire/` | Analyses, résultats, validation |
| `pharmacie` | `/api/v1/pharmacie/` | Stocks, médicaments, alertes |
| `facturation` | `/api/v1/facturation/` | Factures, paiements, tiers-payant |
| `personnel` | `/api/v1/personnel/` | RH, médecins, infirmiers |
| `soins` | `/api/v1/soins/` | Constantes vitales, soins infirmiers |
| `dashboard` | `/api/v1/dashboard/` | KPIs, statistiques temps réel |
| `chat` | `/api/v1/chat/` | Messagerie médecin-patient |
| `gardes` | `/api/v1/gardes/` | Planning de garde |
| `rendez_vous` | `/api/v1/rendez-vous/` | Prise de RDV |
| `prescriptions` | `/api/v1/prescriptions/` | Ordonnances, PDF signés |
| `urgences` | `/api/v1/urgences/` | Triage, prise en charge urgente |
| `imagerie` | `/api/v1/imagerie/` | Radiologie, IRM, scanner |
| `bloc_operatoire` | `/api/v1/bloc-operatoire/` | Planification chirurgicale |
| `maternite` | `/api/v1/maternite/` | Suivi grossesse, accouchements |
| `teleconsultation` | `/api/v1/teleconsultation/` | Consultations à distance |
| `audit` | `/api/v1/audit/` | Journal immuable des actions |
| `consentement` | `/api/v1/consentement/` | Consentements éclairés |
| `archivage` | `/api/v1/archivage/` | Archivage sécurisé des dossiers |
| `interoperabilite` | `/api/v1/interop/` | Standard HL7/FHIR |

### 3.3 Authentification JWT

Le système utilise deux types de tokens :

```
POST /api/v1/auth/login/
→ Retourne : { access: "...", refresh: "..." }

POST /api/v1/auth/refresh/
→ Renouvelle le token d'accès

POST /api/v1/auth/register/
→ Inscription patient (crée User Django + dossier Patient)
```

**Durée de vie des tokens :**
- Access Token : **60 minutes**
- Refresh Token : **7 jours** (rotation automatique)

### 3.4 Endpoints spéciaux

```
GET  /                    → Informations API (version, liens)
GET  /api/v1/sante/       → Health check (DB, Cache, compteurs)
GET  /api/v1/docs/        → Documentation interactive Swagger
GET  /admin/              → Interface d'administration Django
```

### 3.5 Middleware de sécurité (chaîne d'exécution)

```
Requête entrante
      │
      ▼
CorsMiddleware          → Autorise les requêtes cross-origin (mobile, web)
      │
      ▼
SecurityHeadersMiddleware → Ajoute X-Frame-Options, X-Content-Type
      │
      ▼
RateLimitMiddleware     → Limite le nombre de requêtes par IP
      │
      ▼
InputSanitizationMiddleware → Nettoie les entrées (XSS, injection)
      │
      ▼
AuthenticationMiddleware → Vérifie le JWT
      │
      ▼
RBACMiddleware          → Contrôle d'accès par rôle
      │
      ▼
Vue / API Handler
```

### 3.6 Configuration base de données (multi-environnement)

```python
# Priorité de connexion :
# 1. DATABASE_PUBLIC_URL (Railway externe)
# 2. DATABASE_URL (Railway interne)
# 3. Variables DB_* individuelles
# 4. SQLite (développement local)
```

### 3.7 Logging structuré JSON

Trois fichiers de logs rotatifs (compatibles ELK Stack) :

| Fichier | Contenu | Rétention |
|---|---|---|
| `sghl.json.log` | Logs applicatifs généraux | 10 fichiers × 50 MB |
| `security.json.log` | Tentatives d'intrusion, rate limit | 30 fichiers × 20 MB |
| `audit.json.log` | Toutes les actions utilisateurs | 90 fichiers × 100 MB |

---

## 4. FRONTEND — VUE.JS 3

### 4.1 Stack technique

| Élément | Version | Rôle |
|---|---|---|
| Vue.js | 3.5 | Framework réactif (Composition API) |
| Vue Router | 4.6 | Navigation SPA |
| Pinia | 3.0 | Gestion d'état global |
| Axios | 1.16 | Requêtes HTTP vers l'API |
| Tailwind CSS | 4.3 | Styles utilitaires |
| Vite | 8.0 | Bundler ultra-rapide |
| Heroicons | 2.2 | Bibliothèque d'icônes |

### 4.2 Structure des routes

Le frontend propose **deux espaces distincts** selon le rôle de l'utilisateur :

#### Espace Professionnel (`/dashboard`)
Accessible aux médecins, infirmiers et administrateurs.

| Route | Vue | Description |
|---|---|---|
| `/dashboard/accueil` | DashboardView | KPIs, statistiques temps réel |
| `/dashboard/patients` | PatientsView | Liste et recherche patients |
| `/dashboard/patients/:id` | PatientDetailView | Dossier complet d'un patient |
| `/dashboard/hospitalisations` | HospitalisationsView | Gestion des lits et admissions |
| `/dashboard/consultations` | ConsultationsView | Consultations médicales |
| `/dashboard/laboratoire` | LaboratoireView | Workflow analyses labo |
| `/dashboard/pharmacie` | PharmacieView | Gestion des stocks |
| `/dashboard/facturation` | FacturationView | Factures et paiements |
| `/dashboard/soins` | SoinsView | Soins infirmiers, constantes |
| `/dashboard/planning` | PlanningView | Plannings et gardes |
| `/dashboard/personnel` | PersonnelView | Gestion RH |
| `/dashboard/urgences` | UrgencesView | Triage urgences |
| `/dashboard/imagerie` | ImagerieView | Radiologie |
| `/dashboard/bloc-operatoire` | BlocOperatoireView | Chirurgie |
| `/dashboard/maternite` | MaterniiteView | Maternité |
| `/dashboard/teleconsultation` | TeleconsultationView | Télémédecine |

#### Espace Patient (`/patient`)
Interface simplifiée pour les patients connectés.

| Route | Vue | Description |
|---|---|---|
| `/patient/accueil` | PatientAccueilView | Tableau de bord personnel |
| `/patient/rendez-vous` | PatientRendezVousView | Mes rendez-vous |
| `/patient/resultats` | PatientResultatsView | Mes résultats d'analyses |
| `/patient/ordonnances` | PatientOrdonnancesView | Mes ordonnances PDF |
| `/patient/factures` | PatientFacturesView | Mes factures |
| `/patient/messagerie` | PatientMessagerieView | Chat avec médecin |
| `/patient/hospitalisations` | PatientHospitalisationsView | Mes hospitalisations |
| `/patient/imagerie` | PatientImagerieView | Mes examens d'imagerie |

### 4.3 Système d'authentification frontend

```
Connexion → Token JWT stocké dans localStorage (clé: sghl_token)
Profil    → Données utilisateur dans localStorage (clé: sghl_user)

Guard de navigation (router.beforeEach) :
  - Vérifie la présence du token
  - Lit le rôle (patient / professionnel)
  - Redirige vers le bon espace selon le rôle
  - Redirige vers /login si non authentifié
```

### 4.4 Trois pages de connexion distinctes

| Page | Route | Pour qui |
|---|---|---|
| Connexion Professionnel | `/login/professionnel` | Médecins, infirmiers |
| Connexion Patient | `/login/patient` | Patients |
| Connexion Admin | `/login/admin` | Administrateurs (avec code email MFA) |

---

## 5. APPLICATION MOBILE — FLUTTER

### 5.1 Stack technique

| Élément | Version | Rôle |
|---|---|---|
| Flutter | 3.x | Framework cross-platform |
| Dart | 3.x | Langage |
| go_router | 13.x | Navigation déclarative |
| flutter_riverpod | 2.x | Gestion d'état |
| flutter_secure_storage | 10.x | Stockage sécurisé JWT |
| dio | 5.x | Client HTTP |
| google_fonts | 6.x | Police Inter |
| fl_chart | 0.66 | Graphiques (constantes vitales) |

### 5.2 Architecture de navigation

```
/splash     → Vérification token → /home ou /login
/login      → Authentification JWT
/register   → Inscription nouveau patient

ShellRoute (Bottom Navigation Bar)
├── /home           → Accueil (stats, RDV, rappels médicaments)
├── /appointments   → Rendez-vous
├── /results        → Résultats laboratoire
├── /prescriptions  → Ordonnances
├── /chat           → Messagerie médecin
├── /vitals         → Constantes vitales
├── /invoices       → Factures
└── /profile        → Profil patient
```

### 5.3 Design System — Violet Premium

Toute l'application utilise un design sombre cohérent :

| Élément | Couleur HEX | Usage |
|---|---|---|
| Background | `#0F0C29` | Fond principal |
| Cards | `#1A1740` | Cartes, conteneurs |
| Accent principal | `#6366F1` | Boutons, gradient |
| Violet clair | `#818CF8` | Icônes, textes secondaires |
| Vert | `#34D399` | Succès, statut normal |
| Rouge | `#F87171` | Alertes, erreurs |
| Jaune | `#FBBF24` | Avertissements |

### 5.4 Écrans détaillés

#### Accueil (`home_screen.dart`)
- Header avec avatar initiale + badge "En ligne"
- Barre de stats 4 colonnes (RDV, Résultats, Ordonnances, Messages)
- Carte prochain RDV avec gradient violet
- Accès rapides 6 modules avec emojis et fonds colorés
- Rappels médicamenteux interactifs (cases à cocher)
- Timeline d'activité récente
- Score de santé circulaire avec indicateurs TA/IMC/Glycémie

#### Rendez-vous (`appointments_screen.dart`)
- Liste des RDV avec countdown en jours
- Avatar initiales du médecin (cast Dart explicite pour Flutter Web)
- Salle et horaire affichés
- Bottom sheet de prise de RDV avec sélection médecin/spécialité

#### Résultats (`results_screen.dart`)
- Filtres pills : Tous / Disponibles / Urgents
- Cartes expandables avec valeurs détaillées
- Indicateurs ✅ normal / ⚠️ hors norme par valeur

#### Ordonnances (`prescriptions_screen.dart`)
- Cartes accordéon par ordonnance
- Cases à cocher "pris aujourd'hui" interactives
- Dialog de prévisualisation PDF avec contenu réel (médicaments + posologie)
- Bouton téléchargement avec confirmation

#### Messagerie (`chat_screen.dart`)
- Liste des conversations avec badge non lus
- Indicateur "En ligne" par médecin
- **Bouton "Répondre" inline** sur chaque conversation (sans ouvrir le chat complet)
- Écran de chat complet avec :
  - Bulles gradient violet (messages envoyés)
  - Indicateur lu/envoyé (✓ / ✓✓)
  - Typing indicator animé 3 points
  - Réponse automatique simulée (démo)

#### Constantes vitales (`vitals_screen.dart`)
- 6 cartes avec icônes dédiées par constante :
  - ❤️ Tension artérielle (mmHg)
  - 💓 Fréquence cardiaque (bpm)
  - 🌡️ Température (°C)
  - 💨 SpO₂ (%)
  - 💧 Glycémie (g/L)
  - ⚖️ Poids (kg)
- Valeur en couleur accent + norme de référence
- Indicateur tendance avec flèche (↑↓→)
- 3 graphiques de tendance 7 jours sélectionnables (Tension / Glycémie / FC)
- Bilan de santé synthétique

#### Profil (`profile_screen.dart`)
- SliverAppBar avec grand avatar gradient
- ID patient PAT-XXXX
- Chips info (âge, sexe, groupe sanguin)
- Timeline médicale avec points colorés
- Bouton déconnexion rouge

### 5.5 Stockage sécurisé

```dart
// JWT stocké via flutter_secure_storage (chiffré sur l'appareil)
await secureStorage.write(key: 'access_token', value: token);
await secureStorage.write(key: 'user_data', value: jsonEncode(user));

// Lecture au démarrage (SplashScreen)
final token = await secureStorage.read(key: 'access_token');
```

### 5.6 Communication avec l'API

```dart
// URL de base (api_service.dart)
const baseUrl = 'https://sghl-production.up.railway.app/api/v1';

// Toutes les requêtes incluent le header Authorization
headers: { 'Authorization': 'Bearer $token' }
```

---

## 6. BASE DE DONNÉES — POSTGRESQL

### 6.1 Configuration Railway

- **Moteur** : PostgreSQL 15
- **Hébergement** : Railway (service dédié)
- **Connexion** : Via `DATABASE_PUBLIC_URL` (URL complète avec credentials)
- **SSL** : Désactivé côté Django (Railway gère SSL en amont)
- **Pool de connexions** : `conn_max_age=600` (10 minutes)

### 6.2 Principales tables (par module)

| Module | Tables principales |
|---|---|
| patients | `patients_patient`, `patients_antecedent` |
| hospitalisations | `hospitalisations_hospitalisation`, `hospitalisations_lit`, `hospitalisations_chambre` |
| laboratoire | `laboratoire_analyse`, `laboratoire_resultat`, `laboratoire_validation` |
| pharmacie | `pharmacie_medicament`, `pharmacie_stock`, `pharmacie_mouvement` |
| facturation | `facturation_facture`, `facturation_paiement`, `facturation_ligne` |
| audit | `audit_journal` (immuable — pas de DELETE/UPDATE) |
| chat | `chat_conversation`, `chat_message` |

### 6.3 Migrations

```bash
# Exécutées automatiquement au démarrage (Procfile Railway)
python manage.py migrate --noinput --run-syncdb
```

---

## 7. SÉCURITÉ

### 7.1 Authentification et autorisation

| Mécanisme | Implémentation |
|---|---|
| **JWT** | Access 60min + Refresh 7j avec rotation |
| **RBAC** | Middleware vérifie le rôle à chaque requête |
| **MFA Admin** | Code à 6 chiffres envoyé par email (TTL 15min) |
| **Blacklist tokens** | Tokens révoqués stockés en base |

### 7.2 Protection des données

| Mécanisme | Détail |
|---|---|
| **HTTPS** | Obligatoire en production (Railway gère SSL) |
| **CORS** | Configuré pour autoriser frontend + mobile |
| **Rate Limiting** | Middleware custom limite les requêtes par IP |
| **Input Sanitization** | Nettoyage automatique de toutes les entrées |
| **Mots de passe** | Bcrypt (Django par défaut) — minimum 6 caractères |
| **Stockage mobile** | flutter_secure_storage (chiffrement AES natif) |

### 7.3 Audit Trail

Toutes les actions sensibles sont enregistrées de manière **immuable** :
- Qui a fait l'action (User ID, email)
- Quand (timestamp précis)
- Depuis où (adresse IP)
- Quoi (ancienne valeur → nouvelle valeur)

### 7.4 Headers de sécurité (production)

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000
SECURE_PROXY_SSL_HEADER: HTTP_X_FORWARDED_PROTO = https
```

---

## 8. DÉPLOIEMENT RAILWAY

### 8.1 Services déployés

| Service Railway | Technologie | Démarrage |
|---|---|---|
| **backend** | Python/Django | `Procfile` |
| **frontend** | Vue.js/Nginx | `NIXPACKS.toml` |
| **postgres** | PostgreSQL 15 | Service managé Railway |
| **download-site** | Node.js/Express | `Procfile` |

### 8.2 Procfile Backend

```
web: python manage.py migrate --noinput --run-syncdb
     && python manage.py collectstatic --noinput
     && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Séquence au démarrage :**
1. Migrations automatiques (création/mise à jour des tables)
2. Collecte des fichiers statiques (CSS/JS admin)
3. Lancement Gunicorn (2 workers, timeout 120s)

### 8.3 Variables d'environnement Backend

| Variable | Description |
|---|---|
| `SECRET_KEY` | Clé secrète Django |
| `DEBUG` | `False` en production |
| `DATABASE_PUBLIC_URL` | URL PostgreSQL Railway |
| `RAILWAY_ENVIRONMENT` | Détecté automatiquement → `ALLOWED_HOSTS = ['*']` |
| `EMAIL_HOST_USER` | Compte Gmail SMTP |
| `EMAIL_HOST_PASSWORD` | Mot de passe application Gmail |

### 8.4 Résolution du problème SSL (boucle 301)

Railway gère le SSL en amont (reverse proxy). Si Django active `SECURE_SSL_REDIRECT = True`, il crée une boucle infinie car la requête arrive déjà en HTTP en interne.

**Solution appliquée :**
```python
SECURE_SSL_REDIRECT = False          # Railway gère SSL
SECURE_PROXY_SSL_HEADER = (          # Django sait qu'il est derrière un proxy HTTPS
    'HTTP_X_FORWARDED_PROTO', 'https'
)
```

---

## 9. DISTRIBUTION MOBILE (SIDELOADING)

### 9.1 Principe

Le sideloading permet d'installer une application Android **sans passer par le Google Play Store**, en téléchargeant directement le fichier `.apk` depuis un site web.

```
Patient
  │
  ▼
Visite le site : https://sghl-download.up.railway.app
  │
  ▼
Clique "Télécharger l'APK"
  │
  ▼
Autorise "Sources inconnues" dans les paramètres Android
  │
  ▼
Ouvre le fichier SGHL-Patient.apk
  │
  ▼
Installe et se connecte avec ses identifiants CHU
```

### 9.2 Site de téléchargement (download-site)

```
download-site/
├── server.js          → Express.js sert l'APK + la landing page
├── public/
│   ├── index.html     → Landing page design violet premium
│   └── sghl.apk       → Fichier APK Android
└── Procfile           → Démarrage Railway
```

**Endpoint de téléchargement :**
```
GET /download/sghl.apk
→ Content-Type: application/vnd.android.package-archive
→ Content-Disposition: attachment; filename="SGHL-Patient.apk"
```

### 9.3 Génération de l'APK

```bash
cd mobile/patient_app
flutter clean
flutter build apk --release --no-tree-shake-icons
# APK généré : build/app/outputs/flutter-apk/app-release.apk
```

### 9.4 Guide d'installation pour le patient

1. **Télécharger** le fichier APK depuis le site
2. **Paramètres Android** → Sécurité → Activer "Sources inconnues"
3. **Ouvrir** le fichier `SGHL-Patient.apk` depuis le gestionnaire de fichiers
4. **Confirmer** l'installation
5. **Se connecter** avec les identifiants fournis par le CHU

---

## 10. GUIDE D'UTILISATION

### 10.1 Connexion Professionnel (Frontend Web)

1. Aller sur l'URL du frontend Railway
2. Cliquer **"Connexion Professionnel"**
3. Saisir email + mot de passe
4. Accès au tableau de bord avec tous les modules

### 10.2 Connexion Admin (avec MFA)

1. Cliquer **"Connexion Admin"**
2. Saisir email → Recevoir un code à 6 chiffres par email
3. Saisir le code (valable 15 minutes)
4. Accès complet + interface `/admin` Django

### 10.3 Inscription Patient (Mobile)

1. Ouvrir l'application SGHL Patient
2. Appuyer **"Créer un compte"**
3. Remplir : Nom, Prénom, Email, Mot de passe (min. 6 caractères), Date de naissance, Sexe, Téléphone
4. Le système crée automatiquement :
   - Un compte Django User
   - Un dossier Patient associé
   - Des tokens JWT retournés immédiatement
5. Connexion automatique après inscription

### 10.4 Fonctionnalités clés Mobile

| Fonctionnalité | Comment l'utiliser |
|---|---|
| **Prendre un RDV** | Onglet RDV → Bouton "+" → Sélectionner médecin + date |
| **Voir résultats labo** | Onglet Résultats → Filtrer par statut → Appuyer pour détails |
| **Télécharger ordonnance PDF** | Onglet Ordonnances → Appuyer sur l'ordonnance → Icône PDF |
| **Envoyer un message** | Onglet Messages → Appuyer "Répondre" ou ouvrir la conversation |
| **Suivre constantes** | Onglet Constantes → Voir graphiques 7 jours |
| **Modifier profil** | Onglet Profil (icône en haut à droite) |

### 10.5 Health Check API

Pour vérifier que le backend fonctionne :

```
GET https://sghl-production.up.railway.app/api/v1/sante/

Réponse :
{
  "status": "ok",
  "timestamp": "2024-12-01T10:00:00Z",
  "version": "1.0",
  "database": "ok",
  "cache": "ok",
  "patients_total": 42,
  "hospitalisations_actives": 8
}
```

---

## ANNEXE — RÉSUMÉ TECHNIQUE

| Critère | Détail |
|---|---|
| **Lignes de code** | ~15 000+ (backend) + ~8 000+ (frontend) + ~5 000+ (mobile) |
| **Modules backend** | 21 applications Django |
| **Endpoints API** | 100+ routes REST |
| **Écrans mobile** | 10 écrans Flutter |
| **Vues frontend** | 30+ vues Vue.js |
| **Sécurité** | JWT + RBAC + MFA + Rate Limiting + Audit Trail |
| **Base de données** | PostgreSQL 15 (Railway) |
| **Déploiement** | 100% cloud Railway (CI/CD via GitHub) |
| **Distribution mobile** | Sideloading APK via site web dédié |
| **Conformité** | RGPD (anonymisation, audit trail, chiffrement) |

---

*Manuel rédigé par NLP-Core-Team — CHU DIGNE HOSPITAL — 2024*
