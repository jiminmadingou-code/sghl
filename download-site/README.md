# SGHL Download Site — Guide Sideloading

Site web hébergé sur Railway qui permet aux patients de télécharger l'APK Android directement.

---

## Structure

```
download-site/
├── public/
│   ├── index.html      ← Landing page (design violet premium)
│   └── sghl.apk        ← APK généré (NON commité sur git, à uploader manuellement)
├── server.js           ← Serveur Express
├── package.json
├── Procfile            ← Pour Railway
├── build_and_copy_apk.bat  ← Script de build APK Windows
└── README.md
```

---

## Étape 1 — Générer l'APK

### Option A : Script automatique (Windows)
```bat
cd download-site
build_and_copy_apk.bat
```

### Option B : Commande manuelle
```bash
cd mobile/patient_app
flutter build apk --release --no-tree-shake-icons
# L'APK est dans : build/app/outputs/flutter-apk/app-release.apk
copy build\app\outputs\flutter-apk\app-release.apk ..\..\download-site\public\sghl.apk
```

---

## Étape 2 — Déployer sur Railway

### Première fois
1. Aller sur [railway.app](https://railway.app)
2. **New Project → Deploy from GitHub repo**
3. Sélectionner le repo `sghl`
4. Choisir le dossier **Root Directory** : `download-site`
5. Railway détecte automatiquement Node.js via `package.json`
6. Cliquer **Deploy**

### Variables d'environnement Railway (optionnel)
Aucune variable requise. Le port est géré automatiquement via `process.env.PORT`.

---

## Étape 3 — Uploader l'APK sur Railway

L'APK est dans `.gitignore` (trop lourd pour git). Il faut l'uploader via :

### Option A : Railway Volume (recommandé)
1. Dans Railway → ton service download-site → **Volumes**
2. Créer un volume monté sur `/app/public`
3. Uploader `sghl.apk` via Railway CLI :
```bash
npm install -g @railway/cli
railway login
railway up
```

### Option B : Inclure l'APK dans le repo (si < 100MB)
Retirer `public/sghl.apk` du `.gitignore` :
```bash
# Dans download-site/.gitignore, supprimer la ligne : public/sghl.apk
git add download-site/public/sghl.apk
git commit -m "feat: add release APK v1.0.0"
git push origin main
```
Railway redéploie automatiquement.

### Option C : Héberger l'APK sur un CDN externe
Modifier `server.js` pour rediriger vers une URL externe (GitHub Releases, S3, etc.) :
```js
app.get('/download/sghl.apk', (req, res) => {
  res.redirect('https://github.com/ton-org/sghl/releases/download/v1.0.0/sghl.apk');
});
```

---

## Étape 4 — Partager le lien

Une fois déployé, Railway donne une URL du type :
```
https://sghl-download.up.railway.app
```

Partager ce lien aux patients. Ils arrivent sur la landing page et cliquent **Télécharger l'APK**.

---

## Mise à jour de l'APK

Pour chaque nouvelle version :
1. Modifier `version` dans `mobile/patient_app/pubspec.yaml` (ex: `1.0.1+2`)
2. Relancer `build_and_copy_apk.bat`
3. `git add download-site/public/sghl.apk && git commit -m "release: v1.0.1" && git push`
4. Railway redéploie automatiquement ✅

---

## URL finale attendue

| Service       | URL Railway                                      |
|---------------|--------------------------------------------------|
| Backend API   | https://sghl-production.up.railway.app/api/v1    |
| Frontend Web  | https://sghl-frontend.up.railway.app             |
| Download APK  | https://sghl-download.up.railway.app             |
