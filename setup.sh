#!/bin/bash
# ============================================================
# Script de démarrage SGHL — Développement local
# Usage: bash setup.sh
# ============================================================
set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║         SGHL — Système de Gestion Hospitalière       ║"
echo "║              Setup Développement Local               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Backend ──────────────────────────────────────────────────
echo "📦 Installation des dépendances backend..."
cd backend
python -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
pip install -r requirements.txt -q

echo "🗄️  Application des migrations..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput

echo "🌱 Initialisation des données de démonstration..."
python manage.py shell < fixtures/seed_data.py 2>/dev/null || echo "⚠️  Seed déjà effectué ou erreur ignorée"

echo "👤 Création du superuser admin (si inexistant)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sghl.local', 'Admin@2025!')
    print('✅ Superuser admin créé')
else:
    print('ℹ️  Superuser admin existe déjà')
" 2>/dev/null || true

cd ..

# ── Frontend ─────────────────────────────────────────────────
echo ""
echo "🎨 Installation des dépendances frontend..."
cd frontend
npm install --silent
cd ..

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                  ✅ Setup terminé !                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Backend  : cd backend && python manage.py runserver ║"
echo "║  Frontend : cd frontend && npm run dev               ║"
echo "║  Docker   : docker-compose up -d                     ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Admin    : admin / Admin@2025!                      ║"
echo "║  Médecin  : dr.camara / Medecin@2025!                ║"
echo "║  Biologiste: dr.diallo / Bio@2025!                   ║"
echo "║  Infirmier: inf.kouyate / Infirmier@2025!            ║"
echo "║  Pharmacien: pharmacien1 / Pharma@2025!              ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  API Docs : http://localhost:8000/api/v1/docs        ║"
echo "║  Frontend : http://localhost:5173                    ║"
echo "║  Health   : http://localhost:8000/api/v1/sante/      ║"
echo "╚══════════════════════════════════════════════════════╝"
