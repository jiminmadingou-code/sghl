from ninja import Router, Schema
from typing import List, Optional
from datetime import date
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Medicament, LotMedicament, MouvementStock

router = Router(tags=['Pharmacie'])


class MedicamentIn(Schema):
    nom: str
    categorie: str
    unite: str = 'comprimé'
    seuil_alerte: int = 50


class MedicamentOut(Schema):
    id: int
    nom: str
    categorie: str
    unite: str
    seuil_alerte: int


class LotIn(Schema):
    medicament_id: int
    numero_lot: str
    quantite: int
    date_peremption: date


class LotOut(Schema):
    id: int
    medicament_id: int
    numero_lot: str
    quantite: int
    date_peremption: date
    statut: str


class MouvementIn(Schema):
    lot_id: int
    type_mouvement: str
    quantite: int
    motif: str = ''


@router.get('/medicaments/', response=List[MedicamentOut])
def list_medicaments(request, search: Optional[str] = None):
    qs = Medicament.objects.all()
    if search:
        qs = qs.filter(nom__icontains=search)
    return qs


@router.post('/medicaments/', response=MedicamentOut)
def create_medicament(request, payload: MedicamentIn):
    return Medicament.objects.create(**payload.dict())


@router.put('/medicaments/{med_id}', response=MedicamentOut)
def update_medicament(request, med_id: int, payload: MedicamentIn):
    med = get_object_or_404(Medicament, id=med_id)
    for k, v in payload.dict().items():
        setattr(med, k, v)
    med.save()
    return med


@router.get('/stocks/', response=List[LotOut])
def list_stocks(request, medicament_id: Optional[int] = None, statut: Optional[str] = None):
    qs = LotMedicament.objects.select_related('medicament').all()
    if medicament_id:
        qs = qs.filter(medicament_id=medicament_id)
    return [l for l in qs if not statut or l.statut == statut]


@router.post('/stocks/', response=LotOut)
def create_lot(request, payload: LotIn):
    with transaction.atomic():
        lot = LotMedicament.objects.create(**payload.dict())
        try:
            personnel = request.user.personnel
        except Exception:
            personnel = None
        if personnel:
            MouvementStock.objects.create(
                lot=lot, type_mouvement='Entrée',
                quantite=payload.quantite,
                motif='Entrée initiale de stock',
                created_by=personnel
            )
    return lot


@router.post('/mouvements/')
def enregistrer_mouvement(request, payload: MouvementIn):
    lot = get_object_or_404(LotMedicament, id=payload.lot_id)
    try:
        personnel = request.user.personnel
    except Exception:
        from ninja.errors import HttpError
        raise HttpError(403, 'Profil pharmacien requis')
    with transaction.atomic():
        if payload.type_mouvement == 'Sortie':
            if lot.quantite < payload.quantite:
                from ninja.errors import HttpError
                raise HttpError(400, f'Stock insuffisant: {lot.quantite} disponibles')
            lot.quantite -= payload.quantite
        elif payload.type_mouvement == 'Entrée':
            lot.quantite += payload.quantite
        else:
            lot.quantite += payload.quantite  # Ajustement
        lot.save()
        MouvementStock.objects.create(
            lot=lot, type_mouvement=payload.type_mouvement,
            quantite=payload.quantite, motif=payload.motif,
            created_by=personnel
        )
    return {'success': True, 'nouveau_stock': lot.quantite, 'statut': lot.statut}


@router.get('/alertes/')
def alertes_stock(request):
    lots = LotMedicament.objects.select_related('medicament').all()
    return [
        {
            'id': l.id, 'medicament': l.medicament.nom,
            'quantite': l.quantite, 'seuil': l.medicament.seuil_alerte,
            'statut': l.statut, 'peremption': str(l.date_peremption),
            'lot': l.numero_lot
        }
        for l in lots if l.statut != 'Normal'
    ]


@router.get('/mouvements/{lot_id}')
def historique_mouvements(request, lot_id: int):
    mouvements = MouvementStock.objects.filter(lot_id=lot_id).select_related('created_by')
    return [
        {
            'id': m.id, 'type': m.type_mouvement, 'quantite': m.quantite,
            'motif': m.motif, 'date': m.created_at.isoformat(),
            'par': str(m.created_by)
        }
        for m in mouvements
    ]


@router.get('/inventaire/')
def inventaire_global(request):
    """Inventaire complet avec valeur de stock."""
    from django.db.models import Sum
    medicaments = Medicament.objects.prefetch_related('lots').all()
    result = []
    for med in medicaments:
        stock_total = med.lots.aggregate(total=Sum('quantite'))['total'] or 0
        lots_alerte = [l for l in med.lots.all() if l.statut != 'Normal']
        result.append({
            'id': med.id, 'nom': med.nom, 'categorie': med.categorie,
            'unite': med.unite, 'stock_total': stock_total,
            'seuil_alerte': med.seuil_alerte,
            'statut': 'Rupture' if stock_total == 0 else ('Alerte' if lots_alerte else 'Normal'),
            'nb_lots': med.lots.count()
        })
    return result
