from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import InterventionChirurgicale, SalleOperation

router = Router(tags=['Bloc Opératoire'])


class InterventionIn(Schema):
    patient_id: int
    hospitalisation_id: int
    salle_id: int
    chirurgien_principal_id: int
    anesthesiste_id: int
    acte_principal: str
    code_ccam: str = ''
    type_urgence: str = 'Programmée'
    type_anesthesie: str
    date_programmee: datetime
    duree_prevue_minutes: int = 60


class InterventionOut(Schema):
    id: int
    patient_id: int
    acte_principal: str
    code_ccam: str
    type_urgence: str
    type_anesthesie: str
    statut: str
    date_programmee: datetime
    date_debut_reelle: Optional[datetime]
    date_fin_reelle: Optional[datetime]
    duree_reelle_minutes: Optional[int]


@router.get('/', response=List[InterventionOut])
def list_interventions(request, statut: Optional[str] = None):
    qs = InterventionChirurgicale.objects.select_related('patient', 'salle')
    if statut:
        qs = qs.filter(statut=statut)
    return qs


@router.post('/', response=InterventionOut)
def programmer_intervention(request, payload: InterventionIn):
    return InterventionChirurgicale.objects.create(**payload.dict())


@router.post('/{intervention_id}/demarrer')
def demarrer_intervention(request, intervention_id: int):
    intervention = get_object_or_404(InterventionChirurgicale, id=intervention_id)
    intervention.demarrer()
    return {'success': True}


@router.post('/{intervention_id}/terminer')
def terminer_intervention(request, intervention_id: int, compte_rendu: str = '', complications: str = ''):
    intervention = get_object_or_404(InterventionChirurgicale, id=intervention_id)
    intervention.terminer(compte_rendu, complications)
    return {'success': True}


@router.get('/planning-salle/{salle_id}')
def planning_salle(request, salle_id: int, date: str):
    from datetime import date as date_type
    d = date_type.fromisoformat(date)
    interventions = InterventionChirurgicale.objects.filter(
        salle_id=salle_id,
        date_programmee__date=d
    ).order_by('date_programmee')
    return [{'id': i.id, 'acte': i.acte_principal, 'patient': str(i.patient),
              'heure': i.date_programmee.strftime('%H:%M'), 'duree': i.duree_prevue_minutes,
              'statut': i.statut} for i in interventions]
