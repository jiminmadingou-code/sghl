# Déploiement SGHL - Guide Complet

## Prérequis

- Docker & Docker Compose
- Python 3.11+ (pour développement local)
- Node.js 18+ (pour développement frontend)
- PostgreSQL 15+ (ou utiliser Docker)
- Redis 7+ (ou utiliser Docker)

## 1. Installation Locale (Développement)

### Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Copier fichier d'environnement
cp .env.example .env
# Modifier .env avec vos paramètres

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer serveur
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Installer dépendances
npm install

# Lancer serveur de développement
npm run dev
```

### Mobile (Flutter)

```bash
cd mobile/patient_app

# Installer dépendances
flutter pub get

# Lancer l'application
flutter run
```

## 2. Déploiement Docker (Production)

### Configuration

```bash
# Racine du projet
cp .env.example .env
nano .env  # Modifier les variables sensibles
```

Variables critiques à modifier:
- `SECRET_KEY`
- `DB_PASSWORD`
- `GRAFANA_PASSWORD`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

### Lancer l'infrastructure

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### Avec monitoring (Prometheus + Grafana)

```bash
docker-compose --profile monitoring up -d
```

Accéder à:
- Grafana: http://localhost:3000 (admin/grafana_password)
- Prometheus: http://localhost:9090

## 3. Initialisation Base de Données

```bash
# Via Docker
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput

# Créer superuser
docker-compose exec backend python manage.py createsuperuser
```

## 4. Scripts Utiles

### Backup Base de Données

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U sghl_user sghl_db > backup_$(date +%Y%m%d).sql

# Restaurer
docker-compose exec -T postgres psql -U sghl_user sghl_db < backup_20240101.sql
```

### Backup Média

```bash
docker run --rm -v sghl_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d).tar.gz /data
```

### Nettoyage

```bash
# Supprimer conteneurs arrêtés
docker-compose down

# Supprimer volumes (ATTENTION: perte données!)
docker-compose down -v
```

## 5. Configuration Nginx

### SSL/TLS (Production)

```bash
# Générer certificat Let's Encrypt
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d votre-domaine.com

# Ou auto-générer pour test
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

## 6. Monitoring & Santé

### Health Check

```bash
curl http://localhost:8000/api/v1/dashboard/health
```

### KPIs Dashboard

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/dashboard/summary
```

### Logs Application

```bash
docker-compose logs backend
docker-compose logs -f backend  # En temps réel
```

## 7. Plan de Reprise Activité (DRP)

### Backup Automatique (Cron)

```bash
# /etc/cron.daily/sghl-backup
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec -T postgres pg_dump -U sghl_user sghl_db > /backups/db_$DATE.sql
docker run --rm -v sghl_media_volume:/data -v /backups:/backup alpine tar czf /backup/media_$DATE.tar.gz /data
```

### Restauration

```bash
# 1. Arrêter services
docker-compose down

# 2. Restaurer base
docker-compose exec -T postgres psql -U sghl_user sghl_db < db_backup.sql

# 3. Restaurer média
docker run --rm -v sghl_media_volume:/data -v $(pwd):/backup alpine tar xzf /backup/media_backup.tar.gz -C /

# 4. Redémarrer
docker-compose up -d
```

## 8. Tests de Charge

```bash
# Installer locust
pip install locust

# Lancer tests
locust -f load_test.py --host=http://localhost:8000
```

## 9. Sécurité Production

### Checklist

- [ ] SECRET_KEY unique et sécurisé
- [ ] DEBUG=False
- [ ] HTTPS obligatoire (Nginx)
- [ ] Base de données sur réseau privé
- [ ] Firewall configuré
- [ ] Rotation logs active
- [ ] Backup quotidien externalisé
- [ ] Mots de passe forts
- [ ] MFA activé pour admin
- [ ] Rate limiting configuré
- [ ] Certificates SSL renouvellement automatique

### Hardening

```bash
# Security headers (déjà dans settings.py)
SECURE_HSTS_SECONDS=31536000
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 10. URLs Produits Hébergés

Une fois déployé:

- **Frontend Web**: https://votre-domaine.com
- **Backend API**: https://votre-domaine.com/api/v1/
- **Admin Django**: https://votre-domaine.com/admin/
- **Grafana**: https://votre-domaine.com/grafana
- **Prometheus**: https://votre-domaine.com/prometheus

### Mobile App

- **Android APK**: https://votre-domaine.com/downloads/app.apk
- **iOS IPA**: https://votre-domaine.com/downloads/app.ipa

## 11. Résolution Problèmes

### Backend ne démarre pas

```bash
docker-compose logs backend
docker-compose exec backend python manage.py check
```

### Base de données non accessible

```bash
docker-compose exec postgres psql -U sghl_user -d sghl_db
```

### Redis non connecté

```bash
docker-compose exec redis redis-cli ping
```

### Permissions fichiers

```bash
docker-compose exec backend chown -R www-data:www-data /app/media /app/static
```

## 12. Support & Documentation

- **Documentation API**: http://localhost:8000/api/v1/docs/
- **Admin Interface**: http://localhost:8000/admin/
- **Issue Tracker**: [lien vers votre repo]

---

**Version**: 1.0.0
**Dernière mise à jour**: 2024
**Maintenu par**: NLP-Core-Team
