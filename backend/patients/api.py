from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import date
from .models import Patient

router = Router(tags=['Patients'])

class PatientIn(Schema):
    prenom: str
    nom: str
    date_naissance: date
    sexe: str
    telephone: str = ''
    adresse: str = ''
    groupe_sanguin: str = ''
    allergies: str = ''
    antecedents: str = ''

class PatientOut(Schema):
    id: int
    prenom: str
    nom: str
    date_naissance: date
    sexe: str
    telephone: str
    groupe_sanguin: str
    statut: str = 'Actif'

    @staticmethod
    def resolve_statut(obj):
        if hasattr(obj, 'hospitalisations') and obj.hospitalisations.filter(statut='Actif').exists():
            return 'Hospitalisé'
        return 'Actif'

@router.get('/', response=List[PatientOut])
def list_patients(request, search: Optional[str] = None):
    qs = Patient.objects.all()
    if search:
        qs = qs.filter(nom__icontains=search) | qs.filter(prenom__icontains=search)
    return qs

@router.post('/', response=PatientOut)
def create_patient(request, payload: PatientIn):
    return Patient.objects.create(**payload.dict())

@router.get('/{patient_id}', response=PatientOut)
def get_patient(request, patient_id: int):
    return get_object_or_404(Patient, id=patient_id)

@router.put('/{patient_id}', response=PatientOut)
def update_patient(request, patient_id: int, payload: PatientIn):
    patient = get_object_or_404(Patient, id=patient_id)
    for k, v in payload.dict().items():
        setattr(patient, k, v)
    patient.save()
    return patient

@router.delete('/{patient_id}')
def delete_patient(request, patient_id: int):
    get_object_or_404(Patient, id=patient_id).delete()
    return {'success': True}
