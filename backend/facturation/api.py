from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from decimal import Decimal
from .models import Facture, Paiement

router = Router(tags=['Facturation'])

class FactureIn(Schema):
    patient_id: int
    type_facture: str
    montant_total: Decimal
    notes: str = ''

class FactureOut(Schema):
    id: int
    patient_id: int
    type_facture: str
    montant_total: Decimal
    montant_paye: Decimal
    statut: str
    date_emission: str

class PaiementIn(Schema):
    montant: Decimal
    mode_paiement: str
    reference: str = ''

@router.get('/', response=List[FactureOut])
def list_factures(request, statut: Optional[str] = None):
    qs = Facture.objects.prefetch_related('paiements')
    if statut:
        qs = qs.filter(statut=statut)
    return qs

@router.post('/', response=FactureOut)
def create_facture(request, payload: FactureIn):
    return Facture.objects.create(**payload.dict())

@router.get('/{facture_id}/pdf')
def telecharger_facture_pdf(request, facture_id: int):
    from django.http import HttpResponse
    from .pdf_generator import FacturePDF
    facture = get_object_or_404(Facture.objects.prefetch_related('paiements', 'patient'), id=facture_id)
    pdf_bytes = FacturePDF.generate(facture)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture_id}.pdf"'
    return response


@router.post('/{facture_id}/paiement/')
def ajouter_paiement(request, facture_id: int, payload: PaiementIn):
    facture = get_object_or_404(Facture, id=facture_id)
    Paiement.objects.create(facture=facture, **payload.dict())
    facture.update_statut()
    return {'statut': facture.statut, 'solde': float(facture.solde)}
