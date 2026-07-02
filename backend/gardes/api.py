from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import date, datetime, time
from django.utils import timezone
from .models import PlanningGarde, TypeGarde, DisponibiliteMedecin, CongesAbsence

router = Router(tags=['Gardes & Plannings'])


class TypeGardeOut(Schema):
    id: int
    nom: str
    description: str
    duree_heures: int
    coefficient_paiement: float


class PlanningGardeIn(Schema):
    personnel_id: int
    type_garde_id: int
    date_debut: datetime
    date_fin: datetime
    lieu: str = ''
    observations: str = ''


class PlanningGardeOut(Schema):
    id: int
    personnel_id: int
    type_garde_id: int
    date_debut: datetime
    date_fin: datetime
    statut: str
    lieu: str
    observations: str


class DisponibiliteIn(Schema):
    medicecin_id: int
    date: date
    heure_debut: time
    heure_fin: time
    duree_consultation_minutes: int = 30
    exceptionnelle: bool = False
    motif_exception: str = ''


class DisponibiliteOut(Schema):
    id: int
    medicecin_id: int
    date: date
    heure_debut: time
    heure_fin: time
    creneaux_disponibles: int


@router.get('/types-garde/', response=List[TypeGardeOut])
def list_types_garde(request):
    return TypeGarde.objects.all()


@router.get('/planning/', response=List[PlanningGardeOut])
def list_planning_garde(
    request,
    personnel_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    statut: Optional[str] = None
):
    qs = PlanningGarde.objects.select_related('type_garde').all()
    
    if personnel_id:
        qs = qs.filter(personnel_id=personnel_id)
    if date_from:
        qs = qs.filter(date_debut__gte=date_from)
    if date_to:
        qs = qs.filter(date_fin__lte=date_to)
    if statut:
        qs = qs.filter(statut=statut)
    
    return qs.order_by('date_debut')


@router.post('/planning/', response=PlanningGardeOut)
def create_planning_garde(request, payload: PlanningGardeIn):
    """Créer un nouveau planning de garde."""
    planning = PlanningGarde.objects.create(**payload.dict())
    return planning


@router.put('/planning/{planning_id}/confirm')
def confirm_planning(request, planning_id: int):
    """Confirmer un planning de garde."""
    planning = get_object_or_404(PlanningGarde, id=planning_id)
    planning.confirmer()
    return {'success': True}


@router.put('/planning/{planning_id}/cancel')
def cancel_planning(request, planning_id: int, motif: str = ''):
    """Annuler un planning de garde."""
    planning = get_object_or_404(PlanningGarde, id=planning_id)
    planning.annuler(motif)
    return {'success': True}


@router.get('/disponibilites/', response=List[DisponibiliteOut])
def list_disponibilites(
    request,
    medecin_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    qs = DisponibiliteMedecin.objects.all()
    
    if medecin_id:
        qs = qs.filter(medicecin_id=medecin_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    
    return qs.order_by('date', 'heure_debut')


@router.post('/disponibilites/', response=DisponibiliteOut)
def create_disponibilite(request, payload: DisponibiliteIn):
    """Créer une disponibilité pour rendez-vous."""
    disponibilite = DisponibiliteMedecin.objects.create(**payload.dict())
    disponibilite.calculer_creneaux()
    return disponibilite


@router.get('/creneaux-libres/{medecin_id}')
def get_creneaux_libres(
    request,
    medecin_id: int,
    date: date,
    duree: int = 30
):
    """
    Obtenir les créneaux libres pour un médecin à une date donnée.
    Retourne une liste de créneaux horaires disponibles.
    """
    disponibilites = DisponibiliteMedecin.objects.filter(
        medicecin_id=medecin_id,
        date=date,
        exceptionnelle=False
    )
    
    creneaux = []
    for disp in disponibilites:
        # Générer les créneaux entre heure_debut et heure_fin
        current_time = disp.heure_debut
        while current_time < disp.heure_fin:
            # Vérifier si le créneau est déjà réservé (à implémenter)
            creneaux.append({
                'heure_debut': current_time.isoformat(),
                'heure_fin': (current_time + timezone.timedelta(minutes=duree)).isoformat(),
                'disponible': True,
            })
            current_time = current_time + timezone.timedelta(minutes=duree)
    
    return creneaux


class CongesAbsenceOut(Schema):
    id: int
    personnel_id: int
    type_absence: str
    date_debut: date
    date_fin: date
    statut: str
    motif: str


@router.get('/conges/', response=List[CongesAbsenceOut])
def list_conges(
    request,
    personnel_id: Optional[int] = None,
    statut: Optional[str] = None
):
    qs = CongesAbsence.objects.all()
    if personnel_id:
        qs = qs.filter(personnel_id=personnel_id)
    if statut:
        qs = qs.filter(statut=statut)
    return qs
