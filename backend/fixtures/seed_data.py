"""
Script de seed pour initialiser les données de démonstration du SGHL.
Usage: python manage.py shell < fixtures/seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.contrib.auth.models import User
from personnel.models import Personnel
from patients.models import Patient
from hospitalisations.models import Batiment, Service, Chambre, Lit
from pharmacie.models import Medicament, LotMedicament
from laboratoire.models import ExamenLaboratoire
from soins.models import TypeSoin
from gardes.models import TypeGarde
from imagerie.models import Modalite
from bloc_operatoire.models import SalleOperation
from datetime import date, timedelta
from django.utils import timezone

print("🌱 Initialisation des données SGHL...")

# ── Superuser admin ──────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@sghl.local', 'Admin@2025!')
    Personnel.objects.create(user=admin_user, role='Admin', service='Direction')
    print("✅ Admin créé: admin / Admin@2025!")

# ── Personnel médical ────────────────────────────────────────────
staff = [
    ('dr.camara',    'Alpha',     'Camara',    'Médecin',       'Médecine interne', 'Medecin@2025!'),
    ('dr.bah',       'Mariama',   'Bah',       'Médecin',       'Cardiologie',      'Medecin@2025!'),
    ('dr.diallo',    'Oumar',     'Diallo',    'Biologiste',    'Laboratoire',      'Bio@2025!'),
    ('inf.kouyate',  'Ibrahima',  'Kouyaté',   'Infirmier',     'Urgences',         'Infirmier@2025!'),
    ('pharmacien1',  'Kadiatou',  'Sylla',     'Pharmacien',    'Pharmacie',        'Pharma@2025!'),
    ('caissier1',    'Moussa',    'Traoré',    'Caissier',      'Facturation',      'Caissier@2025!'),
    ('dr.kouyate',   'Sekou',     'Kouyaté',   'Médecin',       'Chirurgie',        'Medecin@2025!'),
    ('sf.diallo',    'Fatoumata', 'Diallo',    'Infirmier',     'Maternité',        'Infirmier@2025!'),
]
for username, first, last, role, service, pwd in staff:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username, f'{username}@sghl.local', pwd, first_name=first, last_name=last)
        Personnel.objects.create(user=u, role=role, service=service)
print(f"✅ {len(staff)} membres du personnel créés")

# ── Patients ─────────────────────────────────────────────────────
patients_data = [
    ('Mamadou', 'Diallo',   date(1979, 3, 15),  'M', '620000001', 'A+'),
    ('Fatoumata','Koné',    date(1992, 7, 22),  'F', '621000002', 'O+'),
    ('Ibrahim', 'Traoré',   date(1957, 11, 8),  'M', '622000003', 'B-'),
    ('Aissatou','Bah',      date(1996, 1, 30),  'F', '623000004', 'AB+'),
    ('Sekou',   'Camara',   date(1970, 5, 12),  'M', '624000005', 'O-'),
    ('Oumou',   'Sylla',    date(1988, 9, 3),   'F', '625000006', 'A-'),
    ('Mariama', 'Barry',    date(2001, 4, 18),  'F', '626000007', 'B+'),
    ('Oumar',   'Baldé',    date(1965, 12, 25), 'M', '627000008', 'AB-'),
]
for prenom, nom, ddn, sexe, tel, gs in patients_data:
    if not Patient.objects.filter(nom=nom, prenom=prenom).exists():
        Patient.objects.create(prenom=prenom, nom=nom, date_naissance=ddn, sexe=sexe, telephone=tel, groupe_sanguin=gs)
print(f"✅ {len(patients_data)} patients créés")

# ── Structure hospitalière ────────────────────────────────────────
if not Batiment.objects.exists():
    bat_a = Batiment.objects.create(code='BAT-A', nom='Bâtiment Principal', nombre_etages=4)
    bat_b = Batiment.objects.create(code='BAT-B', nom='Bâtiment Maternité', nombre_etages=2)
    bat_c = Batiment.objects.create(code='BAT-C', nom='Bâtiment Urgences', nombre_etages=1)

    services_data = [
        (bat_a, 'MED-INT', 'Médecine Interne', 30),
        (bat_a, 'CARDIO',  'Cardiologie',       20),
        (bat_a, 'CHIR',    'Chirurgie',         20),
        (bat_a, 'PEDIATR', 'Pédiatrie',         15),
        (bat_b, 'MATERN',  'Maternité',         25),
        (bat_c, 'URG',     'Urgences',          10),
    ]
    for bat, code, nom, nb_lits in services_data:
        svc = Service.objects.create(batiment=bat, code=code, nom=nom)
        for i in range(1, min(4, nb_lits // 4) + 1):
            ch = Chambre.objects.create(service=svc, numero=f'C-{code[:3]}-{i:02d}', tarif_nuitee=50000)
            for j in range(1, 5):
                Lit.objects.create(chambre=ch, numero_lit=f'L-{j:02d}')
    print("✅ Structure hospitalière créée (bâtiments, services, chambres, lits)")

# ── Médicaments ───────────────────────────────────────────────────
meds_data = [
    ('Artémether 80mg',    'Antipaludéen',      'comprimé', 50),
    ('Amlodipine 5mg',     'Antihypertenseur',  'comprimé', 50),
    ('Metformine 500mg',   'Antidiabétique',    'comprimé', 40),
    ('Amoxicilline 500mg', 'Antibiotique',      'gélule',   30),
    ('Paracétamol 500mg',  'Analgésique',       'comprimé', 100),
    ('Ibuprofène 400mg',   'Anti-inflammatoire','comprimé', 60),
    ('Furosémide 40mg',    'Diurétique',        'comprimé', 30),
    ('Oméprazole 20mg',    'IPP',               'gélule',   40),
    ('Amiodarone 200mg',   'Antiarythmique',    'comprimé', 20),
    ('Insuline Rapide',    'Antidiabétique',    'flacon',   15),
]
for nom, cat, unite, seuil in meds_data:
    med, created = Medicament.objects.get_or_create(nom=nom, defaults={'categorie': cat, 'unite': unite, 'seuil_alerte': seuil})
    if created:
        LotMedicament.objects.create(
            medicament=med, numero_lot=f'LOT-2025-{Medicament.objects.count():03d}',
            quantite=seuil * 4, date_peremption=date.today() + timedelta(days=365)
        )
print(f"✅ {len(meds_data)} médicaments créés avec stocks")

# ── Types de soins ────────────────────────────────────────────────
soins_types = [
    ('MED-ORAL',  'Administration médicament oral',    15, 'Médicament'),
    ('MED-IV',    'Perfusion intraveineuse',            30, 'Médicament'),
    ('PANSEMENT', 'Changement de pansement',            20, 'Soins'),
    ('CONSTANTES','Prise des constantes vitales',       10, 'Surveillance'),
    ('INJECTION', 'Injection sous-cutanée',             10, 'Médicament'),
    ('SONDE',     'Pose/retrait sonde urinaire',        20, 'Soins'),
    ('KINE',      'Kinésithérapie respiratoire',        30, 'Rééducation'),
]
for code, nom, duree, cat in soins_types:
    TypeSoin.objects.get_or_create(code=code, defaults={'nom': nom, 'duree_estimee_minutes': duree, 'categorie': cat})
print(f"✅ {len(soins_types)} types de soins créés")

# ── Types de gardes ───────────────────────────────────────────────
gardes_types = [
    ('Garde de nuit',    12, 1.5),
    ('Garde de jour',     8, 1.0),
    ('Astreinte',        24, 0.5),
    ('Garde week-end',   12, 1.3),
]
for nom, duree, coef in gardes_types:
    TypeGarde.objects.get_or_create(nom=nom, defaults={'duree_heures': duree, 'coefficient_paiement': coef})
print(f"✅ {len(gardes_types)} types de gardes créés")

# ── Modalités imagerie ────────────────────────────────────────────
modalites = [
    ('RX',   'Radiographie standard'),
    ('SCAN', 'Scanner (TDM)'),
    ('IRM',  'Imagerie par Résonance Magnétique'),
    ('ECHO', 'Échographie'),
    ('MAMMO','Mammographie'),
    ('SCINT','Scintigraphie'),
    ('PET',  'PET-Scan'),
]
for code, nom in modalites:
    Modalite.objects.get_or_create(code=code, defaults={'nom': nom})
print(f"✅ {len(modalites)} modalités d'imagerie créées")

# ── Salles d'opération ────────────────────────────────────────────
if not SalleOperation.objects.exists():
    svc_chir = Service.objects.filter(code='CHIR').first()
    if svc_chir:
        for i, nom in enumerate(['Bloc A', 'Bloc B', 'Bloc C', 'Bloc D'], 1):
            SalleOperation.objects.create(code=f'BLOC-{i:02d}', nom=nom, service=svc_chir)
        print("✅ 4 salles d'opération créées")

print("\n🎉 Seed terminé avec succès!")
print("=" * 50)
print("Comptes de connexion:")
print("  admin       / Admin@2025!")
print("  dr.camara   / Medecin@2025!")
print("  dr.diallo   / Bio@2025!")
print("  inf.kouyate / Infirmier@2025!")
print("  pharmacien1 / Pharma@2025!")
print("=" * 50)
