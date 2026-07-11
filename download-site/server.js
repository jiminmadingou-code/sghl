const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

// Téléchargement APK avec headers corrects
app.get('/download/sghl.apk', (req, res) => {
  const apkPath = path.join(__dirname, 'public', 'sghl.apk');
  if (!fs.existsSync(apkPath)) {
    return res.status(404).send('APK non disponible pour le moment.');
  }
  res.setHeader('Content-Type', 'application/vnd.android.package-archive');
  res.setHeader('Content-Disposition', 'attachment; filename="SGHL-Patient.apk"');
  res.download(apkPath, 'SGHL-Patient.apk');
});

app.listen(PORT, () => console.log(`Download site running on port ${PORT}`));
