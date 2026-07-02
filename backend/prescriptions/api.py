from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import date, datetime
from .models import Prescription, LignePrescription

router = Router(tags=['Prescriptions'])


class LigneIn(Schema):
    medicament_id: int
    posologie: str
    duree_jours: int = 7
    quantite: int = 1
    instructions: str = ''


class PrescriptionIn(Schema):
    consultation_id: int
    patient_id: int
    date_validite: Optional[date] = None
    notes: str = ''
    lignes: List[LigneIn]


class LigneOut(Schema):
    id: int
    medicament_id: int
    posologie: str
    duree_jours: int
    quantite: int
    dispensee: bool


class PrescriptionOut(Schema):
    id: int
    consultation_id: int
    patient_id: int
    medecin_id: int
    statut: str
    verrouille: bool
    date_prescription: datetime
    lignes: List[LigneOut]


@router.get('/', response=List[PrescriptionOut])
def list_prescriptions(request, patient_id: Optional[int] = None, statut: Optional[str] = None):
    qs = Prescription.objects.prefetch_related('lignes')
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    if statut:
        qs = qs.filter(statut=statut)
    return qs


@router.post('/', response=PrescriptionOut)
def create_prescription(request, payload: PrescriptionIn):
    from ninja.errors import HttpError
    # Récupérer le médecin depuis le token JWT
    try:
        medecin = request.user.personnel
    except Exception:
        raise HttpError(403, 'Profil médecin requis')

    lignes_data = payload.dict().pop('lignes')
    prescription = Prescription.objects.create(
        medecin=medecin,
        **{k: v for k, v in payload.dict().items() if k != 'lignes'}
    )
    for ligne in lignes_data:
        LignePrescription.objects.create(prescription=prescription, **ligne)
    return Prescription.objects.prefetch_related('lignes').get(pk=prescription.pk)


@router.patch('/{prescription_id}/valider', response=PrescriptionOut)
def valider_prescription(request, prescription_id: int):
    from ninja.errors import HttpError
    prescription = get_object_or_404(Prescription, id=prescription_id)
    try:
        medecin = request.user.personnel
        if not medecin.est_medecin:
            raise HttpError(403, 'Seul un médecin peut valider une prescription')
    except Exception:
        raise HttpError(403, 'Profil médecin requis')
    prescription.valider(medecin)
    return Prescription.objects.prefetch_related('lignes').get(pk=prescription.pk)


@router.patch('/{prescription_id}/dispenser/{ligne_id}')
def dispenser_ligne(request, prescription_id: int, ligne_id: int):
    from ninja.errors import HttpError
    ligne = get_object_or_404(LignePrescription, id=ligne_id, prescription_id=prescription_id)
    if not ligne.prescription.verrouille:
        raise HttpError(400, 'La prescription doit être validée avant dispense')
    try:
        pharmacien = request.user.personnel
    except Exception:
        raise HttpError(403, 'Profil pharmacien requis')
    ligne.dispenser(pharmacien)
    return {'success': True, 'stock_decremente': True}


@router.get('/{prescription_id}/pdf')
def telecharger_pdf(request, prescription_id: int):
    """Générer et télécharger le PDF de l'ordonnance."""
    from django.http import HttpResponse
    prescription = get_object_or_404(Prescription, id=prescription_id)
    from .pdf_generator import OrdonnancePDF
    pdf_bytes = OrdonnancePDF.generate(prescription)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ordonnance_{prescription_id}.pdf"'
    return response
