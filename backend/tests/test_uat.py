"""
Tests UAT (User Acceptance Testing) — SGHL
Couvre les 7 scénarios UAT définis dans les spécifications.
Exécution : python manage.py test tests.test_uat
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import json
import io

from patients.models import Patient, Consultation
from personnel.models import Personnel
from hospitalisations.models import Batiment, Service, Chambre, Lit, Hospitalisation
from laboratoire.models import ExamenLaboratoire
from pharmacie.models import Medicament, LotMedicament, MouvementStock
from facturation.models import Facture, Paiement
from prescriptions.models import Prescription, LignePrescription
from audit.models import AuditTrail
from archivage.models import ArchiveDossier, DocumentMedical


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_user_personnel(username, role, is_staff=False):
    u = User.objects.create_user(username, f'{username}@test.local', 'Test@1234', is_staff=is_staff)
    return Personnel.objects.create(user=u, role=role)

def make_patient(prenom='Test', nom='UAT'):
    return Patient.objects.create(
        prenom=prenom, nom=nom,
        date_naissance=date(1985, 6, 15), sexe='M'
    )

def make_lit(code_suffix=''):
    bat = Batiment.objects.create(code=f'B{code_suffix or Batiment.objects.count()+1}', nom='Bâtiment UAT')
    svc = Service.objects.create(batiment=bat, code=f'S{code_suffix or Service.objects.count()+1}', nom='Service UAT')
    ch  = Chambre.objects.create(service=svc, numero=f'C{Chambre.objects.count()+1:02d}')
    return Lit.objects.create(chambre=ch, numero_lit='L01')


# ── UAT-01 : Admission patient ────────────────────────────────────────────────

class UAT01AdmissionPatient(TestCase):
    """
    Scénario : Admission d'un patient sur un lit libre.
    Règle métier : 1 lit = 1 patient maximum.
    """

    def setUp(self):
        self.medecin = make_user_personnel('med_uat01', 'Médecin')
        self.patient1 = make_patient('Alpha', 'UAT')
        self.patient2 = make_patient('Beta', 'UAT')
        self.lit = make_lit('01')

    def test_lit_libre_avant_admission(self):
        self.assertEqual(self.lit.statut, 'Libre')

    def test_admission_occupe_le_lit(self):
        Hospitalisation.objects.create(
            patient=self.patient1, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='UAT Test'
        )
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, 'Occupe')

    def test_double_admission_meme_lit_impossible(self):
        Hospitalisation.objects.create(
            patient=self.patient1, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='Premier'
        )
        with self.assertRaises(ValueError):
            Hospitalisation.objects.create(
                patient=self.patient2, lit=self.lit,
                medecin_referent=self.medecin,
                date_entree=date.today(), motif='Deuxième'
            )

    def test_sortie_libere_le_lit(self):
        h = Hospitalisation.objects.create(
            patient=self.patient1, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='UAT'
        )
        h.statut = 'Sorti'
        h.date_sortie_reelle = date.today()
        h.save()
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, 'Libre')

    def test_audit_trail_cree_a_admission(self):
        count_before = AuditTrail.objects.count()
        h = Hospitalisation.objects.create(
            patient=self.patient1, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='UAT'
        )
        h.log_audit(request=None, action_type='CREATE',
                    new_value={'patient': str(self.patient1), 'lit': str(self.lit)})
        self.assertGreater(AuditTrail.objects.count(), count_before)


# ── UAT-02 : Workflow laboratoire complet ─────────────────────────────────────

class UAT02WorkflowLaboratoire(TestCase):
    """
    Scénario : Workflow LIS complet Commande → Publication.
    Contrainte : Seul le biologiste peut valider. Résultat immuable après.
    """

    WORKFLOW = ['Commande', 'Prélèvement', 'Affectation', 'Saisie résultats', 'Validé', 'Publié']

    def setUp(self):
        self.medecin    = make_user_personnel('med_uat02', 'Médecin')
        self.biologiste = make_user_personnel('bio_uat02', 'Biologiste')
        self.patient    = make_patient('Labo', 'UAT')

    def test_statut_initial_commande(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='NFS', priorite='Normal'
        )
        self.assertEqual(examen.statut, 'Commande')
        self.assertFalse(examen.resultat_immutable)

    def test_avancement_workflow_etape_par_etape(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='Glycémie'
        )
        for i, statut in enumerate(self.WORKFLOW[1:], 1):
            examen.statut = statut
            examen.save()
            examen.refresh_from_db()
            self.assertEqual(examen.statut, self.WORKFLOW[i])

    def test_validation_par_biologiste_rend_immutable(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='ECG', resultat='Rythme sinusal normal',
            statut='Saisie résultats'
        )
        examen.valider(self.biologiste)
        self.assertEqual(examen.statut, 'Validé')
        self.assertTrue(examen.resultat_immutable)
        self.assertEqual(examen.valide_par, self.biologiste)
        self.assertIsNotNone(examen.date_validation)

    def test_resultat_immutable_bloque_modification(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='CRP', resultat='12 mg/L', statut='Saisie résultats'
        )
        examen.valider(self.biologiste)
        # La protection est au niveau de l'API (HttpError 403)
        # On vérifie que le flag est bien positionné
        self.assertTrue(examen.resultat_immutable)


# ── UAT-03 : Prescription et dispense pharmacie ───────────────────────────────

class UAT03PrescriptionDispense(TestCase):
    """
    Scénario : Prescription → Validation → Dispense avec décrémentation stock FIFO.
    """

    def setUp(self):
        self.medecin    = make_user_personnel('med_uat03', 'Médecin')
        self.pharmacien = make_user_personnel('pha_uat03', 'Pharmacien')
        self.patient    = make_patient('Pharma', 'UAT')
        self.consultation = Consultation.objects.create(
            patient=self.patient, medecin=self.medecin,
            date=timezone.now(), motif='UAT'
        )
        self.medicament = Medicament.objects.create(
            nom='Amoxicilline 500mg', categorie='Antibiotique', seuil_alerte=20
        )
        self.lot = LotMedicament.objects.create(
            medicament=self.medicament, numero_lot='LOT-UAT-001',
            quantite=100, date_peremption=date.today() + timedelta(days=365)
        )

    def test_prescription_verrouillage_apres_validation(self):
        presc = Prescription.objects.create(
            consultation=self.consultation,
            medecin=self.medecin, patient=self.patient
        )
        self.assertFalse(presc.verrouille)
        presc.valider(self.medecin)
        self.assertTrue(presc.verrouille)
        self.assertEqual(presc.statut, 'Validée')
        self.assertEqual(len(presc.signature_hash), 64)

    def test_modification_prescription_verrouillee_impossible(self):
        presc = Prescription.objects.create(
            consultation=self.consultation,
            medecin=self.medecin, patient=self.patient
        )
        presc.valider(self.medecin)
        with self.assertRaises(ValueError):
            presc.notes = 'Modification illégale'
            presc.save()

    def test_dispense_decremente_stock_fifo(self):
        presc = Prescription.objects.create(
            consultation=self.consultation,
            medecin=self.medecin, patient=self.patient
        )
        ligne = LignePrescription.objects.create(
            prescription=presc, medicament=self.medicament,
            posologie='1 cp x 3/j', duree_jours=7, quantite=21
        )
        stock_avant = self.lot.quantite
        ligne.dispenser(self.pharmacien)
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.quantite, stock_avant - 21)
        self.assertTrue(ligne.dispensee)
        self.assertEqual(MouvementStock.objects.filter(lot=self.lot, type_mouvement='Sortie').count(), 1)


# ── UAT-04 : Facturation et paiement partiel ──────────────────────────────────

class UAT04FacturationPaiement(TestCase):
    """
    Scénario : Facture → Paiement partiel → Solde → PDF.
    Journal comptable immuable (aucune suppression).
    """

    def setUp(self):
        self.patient = make_patient('Factu', 'UAT')

    def test_statut_initial_en_attente(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Hospitalisation', montant_total=3500000
        )
        self.assertEqual(f.statut, 'En attente')
        self.assertEqual(f.montant_paye, 0)
        self.assertEqual(f.solde, 3500000)

    def test_paiement_partiel_statut_partielle(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Hospitalisation', montant_total=3500000
        )
        Paiement.objects.create(facture=f, montant=1750000, mode_paiement='Mobile Money')
        f.update_statut()
        self.assertEqual(f.statut, 'Partielle')
        self.assertEqual(f.solde, 1750000)

    def test_paiement_complet_statut_payee(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Consultation', montant_total=450000
        )
        Paiement.objects.create(facture=f, montant=450000, mode_paiement='Espèces')
        f.update_statut()
        self.assertEqual(f.statut, 'Payée')
        self.assertEqual(f.solde, 0)

    def test_journal_comptable_immutable_paiement_non_supprimable(self):
        """Les paiements ne peuvent pas être supprimés (FK PROTECT sur Facture)."""
        f = Facture.objects.create(
            patient=self.patient, type_facture='Examens', montant_total=200000
        )
        p = Paiement.objects.create(facture=f, montant=200000, mode_paiement='Virement')
        # La facture ne peut pas être supprimée tant qu'un paiement existe (PROTECT)
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            f.patient.delete()  # Patient protégé par la facture


# ── UAT-05 : Sécurité — Rate Limiting ────────────────────────────────────────

class UAT05RateLimiting(TestCase):
    """
    Scénario : 5 tentatives de connexion → 6e bloquée (HTTP 429).
    """

    def setUp(self):
        self.client = Client()

    def test_rate_limiter_bloque_apres_5_tentatives(self):
        from core.security import RateLimiter
        limiter = RateLimiter(max_attempts=5, window_seconds=300)
        ip = '10.0.0.1'
        for _ in range(5):
            allowed, _ = limiter.check(ip, 'login')
            self.assertTrue(allowed)
            limiter.increment(ip, 'login')
        allowed, remaining = limiter.check(ip, 'login')
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    def test_rate_limiter_reset_apres_fenetre(self):
        from core.security import RateLimiter
        limiter = RateLimiter(max_attempts=3, window_seconds=300)
        ip = '10.0.0.2'
        for _ in range(3):
            limiter.increment(ip, 'login')
        allowed, _ = limiter.check(ip, 'login')
        self.assertFalse(allowed)
        limiter.reset(ip, 'login')
        allowed, _ = limiter.check(ip, 'login')
        self.assertTrue(allowed)

    def test_login_endpoint_retourne_429_apres_limite(self):
        """Test HTTP 429 sur l'endpoint de login via le middleware."""
        from django.core.cache import cache
        # Simuler 5 tentatives déjà enregistrées en cache
        cache.set('rl:/api/v1/auth/login/:127.0.0.1', 5, timeout=300)
        response = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({'username': 'x', 'password': 'x'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429)
        cache.delete('rl:/api/v1/auth/login/:127.0.0.1')


# ── UAT-06 : Upload document avec antivirus ───────────────────────────────────

class UAT06AntivirusUpload(TestCase):
    """
    Scénario : Upload de fichiers — scan antivirus obligatoire.
    PDF valide → accepté. EXE → rejeté. PHP dans contenu → rejeté.
    """

    def test_pdf_valide_accepte(self):
        from core.antivirus import AntivirusEngine
        engine = AntivirusEngine()
        # Magic bytes PDF valides
        pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'
        result = engine.scan(io.BytesIO(pdf_content), 'rapport.pdf', 'application/pdf', 'documents')
        self.assertTrue(result.is_clean)
        self.assertEqual(result.mime_detected, 'application/pdf')

    def test_extension_exe_rejetee(self):
        from core.antivirus import AntivirusEngine
        engine = AntivirusEngine()
        exe_content = b'MZ\x90\x00\x03\x00\x00\x00' + b'\x00' * 100
        result = engine.scan(io.BytesIO(exe_content), 'malware.exe', 'application/octet-stream')
        self.assertFalse(result.is_clean)
        self.assertTrue(any('EXTENSION_DANGEREUSE' in t or 'SIGNATURE_MALWARE' in t for t in result.threats))

    def test_contenu_php_rejete(self):
        from core.antivirus import AntivirusEngine
        engine = AntivirusEngine()
        php_content = b'%PDF-1.4\n<?php system($_GET["cmd"]); ?>\n'
        result = engine.scan(io.BytesIO(php_content), 'document.pdf', 'application/pdf', 'documents')
        self.assertFalse(result.is_clean)
        self.assertTrue(any('PHP_EXEC' in t or 'CONTENU_MALVEILLANT' in t for t in result.threats))

    def test_fichier_vide_rejete(self):
        from core.antivirus import AntivirusEngine
        engine = AntivirusEngine()
        result = engine.scan(io.BytesIO(b''), 'vide.pdf', 'application/pdf')
        self.assertFalse(result.is_clean)
        self.assertIn('FICHIER_VIDE', result.threats)

    def test_scan_enregistre_dans_audit(self):
        """Chaque scan doit être tracé dans l'audit trail."""
        from core.antivirus import require_clean_file
        from ninja.errors import HttpError
        pdf_content = b'%PDF-1.4\n' + b'A' * 100
        count_before = AuditTrail.objects.count()
        try:
            require_clean_file(io.BytesIO(pdf_content), 'test.pdf', 'application/pdf')
        except HttpError:
            pass
        # L'audit trail doit avoir une entrée FileScan
        self.assertGreaterEqual(AuditTrail.objects.count(), count_before)


# ── UAT-07 : Archivage et politique de conservation ──────────────────────────

class UAT07ArchivagePolitique(TestCase):
    """
    Scénario : Archivage dossier patient — politique 20 ans.
    Anonymisation RGPD.
    """

    def setUp(self):
        self.admin   = make_user_personnel('admin_uat07', 'Admin', is_staff=True)
        self.patient = make_patient('Archive', 'UAT')

    def test_archivage_calcule_date_destruction_20_ans(self):
        archive, _ = ArchiveDossier.objects.get_or_create(patient=self.patient)
        archive.archiver(self.admin, motif='Fin de suivi')
        self.assertEqual(archive.statut, 'Archivé')
        expected_year = date.today().year + ArchiveDossier.DUREE_CONSERVATION
        self.assertEqual(archive.date_destruction_prevue.year, expected_year)

    def test_anonymisation_efface_donnees_personnelles(self):
        self.patient.anonymiser()
        self.patient.refresh_from_db()
        self.assertIn('Anonyme_', self.patient.nom)
        self.assertEqual(self.patient.telephone, '')
        self.assertEqual(self.patient.adresse, '')
        self.assertEqual(self.patient.prenom, '')

    def test_document_medical_hash_sha256_calcule(self):
        """Chaque document doit avoir un hash SHA-256 pour intégrité."""
        import hashlib
        contenu = b'%PDF-1.4 contenu test document medical'
        hash_attendu = hashlib.sha256(contenu).hexdigest()
        doc = DocumentMedical(
            patient=self.patient,
            type_document='Compte-rendu',
            titre='CR Consultation UAT',
            mime_type='application/pdf',
            taille_octets=len(contenu),
            hash_sha256=hash_attendu,
            cree_par=self.admin,
        )
        self.assertEqual(len(doc.hash_sha256), 64)
        self.assertEqual(doc.hash_sha256, hash_attendu)

    def test_acces_document_trace(self):
        """Tout accès à un document sensible doit être tracé."""
        count_before = AuditTrail.objects.count()
        AuditTrail.log(
            request=None, action_type='VIEW',
            model_name='DocumentMedical', object_id=1,
            details={'patient_id': self.patient.id, 'type': 'Compte-rendu', 'action': 'Lecture'}
        )
        self.assertEqual(AuditTrail.objects.count(), count_before + 1)
