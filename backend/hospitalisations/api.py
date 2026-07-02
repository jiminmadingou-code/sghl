from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import date
from .models import Hospitalisation, Lit

router = Router(tags=['Hospitalisations'])

class HospitalisationIn(Schema):
    patient_id: int
    lit_id: int
    medecin_referent_id: int
    date_entree: date
    date_sortie_prevue: Optional[date] = None
    motif: str

class HospitalisationOut(Schema):
    id: int
    patient_id: int
    lit_id: int
    medecin_referent_id: int
    date_entree: date
    date_sortie_prevue: Optional[date]
    motif: str
    statut: str

@router.get('/', response=List[HospitalisationOut])
def list_hospitalisations(request, statut: Optional[str] = None):
    qs = Hospitalisation.objects.select_related('patient', 'lit', 'medecin_referent')
    if statut:
        qs = qs.filter(statut=statut)
    return qs

@router.post('/', response=HospitalisationOut)
def create_hospitalisation(request, payload: HospitalisationIn):
    lit = get_object_or_404(Lit, id=payload.lit_id)
    if lit.occupe:
        from ninja.errors import HttpError
        raise HttpError(400, 'Ce lit est déjà occupé')
    h = Hospitalisation.objects.create(**payload.dict())
    h.log_audit(request, 'CREATE', new_value=payload.dict())
    return h

@router.patch('/{hospit_id}/sortie')
def sortie_patient(request, hospit_id: int, date_sortie: date):
    h = get_object_or_404(Hospitalisation, id=hospit_id)
    old_value = {'statut': h.statut, 'date_sortie_reelle': str(h.date_sortie_reelle) if h.date_sortie_reelle else None}
    h.statut = 'Sorti'
    h.date_sortie_reelle = date_sortie
    h.save()
    h.log_audit(request, 'UPDATE', old_value=old_value, new_value={'statut': 'Sorti', 'date_sortie_reelle': str(date_sortie)})
    return {'success': True}
