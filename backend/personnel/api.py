from ninja import Router, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Personnel, SessionLog

router = Router(tags=['Personnel & RH'])


class PersonnelIn(Schema):
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    service: str = ''
    telephone: str = ''
    password: str


class PersonnelOut(Schema):
    id: int
    full_name: str
    role: str
    service: str
    email: str
    actif: bool
    mfa_active: bool
    last_login_at: Optional[str] = None


class PersonnelUpdateIn(Schema):
    role: Optional[str] = None
    service: Optional[str] = None
    telephone: Optional[str] = None
    actif: Optional[bool] = None


@router.get('/', response=List[PersonnelOut])
def list_personnel(request, role: Optional[str] = None, actif: bool = True):
    qs = Personnel.objects.select_related('user').filter(actif=actif)
    if role:
        qs = qs.filter(role=role)
    return qs


@router.post('/', response=PersonnelOut)
def create_personnel(request, payload: PersonnelIn):
    from ninja.errors import HttpError
    try:
        requester = request.user.personnel
        if not requester.est_admin:
            raise HttpError(403, 'Droits administrateur requis')
    except Exception:
        raise HttpError(403, 'Accès refusé')
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(409, 'Nom d\'utilisateur déjà pris')
    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password=payload.password
    )
    personnel = Personnel.objects.create(
        user=user, role=payload.role,
        service=payload.service, telephone=payload.telephone
    )
    return personnel


@router.get('/{personnel_id}', response=PersonnelOut)
def get_personnel(request, personnel_id: int):
    return get_object_or_404(Personnel, id=personnel_id)


@router.patch('/{personnel_id}', response=PersonnelOut)
def update_personnel(request, personnel_id: int, payload: PersonnelUpdateIn):
    personnel = get_object_or_404(Personnel, id=personnel_id)
    data = {k: v for k, v in payload.dict().items() if v is not None}
    for k, v in data.items():
        setattr(personnel, k, v)
    personnel.save()
    return personnel


@router.delete('/{personnel_id}')
def desactiver_personnel(request, personnel_id: int):
    personnel = get_object_or_404(Personnel, id=personnel_id)
    personnel.actif = False
    personnel.save()
    return {'success': True}


@router.get('/roles/liste')
def liste_roles(request):
    return [{'code': r[0], 'label': r[1]} for r in Personnel.ROLES]


@router.get('/sessions/journal')
def journal_sessions(request, personnel_id: Optional[int] = None):
    qs = SessionLog.objects.select_related('personnel').order_by('-date_debut')
    if personnel_id:
        qs = qs.filter(personnel_id=personnel_id)
    return [
        {
            'id': s.id, 'personnel': str(s.personnel),
            'debut': s.date_debut.isoformat(),
            'fin': s.date_fin.isoformat() if s.date_fin else None,
            'ip': s.ip_address, 'device': s.device_type
        }
        for s in qs[:100]
    ]


@router.get('/stats/rh')
def stats_rh(request):
    from django.db.models import Count
    par_role = Personnel.objects.filter(actif=True).values('role').annotate(total=Count('id'))
    return {
        'total_actifs': Personnel.objects.filter(actif=True).count(),
        'total_inactifs': Personnel.objects.filter(actif=False).count(),
        'par_role': list(par_role),
        'mfa_actif': Personnel.objects.filter(mfa_active=True).count(),
    }
