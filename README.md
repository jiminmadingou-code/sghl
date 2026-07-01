# Système de Gestion Hospitalière et de Laboratoire (SGHL)

## 🏥 ERP Médical Full-Stack Intégré

Un système complet de gestion hospitalière et de laboratoire conçu pour digitaliser l'intégralité du parcours patient, de l'admission au suivi post-hospitalisation.

---

## ✨ Fonctionnalités Principales

### 📋 Gestion Clinique & Hospitalisation
- **Cycle de Consultation**: Diagnostic CIM-10, e-ordonnance, archivage sécurisé, signature électronique
- **Logistique Hospitalière**: Gestion hiérarchique Bâtiment > Service > Chambre > Lit
- **Soins & Infirmier**: Planification des soins, constantes vitales avec graphiques, alertes automatiques
- **Verrouillage optimiste** pour éviter les incohérences simultanées

### 🔬 Laboratoire (LIS)
- Workflow structuré: Commande → Prélèvement → Affectation → Résultats → Validation → Publication
- Validation exclusive par biologiste
- Résultats immuables après validation
- Audit trail obligatoire
- Génération PDF signés électroniquement

### 💊 Pharmacie & Logistique
- Gestion d'inventaire (lots, péremption, seuils d'alerte)
- Décrémentation automatique des stocks
- Historique complet des mouvements
- Alertes de rupture

### 💰 Facturation & Finances
- Moteur de calcul automatisé
- Gestion tiers-payant (assurances)
- Paiements partiels ou échelonnés
- Journal comptable immuable

### 👥 RH & Pilotage
- RBAC (Role-Based Access Control) strict
- Planning de garde avec validation
- Dashboard administratif avec KPIs temps réel
- Statistiques dynamiques via Redis

### 📱 Application Mobile Patient
- **Self-Service**: Prise de RDV, confirmation email, notifications push
- **Transparence**: Historique médical, résultats PDF, plan de soins
- **Observance**: Rappels médicamenteux, suivi post-opératoire
- **Chat temps réel** médecin-patient

---

## 🛠 Stack Technique

### Backend
- **Python 3.11+**
- **Django & Django Ninja** (API REST typée Pydantic, async)
- **PostgreSQL** (Transactions ACID, indexation avancée)
- **Redis** (Cache, file d'attente)
- **JWT** (Auth stateless avec rotation)

### Frontend Web
- **Vue.js 3** (Composition API)
- **Tailwind CSS**
- **Axios**

### Mobile
- **Flutter** (Cross-platform iOS/Android)

### Infrastructure
- **Docker & Docker Compose**
- **Nginx** (Reverse proxy, SSL)
- **Prometheus + Grafana** (Monitoring)
- **SMTP Gmail** (Notifications email)

### Sécurité
- HTTPS obligatoire
- JWT avec rotation de refresh tokens
- MFA (Authentification à deux facteurs)
- Chiffrement AES-256 (données au repos)
- Bcrypt pour mots de passe
- Rate Limiting
- Audit Trail immuable

---

## 📦 Fonctionnalités Implémentées

### ✅ Module Audit & Traçabilité
- Journal immuable de toutes les actions
- Traçabilité complète (User, Timestamp, IP, Old/New Value)
- Filtrage et statistiques
- API: `/api/v1/audit/`

### ✅ Sécurité Avancée
- Chiffrement AES-256
- Rate Limiting
- Validation des entrées
- MFA Handler
- Token rotation

### ✅ Soins & Infirmier
- Planification des soins
- Constantes vitales avec tendances
- Alertes seuils critiques
- Interventions infirmières
- API: `/api/v1/soins/`

### ✅ Gestion des Lits
- Structure hiérarchique complète
- Verrouillage optimiste
- Transferts inter-services
- Taux d'occupation en temps réel

### ✅ Dashboard & KPIs
- KPIs temps réel avec cache Redis
- Monitoring système
- Health check endpoint
- API: `/api/v1/dashboard/`

### ✅ Chat Temps Réel
- Conversations médecin-patient
- Notifications push
- Messages avec pièces jointes
- API: `/api/v1/chat/`

### ✅ Gardes & Plannings
- Planning de garde avec validation
- Disponibilités médecins
- Gestion des congés
- Prévention chevauchements
- API: `/api/v1/gardes/`

---

## 🚀 Installation Rapide

### Développement Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev

# Infrastructure (Docker)
docker-compose up -d postgres redis
```

### Production (Docker)

```bash
# Configuration
cp .env.example .env
nano .env  # Modifier les variables sensibles

# Lancer
docker-compose up -d

# Monitoring (optionnel)
docker-compose --profile monitoring up -d
```

---

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/v1/docs/
- **Fonctionnalités Détaillées**: [FEATURES_IMPLEMENTED.md](backend/FEATURES_IMPLEMENTED.md)
- **Guide de Déploiement**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Architecture Technique**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🔐 Conformité & Sécurité

- ✅ Traçabilité complète et immuable
- ✅ Sécurité de niveau bancaire
- ✅ Chiffrement AES-256
- ✅ Conformité RGPD (anonymisation)
- ✅ Audit trail obligatoire
- ✅ Backup quotidien externalisé
- ✅ Plan de Reprise d'Activité (DRP)

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Reverse Proxy)                │
│                    SSL Termination                       │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  Frontend     │ │  Backend   │ │   Mobile    │
│  Vue.js       │ │  Django    │ │   Flutter   │
│  Port 5173    │ │  Port 8000 │ │   API       │
└───────────────┘ └─────┬──────┘ └─────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼───────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  PostgreSQL   │ │   Redis    │ │  File Store │
│  Port 5432    │ │  Port 6379 │ │  Encrypted  │
└───────────────┘ └────────────┘ └─────────────┘
```

---

## 🧪 Tests

```bash
# Backend
python manage.py test

# Frontend
npm run test

# Load testing
locust -f load_test.py --host=http://localhost:8000
```

---

## 📈 Monitoring

### Grafana Dashboards
- Taux d'occupation des lits
- Recettes journalières/mensuelles
- Examens laboratoire en attente
- Performance API
- Santé système

### Métriques Prometheus
- Request rate
- Error rate
- Response time (P95, P99)
- Database connections
- Cache hit rate

---

## 🤝 Contribution

1. Fork le projet
2. Crée une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit tes changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvre un Pull Request

### Standards de Code
- Backend: PEP8, type hints
- Frontend: ESLint, Prettier
- Tests: Minimum 80% coverage
- Commit messages: Conventional Commits

---

## 📄 Licence

Propriétaire - Tous droits réservés © 2024 NLP-Core-Team

---

## 📞 Support

- **Documentation**: https://docs.sghl.example
- **Issues**: https://github.com/your-org/sglh/issues
- **Email**: support@sghl.example

---

## 🏆 Badges

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.3-orange.svg)
![Flutter](https://img.shields.io/badge/Flutter-3.10-cyan.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

---

**Développé avec ❤️ par NLP-Core-Team**
