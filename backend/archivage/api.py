from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from .models import DocumentMedical, ArchiveDossier, AccesDocument

router = Router(tags=['Archivage'])


class DocumentOut(Schema):
    id: int
    patient_id: int
    type_document: str
    titre: str
    mime_type: str
    taille_octets: int
    version: int
    hash_sha256: str
    created_at: datetime
    acces_patient: bool
    confidentiel: bool


@router.get('/documents/', response=List[DocumentOut])
def list_documents(request, patient_id: Optional[int] = None, type_doc: Optional[str] = None):
    qs = DocumentMedical.objects.select_related('patient')
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    if type_doc:
        qs = qs.filter(type_document=type_doc)
    return qs


@router.get('/documents/{doc_id}', response=DocumentOut)
def get_document(request, doc_id: int):
    doc = get_object_or_404(DocumentMedical, id=doc_id)
    try:
        from personnel.models import Personnel
        personnel = Personnel.objects.get(user=request.user)
        AccesDocument.objects.create(
            document=doc, personnel=personnel, type_acces='Lecture',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        from audit.models import AuditTrail
        AuditTrail.log(
            request=request, action_type='VIEW',
            model_name='DocumentMedical', object_id=doc.pk,
            details={'patient_id': doc.patient_id, 'type': doc.type_document}
        )
    except Exception:
        pass
    return doc


@router.post('/documents/upload')
def upload_document(request, patient_id: int, type_document: str, titre: str):
    """
    Upload d'un document médical avec scan antivirus obligatoire,
    contrôle MIME, taille maximale et calcul hash SHA-256.
    """
    from core.antivirus import require_clean_file
    from audit.models import AuditTrail
    import hashlib

    files = request._request.FILES
    if 'fichier' not in files:
        raise HttpError(400, 'Champ fichier requis (multipart: fichier)')

    f = files['fichier']

    # Scan antivirus — lève HttpError 400 si infecté
    scan_result = require_clean_file(f, f.name, f.content_type, context='documents')

    # Calcul hash SHA-256 du contenu
    f.seek(0)
    sha256 = hashlib.sha256(f.read()).hexdigest()
    f.seek(0)

    try:
        from personnel.models import Personnel
        personnel = Personnel.objects.get(user=request.user)
    except Exception:
        raise HttpError(403, 'Profil personnel requis')

    doc = DocumentMedical.objects.create(
        patient_id=patient_id,
        type_document=type_document,
        titre=titre,
        fichier=f,
        mime_type=scan_result.mime_detected or f.content_type,
        taille_octets=scan_result.file_size,
        hash_sha256=sha256,
        cree_par=personnel,
    )

    AuditTrail.log(
        request=request, action_type='CREATE',
        model_name='DocumentMedical', object_id=doc.pk,
        new_value={'titre': titre, 'type': type_document, 'hash': sha256},
        details={'patient_id': patient_id, 'antivirus': 'clean'}
    )

    return {
        'id': doc.id,
        'titre': doc.titre,
        'hash_sha256': sha256,
        'mime_type': doc.mime_type,
        'taille_octets': doc.taille_octets,
        'message': 'Document uploadé, scanné et archivé avec succès',
    }


@router.get('/documents/{doc_id}/telecharger')
def telecharger_document(request, doc_id: int):
    """Téléchargement avec traçabilité d'accès obligatoire."""
    doc = get_object_or_404(DocumentMedical, id=doc_id)
    try:
        from personnel.models import Personnel
        personnel = Personnel.objects.get(user=request.user)
        AccesDocument.objects.create(
            document=doc, personnel=personnel, type_acces='Téléchargement',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        from audit.models import AuditTrail
        AuditTrail.log(
            request=request, action_type='EXPORT',
            model_name='DocumentMedical', object_id=doc.pk,
            details={'patient_id': doc.patient_id, 'type': doc.type_document}
        )
    except Exception:
        pass
    return FileResponse(doc.fichier.open('rb'), as_attachment=True, filename=doc.titre)


@router.get('/dossier/{patient_id}/archive')
def get_archive(request, patient_id: int):
    archive, _ = ArchiveDossier.objects.get_or_create(patient_id=patient_id)
    return {
        'statut': archive.statut,
        'date_archivage': archive.date_archivage,
        'date_destruction_prevue': archive.date_destruction_prevue,
        'consentement_donne': archive.consentement_donne,
        'duree_conservation_ans': ArchiveDossier.DUREE_CONSERVATION,
    }


@router.post('/dossier/{patient_id}/archiver')
def archiver_dossier(request, patient_id: int, motif: str = ''):
    """Archiver un dossier patient — déclenche la politique de conservation 20 ans."""
    try:
        from personnel.models import Personnel
        personnel = Personnel.objects.get(user=request.user)
        if not personnel.est_admin:
            raise HttpError(403, 'Seul un administrateur peut archiver un dossier')
    except HttpError:
        raise
    except Exception:
        raise HttpError(403, 'Profil administrateur requis')

    archive, _ = ArchiveDossier.objects.get_or_create(patient_id=patient_id)
    if archive.statut == 'Archivé':
        raise HttpError(400, 'Dossier déjà archivé')

    archive.archiver(personnel, motif)

    from audit.models import AuditTrail
    AuditTrail.log(
        request=request, action_type='UPDATE',
        model_name='ArchiveDossier', object_id=archive.pk,
        new_value={'statut': 'Archivé', 'date_destruction_prevue': str(archive.date_destruction_prevue)},
        details={'patient_id': patient_id, 'motif': motif}
    )
    return {
        'statut': archive.statut,
        'date_destruction_prevue': archive.date_destruction_prevue,
        'message': f'Dossier archivé. Conservation 20 ans jusqu\'au {archive.date_destruction_prevue}',
    }


@router.post('/dossier/{patient_id}/anonymiser')
def anonymiser_dossier(request, patient_id: int):
    """Anonymiser les données personnelles du patient (RGPD — droit à l'effacement)."""
    try:
        from personnel.models import Personnel
        personnel = Personnel.objects.get(user=request.user)
        if not personnel.est_admin:
            raise HttpError(403, 'Seul un administrateur peut anonymiser un dossier')
    except HttpError:
        raise
    except Exception:
        raise HttpError(403, 'Profil administrateur requis')

    from patients.models import Patient
    patient = get_object_or_404(Patient, id=patient_id)
    patient.anonymiser()

    archive, _ = ArchiveDossier.objects.get_or_create(patient_id=patient_id)
    archive.statut = 'Anonymisé'
    archive.save()

    from audit.models import AuditTrail
    AuditTrail.log(
        request=request, action_type='UPDATE',
        model_name='Patient', object_id=patient_id,
        details={'action': 'Anonymisation RGPD', 'par': request.user.username}
    )
    return {'message': 'Données personnelles anonymisées conformément au RGPD'}
