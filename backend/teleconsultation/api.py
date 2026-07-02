from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import SessionTeleconsultation

router = Router(tags=['Téléconsultation'])


class SessionIn(Schema):
    patient_id: int
    medecin_id: int
    date_heure_prevue: datetime
    motif: str
    rendez_vous_id: Optional[int] = None


class SessionOut(Schema):
    id: int
    patient_id: int
    medecin_id: int
    date_heure_prevue: datetime
    statut: str
    motif: str
    lien_patient: str
    token_session: str
    duree_minutes: Optional[int]


@router.get('/', response=List[SessionOut])
def list_sessions(request, statut: Optional[str] = None):
    qs = SessionTeleconsultation.objects.select_related('patient', 'medecin')
    if statut:
        qs = qs.filter(statut=statut)
    return qs


@router.post('/', response=SessionOut)
def creer_session(request, payload: SessionIn):
    session = SessionTeleconsultation.objects.create(**payload.dict())
    session.generer_liens()
    return session


@router.post('/{session_id}/demarrer')
def demarrer_session(request, session_id: int):
    session = get_object_or_404(SessionTeleconsultation, id=session_id)
    session.demarrer()
    return {'success': True, 'lien_medecin': session.lien_medecin}


@router.post('/{session_id}/terminer')
def terminer_session(request, session_id: int, notes: str = '', diagnostic: str = ''):
    session = get_object_or_404(SessionTeleconsultation, id=session_id)
    session.terminer(notes, diagnostic)
    return {'success': True, 'duree_minutes': session.duree_minutes}
