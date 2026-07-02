# Checklist de Déploiement - SGHL

## 📋 Pré-Déploiement

### 1. Configuration Infrastructure

- [ ] Domaine DNS configuré (A record pointant vers serveur)
- [ ] Certificat SSL obtenu (Let's Encrypt ou commercial)
- [ ] Firewall configuré (ports 80, 443 ouverts)
- [ ] Backups externalisés configurés (S3, etc.)
- [ ] Monitoring configuré (Grafana, Prometheus)

### 2. Variables d'Environnement

- [ ] SECRET_KEY générée et sécurisée
- [ ] DB_PASSWORD sécurisé et fort
- [ ] REDIS_PASSWORD configuré
- [ ] EMAIL credentials configurés
- [ ] AWS credentials pour backups
- [ ] GRAFANA_ADMIN_PASSWORD changé
- [ ] ALLOWED_HOSTS configuré avec le domaine
- [ ] CORS_ALLOWED_ORIGINS configuré

### 3. Base de Données

- [ ] PostgreSQL 15+ installé/configuré
- [ ] Base de données créée
- [ ] Utilisateur DB créé avec permissions
- [ ] Connexion testée
- [ ] Backup automatique configuré
- [ ] Rétention backups définie (30 jours min)

### 4. Sécurité

- [ ] DEBUG=False dans .env
- [ ] SECRET_KEY unique et longue (50+ caractères)
- [ ] Tous les mots de passe changés
- [ ] HTTPS forcé (HSTS)
- [ ] Rate limiting activé
- [ ] CORS configuré strictement
- [ ] Headers de sécurité configurés
- [ ] Firewall configuré
- [ ] SSH sécurisé (clé seulement)
- [ ] Fail2ban installé (optionnel)

### 5. Performance

- [ ] Redis configuré et connecté
- [ ] Cache activé
- [ ] Gzip compressions activé
- [ ] Static files collectés
- [ ] Database indices créés
- [ ] Connection pooling configuré

## 🔧 Installation

### 1. Cloner et Configurer

```bash
# Cloner le repository
git clone <repository-url>
cd sghl

# Copier et éditer .env
cp .env.example .env
nano .env  # Modifier toutes les variables
```

**Vérifications:**
- [ ] .env créé
- [ ] Toutes variables modifiées
- [ ] Pas de valeurs par défaut

### 2. Build Docker

```bash
# Build des images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
```

**Vérifications:**
- [ ] Build réussi sans erreurs
- [ ] Images créées
- [ ] Taille images raisonnable

### 3. Migrations et Initialisation

```bash
# Migrations
docker-compose exec backend python manage.py migrate

# Collect static
docker-compose exec backend python manage.py collectstatic --noinput

# Créer superutilisateur
docker-compose exec backend python manage.py createsuperuser
```

**Vérifications:**
- [ ] Migrations appliquées
- [ ] Static files collectés
- [ ] Superutilisateur créé

### 4. Démarrage Services

```bash
# Démarrer tous les services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Vérifier les services
docker-compose ps
```

**Vérifications:**
- [ ] Tous les services UP
- [ ] Pas de erreurs dans les logs
- [ ] Health checks passing

## ✅ Tests Post-Déploiement

### 1. Tests Fonctionnels

- [ ] Frontend accessible (https://votre-domaine.com)
- [ ] Backend API accessible (https://votre-domaine.com/api/v1/)
- [ ] Admin Django accessible (https://votre-domaine.com/admin/)
- [ ] Login fonctionne
- [ ] CRUD patients fonctionne
- [ ] CRUD hospitalisations fonctionne
- [ ] CRUD laboratoire fonctionne
- [ ] CRUD pharmacie fonctionne
- [ ] Facturation fonctionne
- [ ] Chat WebSocket fonctionne
- [ ] Notifications email fonctionnent

### 2. Tests API

```bash
# Test health check
curl -I https://votre-domaine.com/api/v1/dashboard/health

# Test authentification
curl -X POST https://votre-domaine.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

**Vérifications:**
- [ ] Health check retourne 200
- [ ] Authentification fonctionne
- [ ] JWT tokens générés
- [ ] Rate limiting activé

### 3. Tests Sécurité

- [ ] HTTPS fonctionne (pas de HTTP)
- [ ] Certificat SSL valide
- [ ] Headers de sécurité présents:
  - [ ] Strict-Transport-Security
  - [ ] X-Content-Type-Options
  - [ ] X-Frame-Options
  - [ ] X-XSS-Protection
  - [ ] Content-Security-Policy
- [ ] CORS configuré correctement
- [ ] Pas d'erreurs de sécurité dans logs

### 4. Tests Performance

```bash
# Test temps de réponse
curl -w "@curl-format.txt" -o /dev/null -s https://votre-domaine.com/api/v1/dashboard/summary
```

**Vérifications:**
- [ ] API response time < 2s
- [ ] Frontend load time < 3s
- [ ] Database queries optimisées
- [ ] Cache Redis fonctionnel
- [ ] Pas de memory leaks

### 5. Tests Monitoring

- [ ] Grafana accessible (https://votre-domaine.com:3000)
- [ ] Prometheus accessible (https://votre-domaine.com:9090)
- [ ] Dashboards Grafana chargés
- [ ] Métriques collectées
- [ ] Alertes configurées
- [ ] Logs centralisés

### 6. Tests Backup

```bash
# Lancer un backup manuel
docker-compose exec backup-worker /app/scripts/backup_daily.sh

# Vérifier le backup
docker-compose exec backup-worker ls -lh /backup/
```

**Vérifications:**
- [ ] Backup généré
- [ ] Backup chiffré
- [ ] Upload S3 réussi (si configuré)
- [ ] Checksum calculé
- [ ] Cleanup anciens backups fonctionne

## 📊 Monitoring Continu

### 1. Logs

```bash
# Voir les logs
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

**À surveiller:**
- [ ] Erreurs 5xx
- [ ] Timeouts
- [ ] Connexions DB échouées
- [ ] Memory usage élevé
- [ ] Disk usage > 80%

### 2. Métriques Grafana

**Dashboards à monitorer:**
- [ ] Système (CPU, RAM, Disk)
- [ ] Application (API response time, Error rate)
- [ ] Database (Connections, Queries/s)
- [ ] Redis (Memory, Commands/s)
- [ ] Users (Actifs, Nouveaux)

**Alertes configurées:**
- [ ] API response time > 2s
- [ ] Error rate > 1%
- [ ] Disk usage > 80%
- [ ] Database connections > 90%
- [ ] Redis memory > 80%

### 3. Backups

**À vérifier quotidiennement:**
- [ ] Backup réussi la veille
- [ ] Taille backup normale
- [ ] Upload cloud réussi
- [ ] Pas d'erreurs dans logs backup

**À vérifier hebdomadairement:**
- [ ] Test de restauration réussi
- [ ] Intégrité des backups vérifiée
- [ ] Rétention respectée

## 🚨 Plan de Reprise

### 1. Documentation

- [ ] Procédure restauration documentée
- [ ] Contacts urgences listés
- [ ] Documentation technique accessible
- [ ] Runbook d'incident créé

### 2. Contacts

- [ ] Admin système
- [ ] Admin base de données
- [ ] Support hébergement
- [ ] Équipe développement

### 3. Procédures d'Urgence

**Si site down:**
1. Vérifier docker-compose ps
2. Voir logs: docker-compose logs backend
3. Vérifier health check
4. Redémarrer services si nécessaire
5. Contacter support si problème persiste

**Si DB down:**
1. Vérifier postgres container
2. Vérifier espace disque
3. Restaurer depuis backup si corrompue
4. Contacter DBA

**Si sécurité compromise:**
1. Isoler le serveur
2. Changer tous les mots de passe
3. Révoquer tokens JWT
4. Auditer les logs
5. Restaurer depuis backup propre

## 📝 Maintenance Régulière

### Quotidien
- [ ] Vérifier logs d'erreurs
- [ ] Vérifier backups réussis
- [ ] Monitorer métriques critiques

### Hebdomadaire
- [ ] Test de restauration
- [ ] Review des logs de sécurité
- [ ] Update dépendances (si critiques)

### Mensuel
- [ ] Update système et packages
- [ ] Review et nettoyage logs
- [ ] Vérifier certificats SSL
- [ ] Review permissions
- [ ] Audit de sécurité

### Trimestriel
- [ ] Tests de charge complets
- [ ] Audit de sécurité complet
- [ ] Plan de reprise testé
- [ ] Documentation mise à jour

## 🎯 KPIs de Production

| Métrique | Cible | Alert |
|----------|-------|-------|
| Uptime | 99.9% | < 99.5% |
| API Response Time | < 2s | > 3s |
| Error Rate | < 0.1% | > 1% |
| Backup Success Rate | 100% | < 99% |
| DB Connections | < 80% | > 90% |
| Disk Usage | < 70% | > 85% |

## ✅ Validation Finale

- [ ] Tous les tests fonctionnels passés
- [ ] Tous les tests de sécurité passés
- [ ] Monitoring configuré et fonctionnel
- [ ] Backups testés et validés
- [ ] Documentation mise à jour
- [ ] Équipe formée
- [ ] Plan de reprise validé
- [ ] Support configuré

---

**Déployé par:** ________________  
**Date:** ________________  
**Validé par:** ________________  

**Signature:**

---

*Document à mettre à jour à chaque changement d'infrastructure*
