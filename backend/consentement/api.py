from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import date
from .models import ConsentementPatient, DemandeAccesDonnees

router = Router(tags=['Consentement RGPD'])


class ConsentementIn(Schema):
    patient_id: int
    type_consentement: str
    date_expiration: Optional[date] = None
    version_document: str = '1.0'
    notes: str = ''


class ConsentementOut(Schema):
    id: int
    patient_id: int
    type_consentement: str
    statut: str
    est_actif: bool
    date_consentement: str
    version_document: str


class DemandeIn(Schema):
    patient_id: int
    type_demande: str
    description: str = ''


class DemandeOut(Schema):
    id: int
    patient_id: int
    type_demande: str
    statut: str
    date_demande: str


@router.get('/consentements/', response=List[ConsentementOut])
def list_consentements(request, patient_id: Optional[int] = None):
    qs = ConsentementPatient.objects.all()
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    return [
        {**c.__dict__, 'est_actif': c.est_actif, 'date_consentement': str(c.date_consentement)}
        for c in qs
    ]


@router.post('/consentements/', response=ConsentementOut)
def enregistrer_consentement(request, payload: ConsentementIn):
    from ninja.errors import HttpError
    try:
        personnel = request.user.personnel
    except Exception:
        raise HttpError(403, 'Authentification requise')
    c, _ = ConsentementPatient.objects.update_or_create(
        patient_id=payload.patient_id,
        type_consentement=payload.type_consentement,
        version_document=payload.version_document,
        defaults={
            'statut': 'accordé',
            'date_expiration': payload.date_expiration,
            'recueilli_par': personnel,
            'notes': payload.notes,
        }
    )
    return {**c.__dict__, 'est_actif': c.est_actif, 'date_consentement': str(c.date_consentement)}


@router.patch('/consentements/{consentement_id}/retirer')
def retirer_consentement(request, consentement_id: int, notes: str = ''):
    c = get_object_or_404(ConsentementPatient, id=consentement_id)
    c.retirer(notes)
    return {'success': True, 'statut': c.statut}


@router.get('/demandes/', response=List[DemandeOut])
def list_demandes(request, statut: Optional[str] = None):
    qs = DemandeAccesDonnees.objects.all()
    if statut:
        qs = qs.filter(statut=statut)
    return [
        {**d.__dict__, 'date_demande': str(d.date_demande)} for d in qs
    ]


@router.post('/demandes/', response=DemandeOut)
def creer_demande(request, payload: DemandeIn):
    d = DemandeAccesDonnees.objects.create(**payload.dict())
    return {**d.__dict__, 'date_demande': str(d.date_demande)}


@router.patch('/demandes/{demande_id}/traiter')
def traiter_demande(request, demande_id: int, reponse: str, statut: str = 'Traitée'):
    from ninja.errors import HttpError
    demande = get_object_or_404(DemandeAccesDonnees, id=demande_id)
    try:
        personnel = request.user.personnel
    except Exception:
        raise HttpError(403, 'Authentification requise')
    demande.traiter(personnel, reponse, statut)
    return {'success': True}
