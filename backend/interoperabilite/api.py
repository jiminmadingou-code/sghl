from ninja import Router
from django.shortcuts import get_object_or_404
from .fhir_converters import (
    patient_to_fhir, observation_to_fhir,
    encounter_to_fhir, medication_request_to_fhir, diagnostic_report_to_fhir
)

router = Router(tags=['Interopérabilité FHIR R4'])

FHIR_CONTENT_TYPE = 'application/fhir+json'


@router.get('/fhir/Patient/{patient_id}')
def fhir_patient(request, patient_id: int):
    from patients.models import Patient
    patient = get_object_or_404(Patient, id=patient_id)
    patient.log_access(request.user, request.META.get('REMOTE_ADDR'))
    return patient_to_fhir(patient)


@router.get('/fhir/Patient')
def fhir_patient_search(request, family: str = None, birthdate: str = None):
    from patients.models import Patient
    qs = Patient.objects.all()
    if family:
        qs = qs.filter(nom__icontains=family)
    if birthdate:
        qs = qs.filter(date_naissance=birthdate)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": qs.count(),
        "entry": [{"resource": patient_to_fhir(p)} for p in qs[:50]]
    }


@router.get('/fhir/Observation')
def fhir_observations(request, patient_id: int):
    from soins.models import ConstanteVitale
    constantes = ConstanteVitale.objects.filter(
        hospitalisation__patient_id=patient_id
    ).select_related('hospitalisation')[:100]
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": constantes.count(),
        "entry": [{"resource": observation_to_fhir(c, patient_id)} for c in constantes]
    }


@router.get('/fhir/Encounter')
def fhir_encounters(request, patient_id: int):
    from hospitalisations.models import Hospitalisation
    hosps = Hospitalisation.objects.filter(patient_id=patient_id)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": hosps.count(),
        "entry": [{"resource": encounter_to_fhir(h)} for h in hosps]
    }


@router.get('/fhir/MedicationRequest')
def fhir_medication_requests(request, patient_id: int):
    from prescriptions.models import LignePrescription
    lignes = LignePrescription.objects.filter(
        prescription__patient_id=patient_id
    ).select_related('prescription', 'medicament')
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": lignes.count(),
        "entry": [{"resource": medication_request_to_fhir(l)} for l in lignes]
    }


@router.get('/fhir/DiagnosticReport')
def fhir_diagnostic_reports(request, patient_id: int):
    from laboratoire.models import ExamenLaboratoire
    examens = ExamenLaboratoire.objects.filter(patient_id=patient_id)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": examens.count(),
        "entry": [{"resource": diagnostic_report_to_fhir(e)} for e in examens]
    }


@router.get('/fhir/metadata')
def fhir_capability_statement(request):
    """CapabilityStatement FHIR — décrit les capacités du serveur."""
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": "2025-01-01",
        "kind": "instance",
        "fhirVersion": "4.0.1",
        "format": ["application/fhir+json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {"type": "Patient",           "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Observation",       "interaction": [{"code": "search-type"}]},
                    {"type": "Encounter",         "interaction": [{"code": "search-type"}]},
                    {"type": "MedicationRequest", "interaction": [{"code": "search-type"}]},
                    {"type": "DiagnosticReport",  "interaction": [{"code": "search-type"}]},
                ]
            }
        ]
    }
