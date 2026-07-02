from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import PassageUrgences, ActeUrgence

router = Router(tags=['Urgences'])


class PassageIn(Schema):
    patient_id: int
    triage: str
    mode_arrivee: str = 'Autonome'
    motif_principal: str
    description_clinique: str = ''
    tension_systolique: Optional[int] = None
    tension_diastolique: Optional[int] = None
    frequence_cardiaque: Optional[int] = None
    temperature: Optional[float] = None
    saturation_o2: Optional[int] = None
    glasgow: Optional[int] = None


class PassageOut(Schema):
    id: int
    patient_id: int
    triage: str
    statut: str
    mode_arrivee: str
    motif_principal: str
    date_arrivee: datetime
    duree_attente_minutes: Optional[int]
    tension_systolique: Optional[int]
    frequence_cardiaque: Optional[int]
    saturation_o2: Optional[int]
    glasgow: Optional[int]


@router.get('/', response=List[PassageOut])
def list_passages(request, statut: Optional[str] = None):
    qs = PassageUrgences.objects.select_related('patient')
    if statut:
        qs = qs.filter(statut=statut)
    return qs


@router.post('/', response=PassageOut)
def creer_passage(request, payload: PassageIn):
    from django.utils import timezone
    passage = PassageUrgences.objects.create(
        **payload.dict(),
        date_triage=timezone.now()
    )
    return passage


@router.get('/{passage_id}', response=PassageOut)
def get_passage(request, passage_id: int):
    return get_object_or_404(PassageUrgences, id=passage_id)


@router.patch('/{passage_id}/statut')
def update_statut(request, passage_id: int, statut: str):
    passage = get_object_or_404(PassageUrgences, id=passage_id)
    from django.utils import timezone
    passage.statut = statut
    if statut == 'En cours' and not passage.date_prise_en_charge:
        passage.date_prise_en_charge = timezone.now()
    if statut in ('Sorti', 'Transféré', 'Décédé'):
        passage.date_sortie = timezone.now()
    passage.save()
    return {'success': True, 'statut': statut}


@router.get('/stats/temps-attente')
def stats_attente(request):
    from django.db.models import Avg, Count
    from django.utils import timezone
    today = timezone.now().date()
    passages_today = PassageUrgences.objects.filter(date_arrivee__date=today)
    return {
        'total_aujourd_hui': passages_today.count(),
        'en_attente': passages_today.filter(statut='En attente').count(),
        'en_cours': passages_today.filter(statut='En cours').count(),
        'p1_actifs': passages_today.filter(triage='P1', statut__in=['En attente', 'En cours']).count(),
        'p2_actifs': passages_today.filter(triage='P2', statut__in=['En attente', 'En cours']).count(),
    }
