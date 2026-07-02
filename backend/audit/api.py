from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime
from .models import AuditTrail

router = Router(tags=['Audit & Traçabilité'])

class AuditEntryOut(Schema):
    id: int
    timestamp: datetime
    user_id: Optional[int]
    user_email: Optional[str]
    action_type: str
    model_name: str
    object_id: int
    old_value: Optional[dict]
    new_value: Optional[dict]
    ip_address: Optional[str]
    details: Optional[dict]

class AuditFilter(Schema):
    model_name: Optional[str] = None
    object_id: Optional[int] = None
    action_type: Optional[str] = None
    user_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

@router.get('/', response=List[AuditEntryOut])
def list_audit_logs(request, model_name: Optional[str] = None, 
                    object_id: Optional[int] = None,
                    action_type: Optional[str] = None,
                    user_id: Optional[int] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None):
    """List audit logs with optional filters."""
    qs = AuditTrail.objects.all()
    
    if model_name:
        qs = qs.filter(model_name__icontains=model_name)
    if object_id:
        qs = qs.filter(object_id=object_id)
    if action_type:
        qs = qs.filter(action_type=action_type)
    if user_id:
        qs = qs.filter(user_id=user_id)
    if date_from:
        qs = qs.filter(timestamp__gte=date_from)
    if date_to:
        qs = qs.filter(timestamp__lte=date_to)
    
    return qs[:1000]  # Limit to 1000 entries

@router.get('/{audit_id}', response=AuditEntryOut)
def get_audit_log(request, audit_id: int):
    """Get specific audit log entry."""
    return get_object_or_404(AuditTrail, id=audit_id)

@router.get('/stats/summary')
def audit_summary(request):
    """Get audit trail summary statistics."""
    from django.db.models import Count, Q
    
    total = AuditTrail.objects.count()
    today = AuditTrail.objects.filter(timestamp__date=datetime.now().date()).count()
    by_action = AuditTrail.objects.values('action_type').annotate(count=Count('id'))
    by_model = AuditTrail.objects.values('model_name').annotate(count=Count('id'))
    
    return {
        'total_entries': total,
        'entries_today': today,
        'by_action_type': list(by_action),
        'by_model': list(by_model),
    }
