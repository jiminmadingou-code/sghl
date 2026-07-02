from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime
from .models import ExamenLaboratoire

router = Router(tags=['Laboratoire'])

class ExamenIn(Schema):
    patient_id: int
    prescripteur_id: int
    type_examen: str
    priorite: str = 'Normal'

class ExamenOut(Schema):
    id: int
    patient_id: int
    type_examen: str
    priorite: str
    statut: str
    resultat: str
    date_prescription: datetime

@router.get('/', response=List[ExamenOut])
def list_examens(request, statut: Optional[str] = None, priorite: Optional[str] = None):
    qs = ExamenLaboratoire.objects.all()
    if statut:
        qs = qs.filter(statut=statut)
    if priorite:
        qs = qs.filter(priorite=priorite)
    return qs

@router.post('/', response=ExamenOut)
def create_examen(request, payload: ExamenIn):
    return ExamenLaboratoire.objects.create(**payload.dict())

@router.patch('/{examen_id}/avancer')
def avancer_workflow(request, examen_id: int):
    workflow = ['Commande', 'Prélèvement', 'Affectation', 'Saisie résultats', 'Validé', 'Publié']
    examen = get_object_or_404(ExamenLaboratoire, id=examen_id)
    idx = workflow.index(examen.statut)
    if idx < len(workflow) - 1:
        examen.statut = workflow[idx + 1]
        examen.save()
    return {'statut': examen.statut}

@router.patch('/{examen_id}/resultat')
def saisir_resultat(request, examen_id: int, resultat: str):
    examen = get_object_or_404(ExamenLaboratoire, id=examen_id)
    if examen.resultat_immutable:
        from ninja.errors import HttpError
        raise HttpError(403, 'Résultat validé — immuable')
    examen.resultat = resultat
    examen.save()
    return {'success': True}


@router.post('/{examen_id}/upload-document')
def upload_document_labo(request, examen_id: int):
    """Upload d'un document lié à un examen avec scan antivirus."""
    from ninja.errors import HttpError
    from core.antivirus import require_clean_file
    examen = get_object_or_404(ExamenLaboratoire, id=examen_id)
    files = request._request.FILES
    if 'document' not in files:
        raise HttpError(400, 'Aucun fichier fourni')
    f = files['document']
    # Scan antivirus obligatoire avant tout stockage
    scan_result = require_clean_file(f, f.name, f.content_type, context='documents')
    return {
        'message': 'Document validé et accepté',
        'filename': f.name,
        'hash': scan_result.file_hash,
        'mime': scan_result.mime_detected,
        'size': scan_result.file_size,
    }

@router.patch('/{examen_id}/valider', response=ExamenOut)
def valider_examen(request, examen_id: int):
    from ninja.errors import HttpError
    from audit.models import AuditTrail
    examen = get_object_or_404(ExamenLaboratoire, id=examen_id)
    
    try:
        biologiste = request.user.personnel
        if not biologiste.est_biologiste:
            raise HttpError(403, 'Seul un biologiste peut valider un examen')
    except Exception:
        raise HttpError(403, 'Profil biologiste requis pour la validation')
        
    old_status = examen.statut
    examen.valider(biologiste)
    
    AuditTrail.log(
        request=request,
        action_type='VALIDATE',
        model_name='ExamenLaboratoire',
        object_id=examen.id,
        old_value={'statut': old_status},
        new_value={'statut': examen.statut, 'valide_par': biologiste.full_name},
        details={'patient_id': examen.patient_id}
    )
    
    return examen

@router.get('/{examen_id}/pdf')
def telecharger_resultat_pdf(request, examen_id: int):
    from django.http import HttpResponse
    import json
    examen = get_object_or_404(ExamenLaboratoire, id=examen_id)
    
    try:
        resultats_list = json.loads(examen.resultat)
        if not isinstance(resultats_list, list):
            resultats_list = [resultats_list]
    except Exception:
        resultats_list = [{
            'parameter': examen.type_examen,
            'value': examen.resultat or 'Non renseigné',
            'unit': '',
            'normal_range': 'N/A',
            'abnormal': False
        }]
        
    from .pdf_generator import ResultatLaboratoirePDF
    pdf_bytes = ResultatLaboratoirePDF.generate(examen, resultats_list, commentaires="Résultats validés conformes.")
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resultats_labo_{examen_id}.pdf"'
    return response
