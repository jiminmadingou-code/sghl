from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime, date, time
from django.utils import timezone
from .models import TypeSoin, PlanificationSoins, ConstanteVitale, InterventionInfirmiere

router = Router(tags=['Soins & Infirmier'])


class TypeSoinIn(Schema):
    code: str
    nom: str
    description: str = ''
    duree_estimee_minutes: int = 15
    categorie: str = ''
    actif: bool = True


class TypeSoinOut(Schema):
    id: int
    code: str
    nom: str
    description: str
    duree_estimee_minutes: int
    categorie: str
    actif: bool


class PlanificationSoinsIn(Schema):
    hospitalisation_id: int
    type_soin_id: int
    date_heure_prevue: datetime
    duree_prevue_minutes: int = 15
    priorite: str = 'Normale'
    infirmier_assigne_id: Optional[int] = None
    instructions: str = ''


class PlanificationSoinsOut(Schema):
    id: int
    type_soin: str
    hospitalisation_id: int
    date_heure_prevue: datetime
    statut: str
    priorite: str
    infirmier_assigne_id: Optional[int]
    notes_realisation: str = ''
    alerte_omission: bool = False


class ConstanteVitaleIn(Schema):
    hospitalisation_id: int
    type_constante: str
    valeur: float
    notes: str = ''
    seuil_bas: Optional[float] = None
    seuil_haut: Optional[float] = None


class ConstanteVitaleOut(Schema):
    id: int
    hospitalisation_id: int
    type_constante: str
    valeur: float
    unite: str
    date_mesure: datetime
    alerte_seuil: bool
    notes: str


class InterventionIn(Schema):
    hospitalisation_id: int
    type_intervention: str
    description: str
    medicaments_administres: List[dict] = []
    reponse_patient: str = ''


@router.get('/types-soins/', response=List[TypeSoinOut])
def list_types_soin(request):
    return TypeSoin.objects.filter(actif=True)


@router.post('/types-soins/', response=TypeSoinOut)
def create_type_soin(request, payload: TypeSoinIn):
    return TypeSoin.objects.create(**payload.dict())


@router.get('/planning/', response=List[PlanificationSoinsOut])
def list_planning_soins(
    request,
    hospitalisation_id: Optional[int] = None,
    statut: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    qs = PlanificationSoins.objects.select_related('type_soin').all()
    
    if hospitalisation_id:
        qs = qs.filter(hospitalisation_id=hospitalisation_id)
    if statut:
        qs = qs.filter(statut=statut)
    if date_from:
        qs = qs.filter(date_heure_prevue__gte=date_from)
    if date_to:
        qs = qs.filter(date_heure_prevue__lte=date_to)
    
    return qs


@router.post('/planning/', response=PlanificationSoinsOut)
def create_planning_soin(request, payload: PlanificationSoinsIn):
    return PlanificationSoins.objects.create(**payload.dict())


@router.put('/planning/{soin_id}/realiser')
def marquer_soin_realise(request, soin_id: int, notes: str = ''):
    soin = get_object_or_404(PlanificationSoins, id=soin_id)
    # TODO: Récupérer l'infirmier depuis request.user
    soin.marquer_comme_realise(infirmier=None, notes=notes)
    return {'success': True, 'message': 'Soin marqué comme réalisé'}


@router.put('/planning/{soin_id}/omettre')
def marquer_soin_omis(request, soin_id: int):
    soin = get_object_or_404(PlanificationSoins, id=soin_id)
    soin.marquer_comme_omis()
    return {'success': True, 'message': 'Alerte d\'omission générée'}


@router.get('/constantes/{hospitalisation_id}', response=List[ConstanteVitaleOut])
def list_constantes_vitales(
    request,
    hospitalisation_id: int,
    type_constante: Optional[str] = None
):
    qs = ConstanteVitale.objects.filter(hospitalisation_id=hospitalisation_id)
    
    if type_constante:
        qs = qs.filter(type_constante=type_constante)
    
    return qs.order_by('-date_mesure')


@router.get('/constantes/{hospitalisation_id}/trend')
def get_trend_constantes(
    request,
    hospitalisation_id: int,
    type_constante: str,
    days: int = 7
):
    """Obtenir la tendance des constantes sur les derniers jours."""
    from django.utils import timezone
    from datetime import timedelta
    
    date_start = timezone.now() - timedelta(days=days)
    
    constantes = ConstanteVitale.objects.filter(
        hospitalisation_id=hospitalisation_id,
        type_constante=type_constante,
        date_mesure__gte=date_start
    ).order_by('date_mesure')
    
    return {
        'labels': [c.date_mesure.isoformat() for c in constantes],
        'values': [float(c.valeur) for c in constantes],
        'type': type_constante,
    }


@router.post('/constantes/', response=ConstanteVitaleOut)
def enregistrer_constante(request, payload: ConstanteVitaleIn):
    """Enregistrer une nouvelle constante vitale."""
    constante = ConstanteVitale.objects.create(**payload.dict())
    return constante


@router.get('/constantes/alertes')
def list_alertes_constantes(request):
    """Lister les constantes avec alertes de seuil."""
    return ConstanteVitale.objects.filter(alerte_seuil=True)


@router.post('/interventions/', response=InterventionIn)
def créer_intervention(request, payload: InterventionIn):
    """Créer une intervention infirmière."""
    return InterventionInfirmiere.objects.create(**payload.dict())


@router.get('/interventions/{hospitalisation_id}', response=List[InterventionIn])
def list_interventions(request, hospitalisation_id: int):
    """Lister les interventions pour une hospitalisation."""
    return InterventionInfirmiere.objects.filter(
        hospitalisation_id=hospitalisation_id
    ).order_by('-date_heure')
