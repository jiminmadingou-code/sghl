# Guide d'Exécution - Système de Gestion Hospitalière et de Laboratoire (SGHL)

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Architecture du Projet](#architecture-du-projet)
3. [Installation et Configuration](#installation-et-configuration)
4. [Démarrage Rapide (Docker)](#démarrage-rapide-docker)
5. [Démarrage Manuel (Développement)](#démarrage-manuel-développement)
6. [Fonctionnalités Implémentées](#fonctionnalités-implémentées)
7. [Fonctionnalités Manquantes](#fonctionnalités-manquantes)
8. [Commandes Utiles](#commandes-utiles)
9. [Dépannage](#dépannage)
10. [Déploiement Production](#déploiement-production)

---

## Prérequis

### Outils Requis

- **Docker & Docker Compose** (recommandé)
  - [Installer Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Python 3.10+** (pour développement manuel)
- **Node.js 18+** et **npm** (pour développement frontend)
- **Git** pour cloner le projet

### Vérification des versions

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Vérifier Python
python --version

# Vérifier Node.js
node --version
npm --version
```

---

## Architecture du Projet

```
sghl/
├── backend/                 # Django API REST
│   ├── audit/              # Traçabilité et logs immuables
│   ├── patients/           # Gestion patients
│   ├── hospitalisations/   # Gestion lits, chambres, services
│   ├── laboratoire/        # LIS - Examens et résultats
│   ├── pharmacie/          # Gestion stocks et médicaments
│   ├── facturation/        # Factures et paiements
│   ├── personnel/          # RH et RBAC
│   ├── soins/              # Planification soins infirmiers
│   ├── dashboard/          # KPIs et monitoring
│   ├── chat/               # Messagerie temps réel
│   ├── gardes/             # Plannings de garde
│   └── core/               # Configuration et sécurité
│
├── frontend/               # Vue.js 3
│   ├── src/
│   │   ├── views/          # Pages principales
│   │   ├── components/     # Composants réutilisables
│   │   ├── services/       # Appels API
│   │   └── stores/         # State management (Pinia)
│   └── nginx.conf/         # Configuration Nginx
│
├── monitoring/             # Prometheus & Grafana
├── nginx/                  # SSL et reverse proxy
└── docker-compose.yml      # Orchestration
```

---

## Installation et Configuration

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd sghl
```

### 2. Configuration Backend

```bash
cd backend

# Copier le fichier d'environnement
cp .env.example .env

# Éditer le fichier .env
# Sur Windows (PowerShell):
notepad .env

# Sur Linux/Mac:
nano .env
```

**Variables obligatoires à modifier:**

```env
SECRET_KEY=generate-a-secret-key-aleatoire
DB_PASSWORD=votre-mot-de-passe-secure
GRAFANA_PASSWORD=votre-mot-de-passe-grafana

# Email SMTP (pour notifications)
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password-gmail
```

> **💡 Générer un SECRET_KEY sécurisé:**
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 3. Configuration Frontend

```bash
cd frontend

# Aucune configuration nécessaire pour le développement
# Le proxy Vite redirige vers le backend automatiquement
```

---

## Démarrage Rapide (Docker)

### Option 1: Démarrage Complet (Production-like)

```bash
# Démarrer tous les services (Backend, Frontend, DB, Redis, Monitoring)
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter tous les services
docker-compose down
```

### Option 2: Développement (Backend + DB + Redis seulement)

```bash
# Démarrer seulement les services backend
docker-compose up -d postgres redis backend

# Accéder au shell du container backend
docker exec -it sghl-backend bash

# Dans le container:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Créer un utilisateur de test
python manage.py shell
>>> from personnel.models import Personnel
>>> from patients.models import Patient
>>> # Créez vos utilisateurs et patients ici
>>> exit()

# Redémarrer le backend avec les migrations
docker-compose restart backend
```

### Option 3: Avec Monitoring (Prometheus + Grafana)

```bash
# Démarrer avec les services de monitoring
docker-compose --profile monitoring up -d

# Accéder à Grafana: http://localhost:3000
# Login: admin / admin123

# Accéder à Prometheus: http://localhost:9090
```

---

## Démarrage Manuel (Développement)

### Backend Django

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer PostgreSQL (optionnel, utilise SQLite par défaut)
# Modifier backend/.env pour PostgreSQL

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver 8000

# Avec ASGI pour WebSocket (chat temps réel)
daphne -b 127.0.0.1 -p 8000 core.asgi:application
```

### Frontend Vue.js

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev

# Ouvrir http://localhost:5173
```

### Redis (Cache)

```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis:alpine

# Option 2: Installation locale
# Windows: https://github.com/microsoftarchive/redis/releases
# Linux/Mac: brew install redis ou apt-get install redis-server
redis-server
```

---

## Fonctionnalités Implémentées

### ✅ 1. Audit Trail & Traçabilité
- Journal immuable de toutes les actions
- Filtrage et recherche
- Statistiques d'audit

**Endpoints:**
```
GET /api/v1/audit/
GET /api/v1/audit/stats/summary
```

### ✅ 2. Sécurité Avancée
- Chiffrement AES-256
- Rate Limiting
- MFA (prêt)
- Rotation JWT

### ✅ 3. Gestion Hospitalisation
- Structure: Bâtiment > Service > Chambre > Lit
- Verrouillage optimiste
- Transferts inter-services
- Taux d'occupation

**Endpoints:**
```
GET /api/v1/hospitalisations/batiments/
GET /api/v1/hospitalisations/services/{id}/disponibilite/
POST /api/v1/hospitalisations/admission/
```

### ✅ 4. Soins Infirmiers
- Planification des soins
- Constantes vitales avec alertes
- Interventions documentées
- Visualisation tendances

**Endpoints:**
```
GET /api/v1/soins/constantes/{hospitalisation_id}
POST /api/v1/soins/constantes/
GET /api/v1/soins/constantes/alertes
```

### ✅ 5. Laboratoire (LIS)
- Workflow complet: Commande → Publication
- Validation biologiste
- Résultats immuables
- Audit trail

**Endpoints:**
```
GET /api/v1/laboratoire/examens/
POST /api/v1/laboratoire/examens/
PUT /api/v1/laboratoire/examens/{id}/valider/
```

### ✅ 6. Pharmacie
- Gestion lots et péremption
- Alertes rupture
- Décrémentation automatique
- Mouvements traçables

**Endpoints:**
```
GET /api/v1/pharmacie/medicaments/
GET /api/v1/pharmacie/lots/alertes/
POST /api/v1/pharmacie/mouvements/
```

### ✅ 7. Facturation
- Factures multi-types
- Paiements partiels/échelonnés
- Tiers-payant
- Journal comptable

**Endpoints:**
```
GET /api/v1/facturation/factures/
POST /api/v1/facturation/factures/
POST /api/v1/facturation/paiements/
```

### ✅ 8. Dashboard & KPIs
- Taux d'occupation
- Recettes en temps réel
- Examens en attente
- Alertes stock
- Health check

**Endpoints:**
```
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/kpi/patients
GET /api/v1/dashboard/health
```

### ✅ 9. Chat Temps Réel
- Conversations médecin-patient
- Messages avec pièces jointes
- Notifications push
- Statut lu/non lu

**Endpoints:**
```
GET /api/v1/chat/conversations/
POST /api/v1/chat/messages/
WebSocket: ws://localhost:8000/ws/chat/{conversation_id}/
```

### ✅ 10. Gardes & Plannings
- Planification gardes
- Disponibilités médecins
- Gestion congés
- Calcul créneaux libres

**Endpoints:**
```
GET /api/v1/gardes/planning/
POST /api/v1/gardes/disponibilites/
GET /api/v1/gardes/creneaux-libres/{medecin_id}
```

---

## Fonctionnalités Manquantes

### 🔴 Backend

#### 1. **WebSocket Temps Réel Complet**
```python
# À implémenter dans core/asgi.py et chat/consumers.py
- Configuration ASGI complète
- Chat consumers pour WebSocket
- Channel Redis Layer
- Gestion connexions déconnectées
```

#### 2. **Service Email SMTP**
```python
# Nouveau module: backend/email_service/
- Envoi emails transactionnels
- Templates HTML professionnels
- Files d'attente asynchrones
- Validation et réessai automatique
```

#### 3. **Génération PDF Signés**
```python
# À implémenter dans:
- laboratoire/pdf_generator.py (résultats)
- facturation/pdf_generator.py (factures)
- hospitalisations/pdf_generator.py (certificats)
- Signature électronique intégrée
```

#### 4. **Backup Automatique & DRP**
```python
# Scripts backend/scripts/
- backup_daily.sh (PostgreSQL dump)
- backup_encrypted.py (chiffrement AES)
- restore_test.py (tests trimestriels)
- Upload cloud (S3/Backblaze)
```

#### 5. **Tests de Charge API**
```python
# Tests/locustfile.py
- Scénarios utilisateurs simultanés
- Tests performance endpoints critiques
- Rapports de charge
- Seuil alerte performance
```

#### 6. **Interopérabilité HL7/FHIR**
```python
# Nouveau module: backend/interop/
- Parser HL7 v2.x
- Mapper FHIR resources
- API webhooks assurances
- Export standards médicaux
```

#### 7. **Moteur de Prescription Électronique**
```python
# hospitalisations/prescription_engine.py
- Validation interactions médicamenteuses
- Calcul posologie pédiatrique
- Alerte allergies
- Signature électronique
```

#### 8. **API Versioning & Dépréciation**
```python
# core/versioning.py
- Auto versioning API
- Policy de dépréciation
- Compatibilité ascendante
- Documentation Swagger/OpenAPI auto
```

### 🔴 Frontend

#### 1. **Dashboard Complet avec Graphiques**
```vue
<!-- frontend/src/views/DashboardView.vue -->
- Intégration Chart.js ou ApexCharts
- Taux occupation temps réel
- Évolution recettes
- Examens par statut
- Alertes pharmacie visuelles
```

#### 2. **Interface Chat Temps Réel**
```vue
<!-- frontend/src/components/ChatWidget.vue (améliorer) -->
- WebSocket connection management
- Notifications push navigateur
- Upload pièces jointes
- Historique scroll infini
- Recherche messages
```

#### 3. **Gestion Planning Soins**
```vue
<!-- frontend/src/views/SoinsView.vue -->
- Calendrier interactif (FullCalendar)
- Drag & drop planifications
- Visualisation constantes graphiques
- Alertes doses omises
- Checklists soins
```

#### 4. **Visualisation Laboratoire**
```vue
<!-- frontend/src/views/LaboratoireView.vue -->
- Workflow visuel examens
- Validation biologiste UI
- Téléchargement PDF
- Historique modifications
- Filtres avancés
```

#### 5. **Application Mobile Flutter**
```dart
// À créer: mobile_flutter/
- Prise de RDV
- Consultation historique
- Rappels médicamenteux
- Résultats laboratoire
- Notifications push
- Chat intégré
```

### 🔴 DevOps & Infrastructure

#### 1. **CI/CD Pipeline Complet**
```yaml
# .github/workflows/
- tests-unitaires.yml
- security-scan.yml
- deploy-staging.yml
- deploy-production.yml
- backup-verification.yml
```

#### 2. **Monitoring ELK Stack**
```yaml
# docker-compose.monitoring.yml
- Elasticsearch (logs)
- Logstash (processing)
- Kibana (visualisation)
- Filebeat (collecte)
```

#### 3. **Sécurité Avancée**
```python
# backend/security/
- Tests intrusion automatiques
- Scan vulnérabilités dépendances
- WAF configuration
- DDoS protection
- Penetration testing scripts
```

#### 4. **Anonymisation Données**
```python
# backend/anonymization/
- RGPD compliance
- Pseudonymisation réversible
- Anonymisation statistiques
- Consentement patient tracking
- Droit à l'oubli
```

---

## Commandes Utiles

### Backend Django

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Superuser
python manage.py createsuperuser

# Shell interactif
python manage.py shell

# Tests
python manage.py test
python manage.py test patients.tests
python manage.py test --coverage

# Collect static
python manage.py collectstatic --noinput

# Flush DB (développement)
python manage.py flush

# Dump data
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# Check security
python manage.py check --deploy

# Generate API schema
python manage.py spectacular --file schema.yml
```

### Frontend Vue.js

```bash
# Development
npm run dev

# Build production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Tests (si configurés)
npm run test
npm run test:unit
npm run test:e2e
```

### Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Restart service
docker-compose restart backend

# Execute command in container
docker exec -it sghl-backend python manage.py shell

# Database backup
docker exec sghl-postgres pg_dump -U sghl_user sghl_db > backup.sql

# Database restore
cat backup.sql | docker exec -i sghl-postgres psql -U sghl_user sghl_db

# Prune unused
docker-compose down -v  # WARNING: Delete all data
docker system prune -a
```

### Redis

```bash
# Connect Redis CLI
docker exec -it sghl-redis redis-cli

# Monitor commands
redis-cli monitor

# Flush all (développement seulement!)
redis-cli FLUSHALL

# Stats
redis-cli INFO
```

---

## Dépannage

### Problème: Backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

#常见问题:
# 1. Database connection failed
docker-compose ps  # Check postgres is running
docker-compose logs postgres

# 2. Migration errors
docker exec -it sghl-backend bash
python manage.py migrate --run-syncdb

# 3. Redis connection
docker exec -it sghl-redis redis-cli ping
# Should return: PONG
```

### Problème: Frontend ne connecte pas au backend

```javascript
// Vérifier CORS dans backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

// Vérifier Vite proxy dans vite.config.js
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}

// Clear browser cache
// Check Network tab in DevTools
```

### Problème: PostgreSQL connection refused

```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Check environment variables
docker exec sghl-backend env | grep DB_

# Test connection
docker exec -it sghl-postgres psql -U sghl_user -d sghl_db

# If password issue, recreate container
docker-compose down postgres
docker volume rm sghl_postgres_data
docker-compose up -d postgres
```

### Problème: Redis cache non disponible

```bash
# Check Redis
docker exec sghl-redis redis-cli ping

# Restart Redis
docker-compose restart redis

# Clear cache
docker exec -it sghl-backend bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Problème: Permissions fichiers

```bash
# Fix permissions
chmod -R 755 backend/media
chmod -R 755 backend/static
chown -R 1000:1000 backend/media backend/static

# Docker volumes
docker volume inspect sghl_static_volume
docker volume inspect sghl_media_volume
```

---

## Déploiement Production

### Prérequis Production

- [ ] Certificats SSL (Let's Encrypt ou commercial)
- [ ] Domaine configuré (DNS A record)
- [ ] Firewall configuré (ports 80, 443 seulement)
- [ ] Backup automatique externalisé
- [ ] Monitoring alertes configurées
- [ ] Mots de passe changés (tous les services)
- [ ] DEBUG=False dans .env
- [ ] SECRET_KEY unique et sécurisé

### Étapes Déploiement

#### 1. Préparation

```bash
# Générer SECRET_KEY sécurisé
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Mettre à jour .env production
DEBUG=False
SECRET_KEY=<generated-key>
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Configurer SSL
mkdir -p nginx/ssl
# Placer certificats: nginx/ssl/fullchain.pem et nginx/ssl/privkey.pem
```

#### 2. Build et Test

```bash
# Build images production
docker-compose build --no-cache

# Test local avant déploiement
docker-compose up -d

# Vérifier tous les services
docker-compose ps

# Tester endpoints
curl https://votre-domaine.com/api/v1/dashboard/health
```

#### 3. Déploiement

```bash
# Deploy with zero downtime
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Monitor health
watch -n 5 'docker-compose ps'
```

#### 4. Post-Déploiement

```bash
# Vérifier monitoring
# Grafana: https://votre-domaine.com:3000
# Prometheus: https://votre-domaine.com:9090

# Tester backup automatique
docker exec sghl-postgres pg_dump -U sghl_user sghl_db | gzip > /backup/$(date +%Y%m%d).sql.gz

# Security scan
docker run --rm -v $(pwd):/app aquasec/trivy filesystem /app
```

### Monitoring Production

**Grafana Dashboards:**
- Système: CPU, RAM, Disk
- Application: API response time, Error rate
- Database: Connections, Queries/s
- Redis: Memory, Commands/s

**Alertes Configurées:**
- API response time > 2s
- Error rate > 1%
- Disk usage > 80%
- Database connections > 90%
- Redis memory > 80%

### Scale Horizontal

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
  worker:
    deploy:
      replicas: 2
```

```bash
# Scale
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

---

## Support & Contact

**Équipe de Développement:** NLP-Core-Team

**Documentation:**
- [Django Documentation](https://docs.djangoproject.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Docker Documentation](https://docs.docker.com/)

**Ressources:**
- API Swagger: http://localhost:8000/api/v1/docs/
- Admin Django: http://localhost:8000/admin/
- Grafana: http://localhost:3000

---

## License

Système de Gestion Hospitalière et de Laboratoire (SGHL)  
Développé par NLP-Core-Team  
Tous droits réservés © 2024
