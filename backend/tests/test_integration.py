"""
Tests d'intégration complets pour le SGHL.
Couvre: patients, hospitalisations, laboratoire, pharmacie, facturation, prescriptions, audit, sécurité.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from patients.models import Patient, Consultation
from personnel.models import Personnel
from hospitalisations.models import Batiment, Service, Chambre, Lit, Hospitalisation
from laboratoire.models import ExamenLaboratoire
from pharmacie.models import Medicament, LotMedicament, MouvementStock
from facturation.models import Facture, Paiement
from prescriptions.models import Prescription, LignePrescription
from audit.models import AuditTrail


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_personnel(username, role):
    u = User.objects.create_user(username, f'{username}@test.local', 'Test@1234')
    return Personnel.objects.create(user=u, role=role)


def make_patient(prenom='Test', nom='Patient'):
    return Patient.objects.create(
        prenom=prenom, nom=nom,
        date_naissance=date(1990, 1, 1), sexe='M'
    )


def make_lit():
    bat = Batiment.objects.create(code=f'B{Batiment.objects.count()+1}', nom='Bâtiment Test')
    svc = Service.objects.create(batiment=bat, code=f'S{Service.objects.count()+1}', nom='Service Test')
    ch  = Chambre.objects.create(service=svc, numero=f'C{Chambre.objects.count()+1:02d}')
    return Lit.objects.create(chambre=ch, numero_lit='L01')


# ── Patient ───────────────────────────────────────────────────────────────────

class PatientModelTest(TestCase):

    def setUp(self):
        self.patient = Patient.objects.create(
            prenom='Mamadou', nom='Diallo',
            date_naissance=date(1979, 3, 15),
            sexe='M', telephone='620000001', groupe_sanguin='A+'
        )

    def test_str(self):
        self.assertEqual(str(self.patient), 'Mamadou Diallo')

    def test_numero_securise_genere(self):
        self.assertIsNotNone(self.patient.numero_securise)
        self.assertEqual(len(self.patient.numero_securise), 16)

    def test_versioning_incremente(self):
        v0 = self.patient.version
        self.patient.telephone = '620000099'
        self.patient.save()
        self.assertEqual(self.patient.version, v0 + 1)

    def test_anonymisation(self):
        self.patient.anonymiser()
        self.assertIn('Anonyme_', self.patient.nom)
        self.assertEqual(self.patient.telephone, '')
        self.assertEqual(self.patient.adresse, '')


# ── Hospitalisation ───────────────────────────────────────────────────────────

class HospitalisationTest(TestCase):

    def setUp(self):
        self.patient = make_patient()
        self.medecin = make_personnel('med_hospit', 'Médecin')
        self.lit = make_lit()

    def test_admission_occupe_lit(self):
        self.assertEqual(self.lit.statut, 'Libre')
        Hospitalisation.objects.create(
            patient=self.patient, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='Test'
        )
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, 'Occupe')

    def test_admission_lit_occupe_leve_erreur(self):
        Hospitalisation.objects.create(
            patient=self.patient, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='Premier'
        )
        patient2 = make_patient('Autre', 'Patient')
        with self.assertRaises(ValueError):
            Hospitalisation.objects.create(
                patient=patient2, lit=self.lit,
                medecin_referent=self.medecin,
                date_entree=date.today(), motif='Deuxième'
            )

    def test_sortie_libere_lit(self):
        h = Hospitalisation.objects.create(
            patient=self.patient, lit=self.lit,
            medecin_referent=self.medecin,
            date_entree=date.today(), motif='Test'
        )
        h.statut = 'Sorti'
        h.date_sortie_reelle = date.today()
        h.save()
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, 'Libre')


# ── Laboratoire ───────────────────────────────────────────────────────────────

class LaboratoireTest(TestCase):

    def setUp(self):
        self.patient    = make_patient('Labo', 'Test')
        self.biologiste = make_personnel('bio_test', 'Biologiste')
        self.medecin    = make_personnel('med_labo', 'Médecin')

    def test_statut_initial_commande(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='NFS', priorite='Normal'
        )
        self.assertEqual(examen.statut, 'Commande')
        self.assertFalse(examen.resultat_immutable)

    def test_validation_rend_immutable(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='Glycémie', resultat='1.26 g/L',
            statut='Saisie résultats'
        )
        examen.valider(self.biologiste)
        self.assertEqual(examen.statut, 'Validé')
        self.assertTrue(examen.resultat_immutable)
        self.assertEqual(examen.valide_par, self.biologiste)
        self.assertIsNotNone(examen.date_validation)

    def test_resultat_immutable_flag(self):
        examen = ExamenLaboratoire.objects.create(
            patient=self.patient, prescripteur=self.medecin,
            type_examen='ECG', resultat='Normal', statut='Saisie résultats'
        )
        examen.valider(self.biologiste)
        self.assertTrue(examen.resultat_immutable)


# ── Pharmacie ─────────────────────────────────────────────────────────────────

class PharmacieTest(TestCase):

    def setUp(self):
        self.med = Medicament.objects.create(
            nom='Paracétamol 500mg', categorie='Analgésique', seuil_alerte=50
        )
        self.lot = LotMedicament.objects.create(
            medicament=self.med, numero_lot='LOT-001',
            quantite=100, date_peremption=date.today() + timedelta(days=365)
        )
        self.pharmacien = make_personnel('pharma_test', 'Pharmacien')

    def test_statut_normal(self):
        self.assertEqual(self.lot.statut, 'Normal')

    def test_statut_alerte(self):
        self.lot.quantite = 30
        self.lot.save()
        self.assertEqual(self.lot.statut, 'Alerte')

    def test_statut_rupture(self):
        self.lot.quantite = 0
        self.lot.save()
        self.assertEqual(self.lot.statut, 'Rupture')

    def test_mouvement_stock_enregistre(self):
        MouvementStock.objects.create(
            lot=self.lot, type_mouvement='Sortie',
            quantite=20, motif='Dispense', created_by=self.pharmacien
        )
        self.assertEqual(MouvementStock.objects.filter(lot=self.lot).count(), 1)


# ── Facturation ───────────────────────────────────────────────────────────────

class FacturationTest(TestCase):

    def setUp(self):
        self.patient = make_patient('Facture', 'Test')

    def test_statut_initial_en_attente(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Consultation', montant_total=450000
        )
        self.assertEqual(f.statut, 'En attente')
        self.assertEqual(f.montant_paye, 0)
        self.assertEqual(f.solde, 450000)

    def test_paiement_partiel(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Hospitalisation', montant_total=2800000
        )
        Paiement.objects.create(facture=f, montant=1400000, mode_paiement='Espèces')
        f.update_statut()
        self.assertEqual(f.statut, 'Partielle')
        self.assertEqual(f.solde, 1400000)

    def test_paiement_complet(self):
        f = Facture.objects.create(
            patient=self.patient, type_facture='Consultation', montant_total=450000
        )
        Paiement.objects.create(facture=f, montant=450000, mode_paiement='Mobile Money')
        f.update_statut()
        self.assertEqual(f.statut, 'Payée')
        self.assertEqual(f.solde, 0)


# ── Prescription ──────────────────────────────────────────────────────────────

class PrescriptionTest(TestCase):

    def setUp(self):
        self.patient = make_patient('Presc', 'Test')
        self.medecin = make_personnel('med_presc', 'Médecin')
        self.consultation = Consultation.objects.create(
            patient=self.patient, medecin=self.medecin,
            date=timezone.now(), motif='Test'
        )

    def test_verrouillage_apres_validation(self):
        presc = Prescription.objects.create(
            consultation=self.consultation,
            medecin=self.medecin, patient=self.patient
        )
        self.assertFalse(presc.verrouille)
        presc.valider(self.medecin)
        self.assertTrue(presc.verrouille)
        self.assertEqual(presc.statut, 'Validée')
        self.assertIsNotNone(presc.signature_hash)
        self.assertEqual(len(presc.signature_hash), 64)

    def test_modification_verrouillee_leve_erreur(self):
        presc = Prescription.objects.create(
            consultation=self.consultation,
            medecin=self.medecin, patient=self.patient
        )
        presc.valider(self.medecin)
        with self.assertRaises(ValueError):
            presc.notes = 'Modification illégale'
            presc.save()


# ── Audit Trail ───────────────────────────────────────────────────────────────

class AuditTrailTest(TestCase):

    def test_creation_log(self):
        log = AuditTrail.log(
            request=None, action_type='CREATE',
            model_name='Patient', object_id=1,
            details={'test': True}
        )
        self.assertEqual(log.action_type, 'CREATE')
        self.assertEqual(log.model_name, 'Patient')
        self.assertEqual(log.object_id, 1)
        self.assertEqual(log.details, {'test': True})

    def test_log_persiste(self):
        AuditTrail.log(request=None, action_type='DELETE', model_name='Test', object_id=99)
        self.assertEqual(AuditTrail.objects.filter(model_name='Test', object_id=99).count(), 1)

    def test_tous_types_actions(self):
        for action in ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'VALIDATE', 'EXPORT']:
            AuditTrail.log(request=None, action_type=action, model_name='Test', object_id=1)
        self.assertEqual(AuditTrail.objects.filter(model_name='Test').count(), 6)


# ── Sécurité ──────────────────────────────────────────────────────────────────

class SecurityTest(TestCase):

    def test_aes_chiffrement_dechiffrement(self):
        from core.security import AESCipher
        cipher = AESCipher()
        texte = 'Données sensibles patient — confidentiel'
        chiffre = cipher.encrypt(texte)
        dechiffre = cipher.decrypt(chiffre)
        self.assertEqual(dechiffre, texte)
        self.assertNotEqual(chiffre, texte.encode())

    def test_aes_deux_chiffrements_differents(self):
        """Chaque chiffrement doit produire un résultat différent (IV aléatoire)."""
        from core.security import AESCipher
        cipher = AESCipher()
        texte = 'même texte'
        c1 = cipher.encrypt(texte)
        c2 = cipher.encrypt(texte)
        self.assertNotEqual(c1, c2)

    def test_mfa_code_6_chiffres(self):
        from core.security import MFAHandler
        handler = MFAHandler()
        code = handler.generate_code(user_id=42)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_mfa_verification_correcte(self):
        from core.security import MFAHandler
        handler = MFAHandler()
        code = handler.generate_code(user_id=43)
        self.assertTrue(handler.verify_code(43, code))

    def test_mfa_code_usage_unique(self):
        from core.security import MFAHandler
        handler = MFAHandler()
        code = handler.generate_code(user_id=44)
        handler.verify_code(44, code)
        self.assertFalse(handler.verify_code(44, code))

    def test_rate_limiter_bloque_apres_max(self):
        from core.security import RateLimiter
        limiter = RateLimiter(max_attempts=3, window_seconds=60)
        for _ in range(3):
            allowed, _ = limiter.check('192.168.1.1', 'login')
            self.assertTrue(allowed)
            limiter.increment('192.168.1.1', 'login')
        allowed, remaining = limiter.check('192.168.1.1', 'login')
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    def test_rate_limiter_reset(self):
        from core.security import RateLimiter
        limiter = RateLimiter(max_attempts=2, window_seconds=60)
        limiter.increment('192.168.1.2', 'login')
        limiter.increment('192.168.1.2', 'login')
        allowed, _ = limiter.check('192.168.1.2', 'login')
        self.assertFalse(allowed)
        limiter.reset('192.168.1.2', 'login')
        allowed, _ = limiter.check('192.168.1.2', 'login')
        self.assertTrue(allowed)
