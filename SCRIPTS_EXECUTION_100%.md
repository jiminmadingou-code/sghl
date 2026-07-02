# 🛠️ SCRIPTS D'EXÉCUTION - PLAN 100%

**Note:** Ces scripts sont prêts à copier-coller dans votre terminal

---

## **PHASE 1 - SCRIPTS D'IMPLÉMENTATION**

### 1.1 Setup Tests E2E Frontend

```bash
#!/bin/bash
# backend_e2e_setup.sh

cd frontend

# Installer Playwright
npm install --save-dev @playwright/test

# Installer navigateurs
npx playwright install

# Créer répertoires tests
mkdir -p tests/e2e
mkdir -p tests/fixtures

echo "✅ Playwright setup terminé"
echo "Pour lancer les tests: npm run test:e2e"
echo "Pour UI mode: npm run test:e2e:ui"
```

### 1.2 Setup Tests E2E Mobile

```bash
#!/bin/bash
# mobile_e2e_setup.sh

cd mobile/patient_app

# Installer dépendances Flutter si nécessaire
flutter pub get

# Créer répertoire tests intégration
mkdir -p integration_test

# Lancer les tests
echo "Pour tester sur Android/iOS:"
echo "flutter test integration_test/"
echo ""
echo "Ou avec émulateur:"
echo "flutter emulators --launch android_emulator"
echo "flutter test integration_test/"
```

### 1.3 Setup Monitoring Stack

```bash
#!/bin/bash
# monitoring_setup.sh

cd monitoring

# Créer répertoire provisioning
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/provisioning/datasources

# Lancer stack monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Attendre démarrage
sleep 10

echo "✅ Stack Monitoring démarré"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "Ajouter Prometheus comme datasource dans Grafana"
```

### 1.4 Configuration Backend Metrics

```bash
#!/bin/bash
# backend_metrics_setup.sh

cd backend

# Installer dépendances Prometheus
pip install prometheus-client django-prometheus

# Ajouter à requirements.txt
echo "prometheus-client>=0.17.0" >> requirements.txt
echo "django-prometheus>=2.3.0" >> requirements.txt

# Ajouter middleware dans settings.py (déjà documenté dans PLAN_100_PERCENT.md)

echo "✅ Metrics configurées"
echo "Endpoint: http://localhost:8000/metrics/"
```

---

## **PHASE 2 - Tests de Charge**

### 2.1 Setup Locust

```bash
#!/bin/bash
# load_tests_setup.sh

cd backend

# Installer Locust
pip install locust

# Créer répertoires résultats
mkdir -p tests/results

# Copier le locustfile (déjà fourni dans PLAN_100_PERCENT.md)
# Fichier: backend/tests/locustfile.py

echo "✅ Locust configuré"
echo ""
echo "Pour lancer les tests:"
echo "locust -f tests/locustfile.py --host=http://localhost:8000"
```

### 2.2 Exécuter Tests Charge

```bash
#!/bin/bash
# run_load_tests.sh

# Définir variables
API_HOST="http://localhost:8000"
TEST_DURATION="5m"

echo "🚀 Démarrage tests de charge..."
echo ""

# Test 1: Normal
echo "📊 Test 1: Charge normale (50 users, 5 min)"
locust -f tests/locustfile.py \
    --headless \
    --users 50 \
    --spawn-rate 5 \
    --run-time $TEST_DURATION \
    --host $API_HOST \
    --csv results/normal_50_$(date +%s)

sleep 30

# Test 2: Moyenne
echo "📊 Test 2: Charge moyenne (100 users, 5 min)"
locust -f tests/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time $TEST_DURATION \
    --host $API_HOST \
    --csv results/medium_100_$(date +%s)

sleep 30

# Test 3: Élevée
echo "📊 Test 3: Charge élevée (200 users, 5 min)"
locust -f tests/locustfile.py \
    --headless \
    --users 200 \
    --spawn-rate 20 \
    --run-time $TEST_DURATION \
    --host $API_HOST \
    --csv results/high_200_$(date +%s)

echo "✅ Tests terminés!"
echo "Résultats: results/"
```

### 2.3 Analyse Résultats Load Tests

```python
#!/usr/bin/env python3
# analyze_load_tests.py

import pandas as pd
import glob
from pathlib import Path

def analyze_results():
    """Analyser résultats tests de charge"""
    
    results_dir = Path('tests/results')
    csv_files = glob.glob(str(results_dir / '*.csv'))
    
    print("📈 ANALYSE TESTS DE CHARGE")
    print("=" * 60)
    
    for csv_file in sorted(csv_files):
        print(f"\n📄 {Path(csv_file).name}")
        print("-" * 60)
        
        df = pd.read_csv(csv_file)
        
        # Stats clés
        print(f"Total Requests: {len(df)}")
        print(f"Failures: {df['Failure'].sum()}")
        print(f"Success Rate: {(1 - df['Failure'].mean()) * 100:.1f}%")
        
        # Response times
        print(f"\nResponse Times (ms):")
        print(f"  Min: {df['Response Time'].min():.0f}")
        print(f"  Mean: {df['Response Time'].mean():.0f}")
        print(f"  Max: {df['Response Time'].max():.0f}")
        print(f"  P95: {df['Response Time'].quantile(0.95):.0f}")
        print(f"  P99: {df['Response Time'].quantile(0.99):.0f}")
        
        # Status codes distribution
        print(f"\nStatus Codes:")
        status_dist = df['Status Code'].value_counts()
        for status, count in status_dist.items():
            pct = (count / len(df)) * 100
            print(f"  {status}: {count} ({pct:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ Analyse terminée")

if __name__ == "__main__":
    analyze_results()
```

---

## **PHASE 3 - Finalisation Flutter**

### 3.1 Generate Widgets Scaffold

```bash
#!/bin/bash
# flutter_widgets_generator.sh

cd mobile/patient_app

# Créer structure de base
mkdir -p lib/features/{auth,appointments,medical_history,lab_results,chat,notifications,dashboard}/{screens,widgets,providers}

# Générer fichiers auth
touch lib/features/auth/screens/{login_screen.dart,register_screen.dart,mfa_screen.dart}
touch lib/features/auth/widgets/login_form.dart
touch lib/features/auth/providers/auth_provider.dart

# Générer fichiers appointments
touch lib/features/appointments/screens/{appointments_list_screen.dart,appointment_detail_screen.dart,book_appointment_screen.dart}
touch lib/features/appointments/widgets/{appointment_card.dart,calendar_picker.dart,doctor_selector.dart}
touch lib/features/appointments/providers/appointments_provider.dart

# Générer fichiers medical_history
touch lib/features/medical_history/screens/{medical_history_screen.dart,consultation_detail_screen.dart}
touch lib/features/medical_history/widgets/medical_record_card.dart
touch lib/features/medical_history/providers/medical_history_provider.dart

# Générer fichiers lab_results
touch lib/features/lab_results/screens/{lab_results_screen.dart,result_detail_screen.dart}
touch lib/features/lab_results/widgets/result_card.dart
touch lib/features/lab_results/providers/lab_results_provider.dart

# Générer fichiers chat
touch lib/features/chat/screens/{chat_list_screen.dart,chat_detail_screen.dart}
touch lib/features/chat/widgets/{chat_bubble.dart,message_input.dart}
touch lib/features/chat/providers/chat_provider.dart

# Générer fichiers notifications
touch lib/features/notifications/screens/notifications_screen.dart
touch lib/features/notifications/widgets/notification_item.dart
touch lib/features/notifications/providers/notifications_provider.dart

# Générer fichiers dashboard
touch lib/features/dashboard/screens/dashboard_screen.dart
touch lib/features/dashboard/widgets/{quick_actions.dart,upcoming_appointments_card.dart,health_summary_card.dart}
touch lib/features/dashboard/providers/dashboard_provider.dart

echo "✅ Structure Flutter générée"
echo "Prochaine étape: Copier les fichiers de code depuis PLAN_100_PERCENT.md"
```

### 3.2 Pubspec Dependencies

```bash
#!/bin/bash
# flutter_dependencies.sh

cd mobile/patient_app

# Ajouter dépendances dans pubspec.yaml
flutter pub add flutter_riverpod riverpod_generator
flutter pub add dio shared_preferences
flutter pub add flutter_local_notifications
flutter pub add web_socket_channel
flutter pub add cached_network_image
flutter pub add intl
flutter pub add url_launcher
flutter pub add connectivity_plus

# Dev dependencies
flutter pub add --dev build_runner riverpod_generator

echo "✅ Dépendances ajoutées"
echo "Exécuter: flutter pub get"
```

### 3.3 Build & Test Flutter

```bash
#!/bin/bash
# flutter_build_test.sh

cd mobile/patient_app

# Analyser le code
flutter analyze

# Tester
flutter test

# Build Android
flutter build apk --release

# Build iOS (macOS uniquement)
# flutter build ios --release

echo "✅ Build Flutter complété"
echo "APK généré: build/app/outputs/apk/release/app-release.apk"
```

---

## **PHASE 4 - Configuration Complète**

### 4.1 Setup Prometheus Backend

```python
#!/usr/bin/env python3
# setup_prometheus.py

import os
from pathlib import Path

def create_prometheus_files():
    """Créer fichiers Prometheus configuration"""
    
    # prometheus.yml
    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/'
    scrape_interval: 10s
"""
    
    # alert_rules.yml
    alert_rules = """groups:
  - name: sghl_alerts
    rules:
      - alert: HighErrorRate
        expr: 'django_http_requests_total{status=~"5.."} > 10'
        for: 5m
"""
    
    # Créer répertoire monitoring
    Path('monitoring').mkdir(exist_ok=True)
    
    with open('monitoring/prometheus.yml', 'w') as f:
        f.write(prometheus_config)
    
    with open('monitoring/alert_rules.yml', 'w') as f:
        f.write(alert_rules)
    
    print("✅ Fichiers Prometheus créés")

if __name__ == "__main__":
    create_prometheus_files()
```

### 4.2 PDF Facture Test

```python
#!/usr/bin/env python3
# test_facture_pdf.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from facturation.models import Facture
from facturation.pdf_generator import FacturePDF

def test_pdf_generation():
    """Tester génération PDF facture"""
    
    # Récupérer première facture
    facture = Facture.objects.first()
    
    if not facture:
        print("❌ Aucune facture trouvée")
        return
    
    # Générer PDF
    pdf_bytes = FacturePDF.generate(facture)
    
    # Sauvegarder localement
    filename = f"facture_{facture.id}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ PDF généré: {filename}")

if __name__ == "__main__":
    test_pdf_generation()
```

### 4.3 HL7/FHIR Test

```python
#!/usr/bin/env python3
# test_fhir_export.py

import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from patients.models import Patient
from interoperabilite.fhir_converter import FHIRConverter

def test_fhir_export():
    """Tester export FHIR"""
    
    patient = Patient.objects.first()
    
    if not patient:
        print("❌ Aucun patient trouvé")
        return
    
    # Convertir en FHIR
    fhir_data = FHIRConverter.patient_to_fhir(patient)
    
    # Afficher JSON
    print("✅ Patient FHIR:")
    print(json.dumps(fhir_data, indent=2, default=str))

if __name__ == "__main__":
    test_fhir_export()
```

---

## **CI/CD - GitHub Actions Workflows**

### 4.4 Complete Workflow

```yaml
# .github/workflows/complete-pipeline.yml

name: Complete Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: sghl_test
          POSTGRES_USER: sghl_user
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: |
          cd backend
          pip install -r requirements.txt
          python manage.py migrate
          pytest tests/
      
      - run: |
          cd backend
          python manage.py test --keepdb

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - run: |
          cd frontend
          npm install
          npm run build
          npx playwright install
          npm run test:e2e
      
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/

  mobile-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.13.0'
      
      - run: |
          cd mobile/patient_app
          flutter pub get
          flutter test
          flutter test integration_test/

  load-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    needs: [backend-tests, frontend-tests]
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: |
          cd backend
          pip install -r requirements.txt
          pip install locust
          python manage.py migrate
          python manage.py runserver &
          sleep 5
          
          locust -f tests/locustfile.py \
            --headless \
            --users 50 \
            --spawn-rate 5 \
            --run-time 3m \
            --host http://localhost:8000
```

---

## **COMMANDES RAPIDES**

### Démarrer Stack Complète

```bash
#!/bin/bash
# start_all.sh

echo "🚀 Démarrage Stack Complète SGHL..."

# Backend
echo "Backend..."
cd backend
python manage.py migrate
python manage.py runserver &
BACKEND_PID=$!

# Frontend (dev)
echo "Frontend..."
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

# Mobile (optionnel)
# cd ../mobile/patient_app
# flutter run

# Monitoring
echo "Monitoring..."
cd ../../monitoring
docker-compose -f docker-compose.monitoring.yml up -d

echo ""
echo "✅ Stack démarrée!"
echo ""
echo "Endpoints:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo "Pour arrêter: kill $BACKEND_PID $FRONTEND_PID"
```

### Arrêter Stack

```bash
#!/bin/bash
# stop_all.sh

echo "⛔ Arrêt Stack..."

# Arrêter services Python
pkill -f "python manage.py"

# Arrêter services Node
pkill -f "npm run"

# Arrêter Docker
cd monitoring
docker-compose -f docker-compose.monitoring.yml down

echo "✅ Stack arrêtée"
```

### Vérifier Santé

```bash
#!/bin/bash
# health_check.sh

echo "🏥 HEALTH CHECK SGHL"
echo "=" * 60

# Backend
echo "Backend..."
curl -s http://localhost:8000/api/v1/health/ | python -m json.tool || echo "❌ Backend down"

# Frontend
echo "Frontend..."
curl -s http://localhost:5173 | head -1 || echo "❌ Frontend down"

# Prometheus
echo "Prometheus..."
curl -s http://localhost:9090/-/healthy | head -1 || echo "❌ Prometheus down"

# Grafana
echo "Grafana..."
curl -s http://localhost:3000/api/health | python -m json.tool || echo "❌ Grafana down"

# Redis
echo "Redis..."
redis-cli ping || echo "❌ Redis down"

# PostgreSQL
echo "PostgreSQL..."
psql -U sghl_user -d sghl_db -c "SELECT NOW();" || echo "❌ PostgreSQL down"

echo "=" * 60
echo "✅ Health check complété"
```

---

## **DOCUMENTATION SUPPLÉMENTAIRE**

### Checklist Déploiement Production

```markdown
## Pre-Production Checklist

### Sécurité
- [ ] SECRET_KEY configurée
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurés
- [ ] HTTPS obligatoire
- [ ] Certificats SSL valides
- [ ] Rate limiting actif
- [ ] MFA activé pour admins

### Performance
- [ ] Tests charge passés (< 2s)
- [ ] Cache Redis configuré
- [ ] DB indexes optimisés
- [ ] Static files compressés
- [ ] CDN configuré (optionnel)

### Monitoring
- [ ] Prometheus + Grafana actifs
- [ ] Alertes configurées
- [ ] Logs centralisés (ELK ou équivalent)
- [ ] Health check endpoints testés

### Backup & DR
- [ ] Backup automatique (quotidien)
- [ ] Backup externalisé (S3)
- [ ] Test restauration exécuté
- [ ] DRP documenté et testé
- [ ] RTO/RPO définis

### Tests
- [ ] E2E tests passés (Frontend/Mobile)
- [ ] Load tests validés
- [ ] Security tests exécutés
- [ ] UAT approuvée

### Documentation
- [ ] README.md à jour
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture diagram
- [ ] Runbook d'urgence
- [ ] Changelog versioning
```

---

**Tous les scripts et configurations sont prêts à l'emploi. Commencez par la Phase 1 !**