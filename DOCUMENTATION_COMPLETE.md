cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser# Documentation Complète du Système de Gestion Hospitalière et de Laboratoire (SGHL)

## 1. Vision et Objectifs du Produit

Le SGHL est un ERP médical full-stack intégré (Web & Mobile) conçu pour digitaliser l'intégralité du parcours patient, depuis l'admission jusqu'au suivi post-hospitalisation.

### Objectifs Clés
- **Traçabilité Complète :** Journal d'audit immuable pour toutes les actions.
- **Sécurité Bancaire :** Chiffrement AES-256, JWT avec rotation, MFA, RBAC strict.
- **Haute Disponibilité :** Architecture microservices-ready, Redis cache, backups externes.
- **Conformité :** Respect des bonnes pratiques de gouvernance des données de santé.

---

## 2. Architecture Technique

### Stack Technologique
| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Backend** | Python 3.x \| Django 4.2 \| Django Ninja | API REST typée (Pydantic), support async, performance |
| **Frontend Web** | Vue 3 (Composition API) \| Tailwind CSS \| Pinia | UX moderne, réactivité, maintenabilité |
| **Mobile** | Flutter (Cross-platform) | iOS/Android avec codebase unique, performances natives |
| **Base de Données** | PostgreSQL | Transactions ACID, indexation avancée, contraintes d'intégrité |
| **Cache/Session** | Redis | Performance, gestion des sessions, rate limiting |
| **Message Queue** | Channels + Redis | WebSockets pour chat et notifications temps réel |
| **Infrastructure** | Docker + Nginx | Conteneurisation, reverse proxy, load balancing |
| **Monitoring** | Prometheus + Grafana + ELK | Observabilité complète, logs structurés JSON |

### Sécurité
- **Authentification :** JWT Stateless avec rotation de Refresh Tokens.
- **MFA :** Authentification à deux facteurs (code SMS/Email).
- **Chiffrement :** AES-256 pour les données sensibles au repos.
- **Mots de passe :** Bcrypt avec politique de force stricte.
- **Protection API :** Rate limiting, anti-XSS, anti-CSRF, CSP headers.

---

## 3. Architecture Fonctionnelle

### A. Gestion Clinique & Hospitalisation

#### Cycle Consultation
- Diagnostic avec code **CIM-10** validé.
- Prescription électronique (e-ordonnance) avec signature numérique.
- Archivage sécurisé des documents (PDF/Imagerie) avec scan antivirus.

#### Logistique Hospitalière
- **Structure Hiérarchique :** Bâtiment > Service > Chambre > Lit.
- **Règle Métier :** 1 lit = 1 patient maximum (vérifié au niveau base de données).
- **Admission :** Conditionnée par la disponibilité réelle des lits.
- **Transferts :** Gestion des transferts inter-services avec historique.
- **Verrouillage Optimiste :** Champ `version` sur les hospitalisations pour éviter les conflits.

#### Soins & Infirmerie
- Planification des soins synchronisée avec les prescriptions.
- Saisie des constantes vitales avec visualisation graphique.
- Alertes automatiques pour doses omises.

### B. Laboratory Information System (LIS)

#### Workflow Structuré
1. **Commande** → 2. **Prélèvement** → 3. **Affectation** → 4. **Saisie Résultats** → 5. **Validation** → 6. **Publication**

#### Contraintes de Sécurité
- **Validation Exclusive :** Seul un profil **Biologiste** peut valider un examen.
- **Immuabilité :** Un résultat validé ne peut plus être modifié (champ `resultat_immutable`).
- **Audit Trail :** Log obligatoire sur toute modification avant validation.
- **PDF Signé :** Génération automatique de comptes-rendus PDF signés électroniquement.

#### Stockage
- Chiffrement des documents.
- Contrôle MIME type et taille maximale.
- Scan antivirus automatisé (ClamAV ou équivalent).

### C. Logistique & Finances

#### Pharmacie
- Gestion des inventaires par **Lots** avec suivi des péremptions.
- Décrémentation automatique des stocks lors de la validation des prescriptions.
- Alertes de rupture de stock et alertes de péremption (90 jours).
- Historique complet des mouvements (Entrée/Sortie/Ajustement).

#### Facturation
- Moteur de calcul automatisé (Actes, nuitées, examens, médicaments).
- Gestion du **tiers-payant** (Assurances).
- Paiements partiels ou échelonnés.
- Génération de factures PDF.
- Journal comptable immuable.

### D. Gestion RH & Pilotage

#### RBAC (Role-Based Access Control)
- Matrice de permissions stricte par profil (Patient, Médecin, Infirmier, Biologiste, Pharmacien, Caissier, Admin).
- Séparation des privilèges sensibles.
- Middleware RBAC pour vérifier les permissions à chaque requête.

#### Planning de Garde
- Attribution des plages horaires par personnel.
- Visualisation calendrier.

#### Dashboard Administratif
- KPIs en temps réel (Taux d'occupation, recettes, examens en attente).
- Statistiques dynamiques via Redis cache.

---

## 4. Application Mobile Patient (Flutter)

L'application mobile repose sur trois axes :

### Self-Service
- **Prise de RDV :** Via calendrier synchronisé aux disponibilités des médecins.
- **Notifications :** Confirmation par email et notifications push.
- **Chat :** Environnement de conversation en temps réel avec les médecins (WebSockets).

### Transparence
- **Historique Médical :** Consultation sécurisée de l'historique.
- **Résultats :** Téléchargement des résultats PDF signés.
- **Soins :** Visualisation du plan de soins et des constantes.

### Observance
- **Rappels :** Notifications push pour les prises médicamenteuses.
- **Suivi :** Suivi post-opératoire.
- **Alertes :** Rendez-vous à venir.

---

## 5. Règles Métier Critiques & Sécurité

### Cohérence
- Tout traitement hospitalier dépend d'une **hospitalisation active**.
- Les prescriptions sont verrouillées dès validation.

### Immuabilité
- Les logs d'audit ne peuvent ni être modifiés ni supprimés (`save()` et `delete()` surchargés).
- Les résultats de laboratoire validés sont immuables.

### Audit Trail (Livre-journal)
- Log immuable contenant : User, Timestamp, IP, Old Value, New Value, Action Type.
- Logs structurés en JSON pour ingestion ELK.

### Protection
- Middlewares anti-XSS, CSRF, protection injection SQL.
- Validation stricte des schémas API via Pydantic.
- Rate Limiting contre le brute-force.
- Rotation des clés JWT et politique de mots de passe forte.

---

## 6. Exigences Non-Fonctionnelles (QoS)

### Performance
- Temps de réponse API < 2 secondes.
- Pagination obligatoire sur toutes les listes.
- Indexation PostgreSQL optimisée sur les champs de requête fréquents.

### Disponibilité
- Backup quotidien externalisé (S3 ou équivalent).
- Plan de Reprise d'Activité (DRP) documenté.
- Tests de restauration trimestriels.

### Observabilité
- Monitoring applicatif et alerting en temps réel (Prometheus/Grafana).
- Logs centralisés (ELK Stack).

### Accessibilité
- Interface Responsive conforme WCAG 2.1.

### Évolutivité
- Conception compatible HL7 / FHIR pour l'interopérabilité.
- APIs assurances tierces prêtes à être intégrées.

---

## 7. Qualité & Tests

### Couverture de Tests
- **Backend :** Tests unitaires et d'intégration (Pytest), tests de charge (Locust).
- **Frontend & Mobile :** Tests composants, tests E2E.
- **Sécurité :** Tests d'intrusion périodiques.
- **Validation :** Phase UAT avant chaque déploiement.

### Politique de Versioning
- Releases versionnées et documentées.
- Versioning API (`/api/v1/`).

---

## 8. Gouvernance & Cycle de Vie des Données

### Conservation
- Politique de conservation des dossiers médicaux conforme à la législation en vigueur.
- Archivage longue durée sécurisé.

### Consentement
- Gestion du consentement patient (opt-in/opt-out).
- Traçabilité des accès aux dossiers sensibles.

### Anonymisation
- Anonymisation des données pour usage analytique et statistique.

---

## 9. Structure du Projet

```
sghl/
├── backend/              # Django + Django Ninja
│   ├── audit/            # Logs immuables
│   ├── patients/         # Gestion patients
│   ├── hospitalisations/ # Logistique lits/chambres
│   ├── laboratoire/      # LIS workflow
│   ├── pharmacie/        # Gestion stocks
│   ├── facturation/      # Factures & paiements
│   ├── personnel/        # RH & Planning
│   ├── soins/            # Soins infirmiers
│   ├── dashboard/        # KPIs
│   ├── chat/             # Messagerie temps réel
│   ├── rendez_vous/      # Gestion RDV
│   ├── prescriptions/    # E-ordonnances
│   ├── consentement/     # Gestion consentements
│   ├── core/             # Config, Sécurité, Middleware
│   └── tests/            # Tests Pytest
├── frontend/             # Vue 3 + Tailwind
├── mobile/               # Flutter
├── monitoring/           # Prometheus + Grafana
├── nginx/                # Configuration reverse proxy
└── docs/                 # Documentation
```

---

## 10. Déploiement

### Environnements
- **Dev :** Docker Compose local.
- **Staging :** Environnement miroir de la production.
- **Production :** Serveurs dédiés avec HTTPS obligatoire.

### CI/CD
- GitHub Actions / GitLab CI pour les tests et le déploiement automatique.
- Gestion multi-environnements via variables d'environnement.

---

*Document généré pour le projet SGHL - Système de Gestion Hospitalière et de Laboratoire*