from ninja import Router, Schema
from typing import List, Optional
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from .models import Grossesse, ConsultationPrenatale, Accouchement, Nouveau_Ne

router = Router(tags=['Maternité'])


class GrossesseIn(Schema):
    patiente_id: int
    date_debut_grossesse: date
    date_terme_prevue: date
    type_grossesse: str = 'Simple'
    medecin_referent_id: int
    antecedents_obstetricaux: str = ''


class GrossesseOut(Schema):
    id: int
    patiente_id: int
    date_terme_prevue: date
    type_grossesse: str
    statut: str
    semaines_amenorrhee: int


@router.get('/', response=List[GrossesseOut])
def list_grossesses(request, statut: Optional[str] = None):
    qs = Grossesse.objects.select_related('patiente')
    if statut:
        qs = qs.filter(statut=statut)
    return qs


@router.post('/', response=GrossesseOut)
def creer_grossesse(request, payload: GrossesseIn):
    return Grossesse.objects.create(**payload.dict())


@router.get('/{grossesse_id}', response=GrossesseOut)
def get_grossesse(request, grossesse_id: int):
    return get_object_or_404(Grossesse, id=grossesse_id)


@router.get('/stats/maternite')
def stats_maternite(request):
    from django.utils import timezone
    today = timezone.now().date()
    return {
        'grossesses_en_cours': Grossesse.objects.filter(statut='En cours').count(),
        'accouchements_mois': Accouchement.objects.filter(
            date_heure__month=today.month, date_heure__year=today.year
        ).count(),
        'terme_proche': Grossesse.objects.filter(
            statut='En cours',
            date_terme_prevue__lte=today + __import__('datetime').timedelta(days=14)
        ).count(),
    }
