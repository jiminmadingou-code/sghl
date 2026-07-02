from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime, date
from .models import RendezVous

router = Router(tags=['Rendez-vous'])


class RendezVousIn(Schema):
    patient_id: int
    medecin_id: int
    date_heure: datetime
    duree_minutes: int = 30
    type_rdv: str = 'Consultation'
    motif: str
    notes: str = ''


class RendezVousOut(Schema):
    id: int
    patient_id: int
    medecin_id: int
    date_heure: datetime
    duree_minutes: int
    type_rdv: str
    motif: str
    statut: str
    confirmation_envoyee: bool


@router.get('/', response=List[RendezVousOut])
def list_rdv(request, medecin_id: Optional[int] = None, patient_id: Optional[int] = None,
             statut: Optional[str] = None, date_debut: Optional[date] = None, date_fin: Optional[date] = None):
    qs = RendezVous.objects.select_related('patient', 'medecin')
    if medecin_id:
        qs = qs.filter(medecin_id=medecin_id)
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    if statut:
        qs = qs.filter(statut=statut)
    if date_debut:
        qs = qs.filter(date_heure__date__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_heure__date__lte=date_fin)
    return qs


@router.post('/', response=RendezVousOut)
def create_rdv(request, payload: RendezVousIn):
    # Vérifier disponibilité médecin (pas de chevauchement)
    from django.db.models import Q
    from datetime import timedelta
    fin_rdv = payload.date_heure + timedelta(minutes=payload.duree_minutes)
    chevauchement = RendezVous.objects.filter(
        medecin_id=payload.medecin_id,
        statut__in=['En attente', 'Confirmé']
    ).filter(
        Q(date_heure__lt=fin_rdv) & Q(date_heure__gte=payload.date_heure)
    ).exists()
    if chevauchement:
        from ninja.errors import HttpError
        raise HttpError(409, 'Créneau déjà occupé pour ce médecin')
    rdv = RendezVous.objects.create(**payload.dict())
    rdv.confirmer()
    return rdv


@router.patch('/{rdv_id}/confirmer', response=RendezVousOut)
def confirmer_rdv(request, rdv_id: int):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.confirmer()
    return rdv


@router.patch('/{rdv_id}/annuler', response=RendezVousOut)
def annuler_rdv(request, rdv_id: int, motif: str = ''):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.annuler(motif)
    return rdv


@router.patch('/{rdv_id}/terminer', response=RendezVousOut)
def terminer_rdv(request, rdv_id: int):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'Terminé'
    rdv.save()
    return rdv


@router.get('/creneaux-libres/{medecin_id}', response=List[datetime])
def creneaux_libres(request, medecin_id: int, date_rdv: date):
    """Retourner les créneaux libres d'un médecin pour une date donnée."""
    from gardes.models import DisponibiliteMedecin
    from datetime import timedelta, datetime as dt
    dispos = DisponibiliteMedecin.objects.filter(medecin_id=medecin_id, date=date_rdv)
    creneaux = []
    for dispo in dispos:
        current = dt.combine(date_rdv, dispo.heure_debut)
        fin = dt.combine(date_rdv, dispo.heure_fin)
        while current + timedelta(minutes=dispo.duree_consultation_minutes) <= fin:
            # Vérifier si ce créneau est libre
            occupe = RendezVous.objects.filter(
                medecin_id=medecin_id,
                date_heure=current,
                statut__in=['En attente', 'Confirmé']
            ).exists()
            if not occupe:
                creneaux.append(current)
            current += timedelta(minutes=dispo.duree_consultation_minutes)
    return creneaux
