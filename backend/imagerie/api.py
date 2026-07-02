from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import ExamenImagerie, Modalite

router = Router(tags=['Imagerie'])


class ExamenImagerieIn(Schema):
    patient_id: int
    modalite_id: int
    region_anatomique: str
    indication_clinique: str
    urgence: str = 'Normal'
    hospitalisation_id: Optional[int] = None


class ExamenImagerieOut(Schema):
    id: int
    patient_id: int
    modalite_id: int
    region_anatomique: str
    urgence: str
    statut: str
    date_prescription: datetime
    compte_rendu: str
    conclusion: str
    verrouille: bool


@router.get('/', response=List[ExamenImagerieOut])
def list_examens(request, statut: Optional[str] = None, patient_id: Optional[int] = None):
    qs = ExamenImagerie.objects.select_related('patient', 'modalite')
    if statut:
        qs = qs.filter(statut=statut)
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    return qs


@router.post('/', response=ExamenImagerieOut)
def prescrire_examen(request, payload: ExamenImagerieIn):
    from personnel.models import Personnel
    medecin = Personnel.objects.get(user=request.user)
    return ExamenImagerie.objects.create(**payload.dict(), prescripteur=medecin)


@router.patch('/{examen_id}/compte-rendu')
def saisir_compte_rendu(request, examen_id: int, compte_rendu: str, conclusion: str):
    examen = get_object_or_404(ExamenImagerie, id=examen_id)
    if examen.verrouille:
        return {'error': 'Examen verrouillé'}
    from django.utils import timezone
    examen.compte_rendu = compte_rendu
    examen.conclusion = conclusion
    examen.statut = 'Interprété'
    examen.date_interpretation = timezone.now()
    examen.save()
    return {'success': True}


@router.post('/{examen_id}/valider')
def valider_examen(request, examen_id: int):
    from personnel.models import Personnel
    radiologue = get_object_or_404(Personnel, user=request.user)
    examen = get_object_or_404(ExamenImagerie, id=examen_id)
    examen.valider(radiologue)
    return {'success': True}
