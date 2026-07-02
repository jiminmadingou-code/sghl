# Fonctionnalités à Implémenter - SGHL

Ce document liste les fonctionnalités manquantes et les travaux à venir pour compléter le Système de Gestion Hospitalière et de Laboratoire.

---

## 🔴 Priorité Haute

### 1. WebSocket Temps Réel Complet

**Fichier:** `backend/chat/consumers.py`

**Fonctionnalités:**
- Configuration ASGI complète
- WebSocket consumers pour chat
- Channel Redis Layer
- Gestion déconnexions
- Typing indicators
- Read receipts

**Fichier:** `backend/core/asgi.py`

```python
"""
ASGI config for SGHL project.
"""
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

**Installation:**
```bash
pip install channels channels-redis daphne
```

---

### 2. Service Email Complet

**Module:** `backend/email_service/`

**État:** ✅ Créé (models.py, services.py)

**À faire:**
- Templates HTML professionnels
- Gestion pièces jointes
- Unsubscribe mechanism
- Email tracking (opens, clicks)
- A/B testing templates

**Templates à créer:**
```python
# backend/email_service/templates/
- welcome.html
- password_reset.html
- appointment_reminder.html
- lab_results.html
- prescription_ready.html
- invoice.html
```

**Commande worker:**
```bash
python manage.py run_email_worker
```

---

### 3. Génération PDF Signés

**État:** ✅ Créé (laboratoire/pdf_generator.py)

**À faire:**
- Factures PDF
- Certificats médicaux
- Ordonnances électroniques
- Signatures numériques (eIDAS)
- HDS stockage PDF

**Modules à créer:**
```python
# backend/facturation/pdf_generator.py
# backend/hospitalisations/pdf_generator.py
# backend/core/signature_electronique.py
```

**Installation:**
```bash
pip install weasyprint reportlab signxml
```

---

### 4. Backup Automatique & DRP

**Fichier:** `backend/scripts/backup_daily.sh`

```bash
#!/bin/bash
# Backup quotidien chiffré

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"
PG_DUMP="pg_dump"

# Dump PostgreSQL
pg_dump -U sghl_user sghl_db > ${BACKUP_DIR}/db_${DATE}.sql

# Chiffrer avec GPG
gpg --symmetric --cipher-algo AES256 \
    --passphrase-file /etc/sghl/backup_key \
    ${BACKUP_DIR}/db_${DATE}.sql

# Upload S3
aws s3 cp ${BACKUP_DIR}/db_${DATE}.sql.gpg s3://sghl-backups/${DATE}/

# Cleanup local (garde 30 jours)
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

# Log
echo "Backup completed: ${DATE}" >> /var/log/sghl/backup.log
```

**Script Python pour restauration test:**
```python
# backend/scripts/test_restore.py
import subprocess
import boto3
from datetime import datetime, timedelta

def test_restore_weekly():
    """Test de restauration hebdomadaire (DRP)"""
    # Télécharger backup le plus récent
    s3 = boto3.client('s3')
    backup_key = get_latest_backup_key()
    
    s3.download_file(
        'sghl-backups',
        backup_key,
        '/tmp/restore_test.sql.gpg'
    )
    
    # Déchiffrer
    subprocess.run(['gpg', '--decrypt', ...])
    
    # Restaurer sur DB de test
    subprocess.run(['psql', '-f', '/tmp/restore_test.sql'])
    
    # Vérifier intégrité
    verify_database_integrity()
    
    # Log résultat
    log_restore_test()
```

**Cron job:**
```bash
# /etc/cron.daily/sghl-backup
0 2 * * * /app/scripts/backup_daily.sh

# /etc/cron.weekly/sghl-restore-test
0 3 * * 0 /app/scripts/test_restore.py
```

---

### 5. Tests de Charge API

**Fichier:** `backend/tests/locustfile.py`

```python
from locust import HttpUser, task, between
import json

class SGHLUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login pour obtenir token
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["access"]
        self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_patients(self):
        self.client.get("/api/v1/patients/")
    
    @task(2)
    def get_dashboard(self):
        self.client.get("/api/v1/dashboard/summary")
    
    @task(1)
    def create_patient(self):
        self.client.post("/api/v1/patients/", json={
            "nom": "Test",
            "prenom": "User",
            "date_naissance": "1990-01-01",
            "sexe": "M"
        })
    
    @task(1)
    def get_hospitalisations(self):
        self.client.get("/api/v1/hospitalisations/")
```

**Exécution tests de charge:**
```bash
# Installation
pip install locust

# Lancer locust
locust -f tests/locustfile.py --host=http://localhost:8000

# Headless mode (CI/CD)
locust -f tests/locustfile.py --headless -u 100 -r 10 -t 5m
```

**Scénarios de test:**
- 50 utilisateurs simultanés
- 200 utilisateurs simultanés
- 500 utilisateurs simultanés
- Pic soudain (flash crowd)

---

## 🟠 Priorité Moyenne

### 6. Interopérabilité HL7/FHIR

**Module:** `backend/interop/`

**Fonctionnalités:**
- Parser HL7 v2.x messages
- Mapper FHIR resources
- Webhooks pour assurances
- Export standards médicaux

**Installation:**
```bash
pip install fhirparser hl7apy
```

**Exemple FHIR Patient:**
```python
from fhir.resources.patient import Patient as FHIRPatient

def patient_to_fhir(patient):
    fhir_patient = FHIRPatient(
        id=patient.id,
        name=[{"family": patient.nom, "given": [patient.prenom]}],
        birthDate=patient.date_naissance.isoformat(),
        gender="male" if patient.sexe == "M" else "female"
    )
    return fhir_patient
```

---

### 7. Moteur de Prescription Électronique

**Fichier:** `backend/hospitalisations/prescription_engine.py`

**Fonctionnalités:**
- Validation interactions médicamenteuses
- Calcul posologie pédiatrique
- Alerte allergies
- Signature électronique
- Base de données médicaments (VIDAL)

**Structure:**
```python
class PrescriptionEngine:
    def validate_prescription(self, prescriptions):
        # Vérifier interactions
        interactions = self.check_interactions(prescriptions)
        
        # Vérifier allergies patient
        allergies = self.check_allergies(prescriptions)
        
        # Vérifier posologies
        posologies = self.validate_posologies(prescriptions)
        
        return {
            'valid': not (interactions or allergies),
            'interactions': interactions,
            'allergies': allergies,
            'posologies': posologies
        }
```

---

### 8. API Versioning & OpenAPI

**Fichier:** `backend/core/versioning.py`

```python
from ninja import NinjaAPI
from ninja.versioning import URLPathVersioning

api = NinjaAPI(
    version='1.0',
    versioning_class=URLPathVersioning,
    # ... autres configs
)

# Usage
@api.get("/patients/", versions=['1.0', '2.0'])
def get_patients_v1(request):
    return [...]

@api.get("/patients/", versions=['3.0'])
def get_patients_v3(request):
    return [...]  # Nouveau format
```

**Génération OpenAPI:**
```bash
python manage.py spectacular --file openapi.yml
python manage.py spectacular --color --file openapi.yml | swagger-ui
```

---

## 🟡 Priorité Basse

### 9. Application Mobile Flutter

**Structure:**
```
mobile_flutter/
├── lib/
│   ├── main.dart
│   ├── app/
│   ├── features/
│   │   ├── auth/
│   │   ├── appointments/
│   │   ├── medical_history/
│   │   ├── lab_results/
│   │   └── chat/
│   ├── services/
│   ├── providers/
│   └── widgets/
├── test/
└── pubspec.yaml
```

**Packages clés:**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  shared_preferences: ^2.2.2
  provider: ^6.1.1
  web_socket_channel: ^2.4.0
  flutter_local_notifications: ^16.3.0
  pdf: ^3.10.7
  url_launcher: ^6.2.1
  cached_network_image: ^3.3.0
```

---

### 10. Monitoring ELK Stack

**Fichier:** `docker-compose.elk.yml`

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline
      - ./monitoring/logstash/patterns:/usr/share/logstash/patterns
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/filebeat/filebeat:8.11.0
    volumes:
      - ./monitoring/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - elasticsearch
```

---

### 11. Sécurité Avancée

**Modules à créer:**
```python
# backend/security/
- penetration_testing.py
- vulnerability_scanner.py
- ddos_protection.py
- waf_rules.py
```

**Docker scan:**
```bash
# Installation
curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Scan
trivy image django:3.2
trivy filesystem backend/
```

---

### 12. Anonymisation Données RGPD

**Fichier:** `backend/anonymization/anonymizer.py`

```python
from django.db import transaction
from faker import Faker
import hashlib

fake = Faker('fr_FR')

class DataAnonymizer:
    @staticmethod
    @transaction.atomic
    def anonymize_patient(patient_id):
        patient = Patient.objects.get(id=patient_id)
        
        # Hash de l'ID pour traçabilité
        anonymized_id = hashlib.sha256(str(patient.id).encode()).hexdigest()[:12]
        
        # Anonymisation
        patient.numero = f"ANON-{anonymized_id}"
        patient.nom = fake.last_name()
        patient.prenom = fake.first_name()
        patient.date_naissance = fake.date_of_birth()
        patient.adresse = fake.address()
        patient.email = fake.email()
        patient.telephone = fake.phone_number()
        
        patient.save()
        
        # Anonymiser données liées
        DataAnonymizer._anonymize_related_data(patient)
        
        return patient
```

---

## 📊 Planning Estimé

| Phase | Fonctionnalités | Durée Estimée |
|-------|----------------|---------------|
| **Phase 1** | WebSocket, Email, PDF | 3-4 semaines |
| **Phase 2** | Backup/DRP, Tests charge | 2-3 semaines |
| **Phase 3** | HL7/FHIR, Prescription | 3-4 semaines |
| **Phase 4** | Mobile Flutter | 6-8 semaines |
| **Phase 5** | Monitoring, Sécurité | 2-3 semaines |

**Total estimé:** 16-22 semaines

---

## 🛠️ Scripts Utilitaires

### Setup Complet Développement

```bash
#!/bin/bash
# setup_development.sh

echo "🚀 Configuration environnement développement SGHL"

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Tests, linting

# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser
python manage.py createsuperuser

# Seed données test
python manage.py loaddata fixtures/test_data.json

# Frontend
cd ../frontend
npm install

# Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

echo "✅ Configuration terminée!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Redis: localhost:6379"
```

### Setup Production

```bash
#!/bin/bash
# setup_production.sh

echo "🔧 Configuration environnement production SGHL"

# Variables d'environnement
read -p "Domaine: " DOMAIN
read -p "Email admin: " ADMIN_EMAIL
read -p "Mot de passe DB: " DB_PASSWORD

# Générer secrets
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Créer .env production
cat > .env << EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN}
DB_PASSWORD=${DB_PASSWORD}
EOF

# SSL avec Let's Encrypt
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone -d ${DOMAIN} -d www.${DOMAIN} \
  --email ${ADMIN_EMAIL} \
  --agree-tos

# Build production
docker-compose build --no-cache

echo "✅ Production setup terminé"
```

---

## 📚 Ressources & Documentation

### Documentation Officielle
- [Django Channels](https://channels.readthedocs.io/)
- [WeasyPrint](https://doc.courtbouillon.org/weasyprint/)
- [Locust](https://docs.locust.io/)
- [FHIR Specification](https://www.hl7.org/fhir/)

### Sécurité Médicale
- [HDS Certification](https://www.certificat-sante.fr/)
- [RGPD Santé](https://cnil.fr/fr/rgpd-et-sante)
- [eIDAS Signature](https://eidas.europa.eu/)

### Best Practices
- [OWASP Medical Health](https://owasp.org/www-project-medical-health/)
- [HIPAA Compliance](https://www.hhs.gov/hipaa/)
- [ISO 27001 Santé](https://www.iso.org/isoiec-27001-information-security.html)

---

## 🤝 Contribuer

Pour contribuer à ce projet:

1. Fork le repository
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

**Conventional Commits:**
```
feat: Nouvelle fonctionnalité
fix: Correction de bug
docs: Documentation
style: Formatage
refactor: Refactoring
test: Tests
chore: Maintenance
```

---

**Dernière mise à jour:** Décembre 2024  
**Version:** 1.0.0  
**Équipe:** NLP-Core-Team
