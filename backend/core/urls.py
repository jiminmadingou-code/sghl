from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth.models import User
            # Décoder le jeton
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            # Récupérer l'utilisateur
            user = User.objects.get(id=user_id)
            # Injecter dans request
            request.user = user
            request.user_id = user.id
            request.user_email = user.email
            return token
        except Exception:
            return None

api = NinjaAPI(version='1.0', title='SGHL API', auth=JWTAuth())

from patients.api import router as patients_router
from hospitalisations.api import router as hospit_router
from laboratoire.api import router as labo_router
from pharmacie.api import router as pharma_router
from facturation.api import router as factu_router
from personnel.api import router as personnel_router
from audit.api import router as audit_router
from dashboard.api import router as dashboard_router
from soins.api import router as soins_router
from chat.api import router as chat_router
from gardes.api import router as gardes_router
from rendez_vous.api import router as rdv_router
from prescriptions.api import router as prescriptions_router
from consentement.api import router as consentement_router
from urgences.api import router as urgences_router
from imagerie.api import router as imagerie_router
from bloc_operatoire.api import router as bloc_router
from maternite.api import router as maternite_router
from teleconsultation.api import router as teleconsult_router
from archivage.api import router as archivage_router
from interoperabilite.api import router as fhir_router

api.add_router('/patients/', patients_router)
api.add_router('/hospitalisations/', hospit_router)
api.add_router('/laboratoire/', labo_router)
api.add_router('/pharmacie/', pharma_router)
api.add_router('/facturation/', factu_router)
api.add_router('/personnel/', personnel_router)
api.add_router('/audit/', audit_router)
api.add_router('/dashboard/', dashboard_router)
api.add_router('/soins/', soins_router)
api.add_router('/chat/', chat_router)
api.add_router('/gardes/', gardes_router)
api.add_router('/rendez-vous/', rdv_router)
api.add_router('/prescriptions/', prescriptions_router)
api.add_router('/consentement/', consentement_router)
api.add_router('/urgences/', urgences_router)
api.add_router('/imagerie/', imagerie_router)
api.add_router('/bloc-operatoire/', bloc_router)
api.add_router('/maternite/', maternite_router)
api.add_router('/teleconsultation/', teleconsult_router)
api.add_router('/archivage/', archivage_router)
api.add_router('/interop/', fhir_router)

import json, random, string
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Stockage temporaire des codes en mémoire (TTL 15 min)
_confirm_codes = {}

@csrf_exempt
@require_http_methods(['POST'])
def patient_register_view(request):
    """Inscription d'un nouveau patient avec création du compte Django + dossier patient."""
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        email = data.get('email', '').strip().lower()
        prenom = data.get('prenom', '').strip()
        nom = data.get('nom', '').strip()
        date_naissance = data.get('date_naissance', '')
        sexe = data.get('sexe', 'M')
        telephone = data.get('telephone', '').strip()

        # Générer username unique depuis email
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        # Validation
        if not password or not email or not prenom or not nom:
            return JsonResponse({'error': 'Tous les champs obligatoires doivent être remplis.'}, status=400)
        if password != confirm_password:
            return JsonResponse({'error': 'Les mots de passe ne correspondent pas.'}, status=400)
        if len(password) < 6:
            return JsonResponse({'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Cet email est déjà utilisé.'}, status=409)

        # Créer le compte Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom,
        )

        # Créer le dossier Patient associé
        from patients.models import Patient
        Patient.objects.create(
            prenom=prenom,
            nom=nom,
            date_naissance=date_naissance,
            sexe=sexe,
            telephone=telephone,
            email=email,
            user=user,
        )

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'status': 'ok',
            'message': 'Compte créé avec succès. Vous pouvez vous connecter.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': 'Patient',
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def send_confirm_code_view(request):
    """Génère un code à 6 chiffres et l'envoie par email."""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        nom   = data.get('nom', 'Administrateur')
        if not email:
            return JsonResponse({'error': 'Email requis'}, status=400)

        code = ''.join(random.choices(string.digits, k=6))
        import time
        _confirm_codes[email] = {'code': code, 'expires': time.time() + 900}

        subject = 'DIGNE HOSPITAL — Code de confirmation administrateur'
        body = (
            f'Bonjour {nom},\n\n'
            f'Votre code de confirmation est :\n\n'
            f'  ► {code} ◄\n\n'
            f'Ce code expire dans 15 minutes.\n'
            f'Ne le partagez avec personne.\n\n'
            f'— L\'équipe DIGNE HOSPITAL'
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        print(f'📧 Code {code} envoyé à {email}')
        return JsonResponse({'status': 'sent', 'email': email})
    except Exception as e:
        # Fallback console si SMTP non configuré
        print(f'📧 [FALLBACK] Code pour {email}: {code if "code" in dir() else "ERR"} — Erreur SMTP: {e}')
        return JsonResponse({'status': 'fallback', 'message': str(e)}, status=200)

@csrf_exempt
@require_http_methods(['POST'])
def verify_confirm_code_view(request):
    """Vérifie le code et crée le compte admin Django."""
    try:
        import time
        data  = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        code  = data.get('code', '').strip()
        entry = _confirm_codes.get(email)

        if not entry:
            return JsonResponse({'error': 'Aucun code pour cet email.'}, status=400)
        if time.time() > entry['expires']:
            del _confirm_codes[email]
            return JsonResponse({'error': 'Code expiré. Demandez un nouveau code.'}, status=400)
        if entry['code'] != code:
            return JsonResponse({'error': 'Code incorrect.'}, status=400)

        del _confirm_codes[email]

        # Créer le compte Django User si inexistant
        from django.contrib.auth.models import User
        username = data.get('username', email.split('@')[0])
        password = data.get('password', '')
        if not User.objects.filter(username=username).exists():
            u = User.objects.create_user(
                username=username, email=email,
                password=password,
                first_name=data.get('prenom', ''),
                last_name=data.get('nom', ''),
                is_staff=True,
            )
        return JsonResponse({'status': 'confirmed', 'username': username})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def sante_view(request):
    """Endpoint de health check enrichi."""
    from django.utils import timezone
    checks = {'status': 'ok', 'timestamp': timezone.now().isoformat(), 'version': '1.0'}
    # DB
    try:
        from django.db import connection
        connection.ensure_connection()
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {e}'
        checks['status'] = 'degraded'
    # Cache/Redis
    try:
        from django.core.cache import cache
        cache.set('_health', '1', 5)
        checks['cache'] = 'ok' if cache.get('_health') else 'miss'
    except Exception as e:
        checks['cache'] = f'error: {e}'
        checks['status'] = 'degraded'
    # Counts
    try:
        from patients.models import Patient
        from hospitalisations.models import Hospitalisation
        checks['patients_total'] = Patient.objects.count()
        checks['hospitalisations_actives'] = Hospitalisation.objects.filter(statut='Actif').count()
    except Exception:
        pass
    status_code = 200 if checks['status'] == 'ok' else 503
    return JsonResponse(checks, status=status_code)

def accueil_view(request):
    return JsonResponse({
        'application': 'SGHL — Système de Gestion Hospitalière et de Laboratoire',
        'version': '1.0',
        'status': 'running',
        'api': '/api/v1/',
        'docs': '/api/v1/docs',
        'admin': '/admin/',
        'sante': '/api/v1/sante/',
    })

urlpatterns = [
    path('', accueil_view, name='accueil'),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('api/v1/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/register/', patient_register_view, name='patient_register'),
    path('api/v1/auth/send-confirm-code/', send_confirm_code_view, name='send_confirm_code'),
    path('api/v1/auth/verify-confirm-code/', verify_confirm_code_view, name='verify_confirm_code'),
    path('api/v1/sante/', sante_view, name='sante'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
