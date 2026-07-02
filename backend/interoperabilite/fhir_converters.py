"""
Convertisseurs FHIR R4 pour le SGHL.
Transforme les modèles Django en ressources FHIR standard.
"""
from django.utils import timezone


def patient_to_fhir(patient) -> dict:
    """Convertit un Patient Django en ressource FHIR Patient R4."""
    gender_map = {'M': 'male', 'F': 'female'}
    resource = {
        "resourceType": "Patient",
        "id": str(patient.id),
        "meta": {
            "versionId": str(patient.version),
            "lastUpdated": patient.updated_at.isoformat(),
            "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        },
        "identifier": [
            {
                "system": "urn:sghl:patient",
                "value": patient.numero_securise
            }
        ],
        "name": [
            {
                "use": "official",
                "family": patient.nom,
                "given": [patient.prenom]
            }
        ],
        "gender": gender_map.get(patient.sexe, 'unknown'),
        "birthDate": patient.date_naissance.isoformat(),
        "telecom": [],
        "address": [],
    }
    if patient.telephone:
        resource["telecom"].append({"system": "phone", "value": patient.telephone, "use": "mobile"})
    if patient.email:
        resource["telecom"].append({"system": "email", "value": patient.email})
    if patient.adresse:
        resource["address"].append({"text": patient.adresse, "use": "home"})
    if patient.groupe_sanguin:
        resource["extension"] = [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/patient-bloodType",
                "valueString": patient.groupe_sanguin
            }
        ]
    return resource


def observation_to_fhir(constante, patient_id: int) -> dict:
    """Convertit une ConstanteVitale en ressource FHIR Observation."""
    loinc_map = {
        'Temperature':          {'code': '8310-5',  'display': 'Body temperature', 'unit': 'Cel'},
        'Pouls':                {'code': '8867-4',  'display': 'Heart rate',        'unit': '/min'},
        'PressionSystolique':   {'code': '8480-6',  'display': 'Systolic BP',       'unit': 'mm[Hg]'},
        'PressionDiastolique':  {'code': '8462-4',  'display': 'Diastolic BP',      'unit': 'mm[Hg]'},
        'Respiration':          {'code': '9279-1',  'display': 'Respiratory rate',  'unit': '/min'},
        'SaturationO2':         {'code': '59408-5', 'display': 'Oxygen saturation', 'unit': '%'},
        'Glycemie':             {'code': '2339-0',  'display': 'Glucose',           'unit': 'mg/dL'},
        'Poids':                {'code': '29463-7', 'display': 'Body weight',       'unit': 'kg'},
        'Taille':               {'code': '8302-2',  'display': 'Body height',       'unit': 'cm'},
    }
    loinc = loinc_map.get(constante.type_constante, {'code': 'unknown', 'display': constante.type_constante, 'unit': ''})
    status = 'final'
    if constante.alerte_seuil:
        status = 'amended'
    return {
        "resourceType": "Observation",
        "id": str(constante.id),
        "status": status,
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": loinc['code'], "display": loinc['display']}]},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": constante.date_mesure.isoformat(),
        "valueQuantity": {
            "value": float(constante.valeur),
            "unit": loinc['unit'],
            "system": "http://unitsofmeasure.org",
            "code": loinc['unit']
        },
        "interpretation": [
            {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                         "code": "H" if constante.alerte_seuil else "N"}]}
        ] if constante.alerte_seuil else []
    }


def encounter_to_fhir(hospitalisation) -> dict:
    """Convertit une Hospitalisation en ressource FHIR Encounter."""
    status_map = {'Actif': 'in-progress', 'Sorti': 'finished', 'Transféré': 'triaged'}
    return {
        "resourceType": "Encounter",
        "id": str(hospitalisation.id),
        "status": status_map.get(hospitalisation.statut, 'unknown'),
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP", "display": "inpatient encounter"},
        "subject": {"reference": f"Patient/{hospitalisation.patient_id}"},
        "participant": [
            {"individual": {"reference": f"Practitioner/{hospitalisation.medecin_referent_id}"}}
        ],
        "period": {
            "start": hospitalisation.date_entree.isoformat(),
            "end": hospitalisation.date_sortie_reelle.isoformat() if hospitalisation.date_sortie_reelle else None
        },
        "reasonCode": [{"text": hospitalisation.motif}],
        "location": [
            {"location": {"display": f"Lit {hospitalisation.lit_id}"}, "status": "active"}
        ]
    }


def medication_request_to_fhir(ligne_prescription) -> dict:
    """Convertit une LignePrescription en ressource FHIR MedicationRequest."""
    return {
        "resourceType": "MedicationRequest",
        "id": str(ligne_prescription.id),
        "status": "active" if not ligne_prescription.dispensee else "completed",
        "intent": "order",
        "medicationCodeableConcept": {
            "text": ligne_prescription.medicament.nom
        },
        "subject": {"reference": f"Patient/{ligne_prescription.prescription.patient_id}"},
        "requester": {"reference": f"Practitioner/{ligne_prescription.prescription.medecin_id}"},
        "dosageInstruction": [
            {
                "text": ligne_prescription.posologie,
                "timing": {"repeat": {"duration": ligne_prescription.duree_jours, "durationUnit": "d"}},
                "doseAndRate": [{"doseQuantity": {"value": ligne_prescription.quantite}}]
            }
        ],
        "note": [{"text": ligne_prescription.instructions}] if ligne_prescription.instructions else []
    }


def diagnostic_report_to_fhir(examen_labo) -> dict:
    """Convertit un ExamenLaboratoire en ressource FHIR DiagnosticReport."""
    status_map = {
        'Commande': 'registered', 'Prélèvement': 'partial',
        'Saisie résultats': 'preliminary', 'Validé': 'final', 'Publié': 'final'
    }
    return {
        "resourceType": "DiagnosticReport",
        "id": str(examen_labo.id),
        "status": status_map.get(examen_labo.statut, 'unknown'),
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "LAB"}]}],
        "code": {"text": examen_labo.type_examen},
        "subject": {"reference": f"Patient/{examen_labo.patient_id}"},
        "issued": examen_labo.date_prescription.isoformat(),
        "performer": [{"reference": f"Practitioner/{examen_labo.prescripteur_id}"}],
        "conclusion": examen_labo.resultat if examen_labo.resultat_immutable else None,
        "conclusionCode": [],
    }
