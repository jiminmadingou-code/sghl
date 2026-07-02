from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from patients.models import Patient
from hospitalisations.models import Hospitalisation, Lit
from laboratoire.models import ExamenLaboratoire
from pharmacie.models import LotMedicament
from facturation.models import Facture
from django.core.cache import cache

router = Router(tags=['Dashboard & KPIs'])


class KPIData(Schema):
    key: str
    value: float
    label: str
    change_percent: Optional[float] = None


class DashboardSummary(Schema):
    patients_totaux: int
    patients_hospitalises: int
    hospitalisations_actives: int
    taux_occupation: float
    examens_en_attente: int
    examens_a_valider: int
    ordonnances_en_cours: int
    alertes_stock: int
    chiffre_affaires_jour: float
    chiffre_affaires_mois: float


@router.get('/summary', response=DashboardSummary)
def dashboard_summary(request):
    """Résumé global du dashboard."""
    cache_key = 'dashboard_summary'
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    # Calculer les KPIs
    patients_totaux = Patient.objects.count()
    patients_hospitalises = Patient.objects.filter(
        hospitalisations__statut='Actif'
    ).distinct().count()
    hospitalisations_actives = Hospitalisation.objects.filter(statut='Actif').count()
    
    # Taux d'occupation
    from hospitalisations.models import Lit
    lits_totaux = Lit.objects.filter(actif=True).count()
    lits_occupes = Lit.objects.filter(statut='Occupe').count()
    taux_occupation = (lits_occupes / lits_totaux * 100) if lits_totaux > 0 else 0
    
    # Laboratoire
    examens_en_attente = ExamenLaboratoire.objects.filter(statut='Commande').count()
    examens_a_valider = ExamenLaboratoire.objects.filter(
        statut='Saisie résultats'
    ).count()
    
    # Pharmacie
    ordonnances_en_cours = 0
    alertes_stock = LotMedicament.objects.filter(
        quantite__lte=models.F('medicament__seuil_alerte')
    ).count()
    
    # Facturation
    today = timezone.now().date()
    chiffre_jour = Facture.objects.filter(
        date_emission=today,
        statut='Payée'
    ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    mois_start = timezone.now().replace(day=1).date()
    chiffre_mois = Facture.objects.filter(
        date_emission__gte=mois_start,
        statut='Payée'
    ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    result = DashboardSummary(
        patients_totaux=patients_totaux,
        patients_hospitalises=patients_hospitalises,
        hospitalisations_actives=hospitalisations_actives,
        taux_occupation=round(taux_occupation, 2),
        examens_en_attente=examens_en_attente,
        examens_a_valider=examens_a_valider,
        ordonnances_en_cours=ordonnances_en_cours,
        alertes_stock=alertes_stock,
        chiffre_affaires_jour=chiffre_jour,
        chiffre_affaires_mois=chiffre_mois,
    )
    
    cache.set(cache_key, result, timeout=300)  # Cache 5 minutes
    return result


@router.get('/kpi/patients')
def kpi_patients(request, days: int = 30):
    """KPIs patients sur les derniers jours."""
    date_start = timezone.now() - timedelta(days=days)
    
    nouveaux_patients = Patient.objects.filter(
        created_at__gte=date_start
    ).count()
    
    consultations_total = 0  # À implémenter
    
    return {
        'period_days': days,
        'nouveaux_patients': nouveaux_patients,
        'consultations': consultations_total,
    }


@router.get('/kpi/hospitalisations')
def kpi_hospitalisations(request, days: int = 30):
    """KPIs hospitalisations."""
    date_start = timezone.now() - timedelta(days=days)
    
    admissions = Hospitalisation.objects.filter(
        date_entree__gte=date_start
    ).count()
    
    sorties = Hospitalisation.objects.filter(
        date_sortie_reelle__gte=date_start,
        date_sortie_reelle__isnull=False
    ).count()
    
    sejour_moyen = Hospitalisation.objects.filter(
        statut='Sorti',
        date_entree__gte=date_start
    ).annotate(
        duree=models.F('date_sortie_reelle') - models.F('date_entree')
    ).aggregate(Avg('duree'))['duree__avg'] or 0
    
    return {
        'admissions': admissions,
        'sorties': sorties,
        'sejour_moyen_jours': round(sejour_moyen, 1),
        'actives': Hospitalisation.objects.filter(statut='Actif').count(),
    }


@router.get('/kpi/laboratoire')
def kpi_laboratoire(request, days: int = 7):
    """KPIs laboratoire."""
    from django.utils import timezone
    from datetime import timedelta
    
    date_start = timezone.now() - timedelta(days=days)
    
    examens_total = ExamenLaboratoire.objects.filter(
        date_prescription__gte=date_start
    ).count()
    
    valides = ExamenLaboratoire.objects.filter(
        statut='Validé',
        date_prescription__gte=date_start
    ).count()
    
    temps_moyen_validation = ExamenLaboratoire.objects.filter(
        statut='Validé',
        date_prescription__gte=date_start,
        date_validation__isnull=False
    ).annotate(
        duree=models.F('date_validation') - models.F('date_prescription')
    ).aggregate(Avg('duree'))['duree__avg'] or 0
    
    return {
        'examens_total': examens_total,
        'valides': valides,
        'en_cours': examens_total - valides,
        'temps_moyen_heures': round(temps_moyen_validation.total_seconds() / 3600, 1) if hasattr(temps_moyen_validation, 'total_seconds') else 0,
    }


@router.get('/kpi/finances')
def kpi_finances(request, days: int = 30):
    """KPIs financiers."""
    date_start = timezone.now() - timedelta(days=days)
    
    factures_total = Facture.objects.filter(
        date_emission__gte=date_start
    ).count()
    
    recu = Facture.objects.filter(
        date_emission__gte=date_start,
        statut='Payée'
    ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    en_attente = Facture.objects.filter(
        date_emission__gte=date_start,
        statut__in=['En attente', 'Partielle']
    ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    return {
        'factures_total': factures_total,
        'recette_totale': recu,
        'en_attente_paiement': en_attente,
        'taux_recouvrement': round((recu / (recu + en_attente) * 100), 2) if (recu + en_attente) > 0 else 0,
    }


@router.get('/charts/occupation')
def chart_occupation(request, days: int = 7):
    """Courbe d'occupation des lits sur les derniers jours."""
    labels = []
    values = []
    
    for i in range(days - 1, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        labels.append(date.strftime('%Y-%m-%d'))
        
        # Nombre de lits occupés à cette date
        occupe = Lit.objects.filter(
            statut='Occupe',
            hospitalisations__date_entree__lte=date,
            hospitalisations__date_sortie_reelle__gte=date
        ).count()
        
        total = Lit.objects.filter(actif=True).count()
        taux = (occupe / total * 100) if total > 0 else 0
        values.append(round(taux, 2))
    
    return {'labels': labels, 'values': values}


@router.get('/health')
def health_check(request):
    """Health check endpoint pour monitoring."""
    from django.db import connection
    
    checks = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'checks': {},
    }
    
    # Database check
    try:
        connection.ensure_connection()
        checks['checks']['database'] = {'status': 'ok'}
    except Exception as e:
        checks['checks']['database'] = {'status': 'error', 'message': str(e)}
        checks['status'] = 'unhealthy'
    
    # Cache check (if Redis configured)
    try:
        cache.set('health_check', 'ok', timeout=10)
        if cache.get('health_check') == 'ok':
            checks['checks']['cache'] = {'status': 'ok'}
        else:
            checks['checks']['cache'] = {'status': 'warning', 'message': 'Cache latency'}
    except Exception as e:
        checks['checks']['cache'] = {'status': 'warning', 'message': str(e)}
    
    return checks
