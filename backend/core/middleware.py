"""
Middlewares de sécurité SGHL :
- Anti-XSS headers
- Rate limiting HTTP
- Logging des requêtes suspectes
"""
import re
import logging
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Patterns d'injection SQL et XSS basiques
SUSPICIOUS_PATTERNS = [
    re.compile(r'<script[^>]*>', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r"(union|select|insert|update|delete|drop|truncate)\s+", re.IGNORECASE),
    re.compile(r"(--|;|'|\"|`)\s*(or|and)\s+", re.IGNORECASE),
]

RATE_LIMIT_PATHS = {
    '/api/v1/auth/login/': (5, 300),    # 5 tentatives / 5 min
    '/api/v1/auth/refresh/': (20, 60),  # 20 / min
}


class SecurityHeadersMiddleware:
    """Ajouter les headers de sécurité à chaque réponse."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        if not response.get('Cache-Control'):
            response['Cache-Control'] = 'no-store'
        return response


class RateLimitMiddleware:
    """Rate limiting par IP sur les endpoints sensibles."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path in RATE_LIMIT_PATHS and request.method == 'POST':
            max_attempts, window = RATE_LIMIT_PATHS[path]
            ip = self._get_ip(request)
            key = f'rl:{path}:{ip}'
            count = cache.get(key, 0)
            if count >= max_attempts:
                logger.warning(f"Rate limit dépassé: {ip} sur {path}")
                return JsonResponse(
                    {'detail': 'Trop de tentatives. Réessayez plus tard.'},
                    status=429
                )
            cache.set(key, count + 1, timeout=window)
        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


class RBACMiddleware:
    """
    Middleware de contrôle d'accès basé sur les rôles (RBAC).
    Empêche les utilisateurs d'accéder à des ressources ou actions 
    non autorisées selon leur rôle.
    """
    ROLE_PERMISSIONS = {
        'Patient': ['patients:read', 'rdv:read', 'rdv:create', 'facturation:read', 'resultats:read', 'chat:read', 'chat:create'],
        'Médecin': ['patients:read', 'patients:write', 'rdv:read', 'rdv:write', 'prescriptions:write', 'hospitalisations:write', 'soins:read', 'laboratoire:write', 'chat:read', 'chat:create'],
        'Infirmier': ['patients:read', 'soins:write', 'constantes:write', 'hospitalisations:read', 'chat:read'],
        'Biologiste': ['laboratoire:read', 'laboratoire:write', 'laboratoire:validate', 'patients:read', 'chat:read'],
        'Pharmacien': ['pharmacie:read', 'pharmacie:write', 'prescriptions:read', 'chat:read'],
        'Caissier': ['facturation:read', 'facturation:write', 'patients:read'],
        'Réceptionniste': ['rdv:read', 'rdv:write', 'patients:write', 'hospitalisations:write'],
        'Admin': ['*'],  # Accès total
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorer le middleware pour les utilisateurs non authentifiés
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)
        
        # Ignorer pour les superutilisateurs
        if request.user.is_superuser:
            return self.get_response(request)
        
        user_role = getattr(request.user, 'role', 'Patient')
        allowed_permissions = self.ROLE_PERMISSIONS.get(user_role, [])
        
        # Vérifier si l'utilisateur a la permission nécessaire
        # On extrait la permission demandée du chemin ou des args
        permission_required = self._extract_permission(request)
        
        if permission_required and '*' not in allowed_permissions:
            if permission_required not in allowed_permissions:
                logger.warning(f"Accès refusé RBAC: {request.user.username} ({user_role}) tente d'accéder à {permission_required}")
                from django.http import JsonResponse
                return JsonResponse({'detail': 'Accès refusé: permission insuffisante.'}, status=403)
        
        return self.get_response(request)

    def _extract_permission(self, request):
        """
        Extraire la permission requise depuis la requête.
        Cette logique peut être affinée selon la structure des URLs.
        """
        # Exemple: /api/v1/laboratoire/ -> laboratoire:read
        path = request.path
        method = request.method
        
        # Mappage basique méthode -> action
        action_map = {
            'GET': 'read',
            'POST': 'write',
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'delete',
        }
        action = action_map.get(method, 'read')
        
        # Extraire le module du chemin
        parts = path.strip('/').split('/')
        if len(parts) >= 3:  # /api/v1/module/...
            module = parts[2]
            return f"{module}:{action}"
        
        return None


class InputSanitizationMiddleware:
    """Détecter et bloquer les tentatives d'injection XSS/SQL dans les paramètres GET."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            for value in request.GET.values():
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern.search(value):
                        ip = request.META.get('REMOTE_ADDR', '')
                        logger.warning(f"Tentative d'injection détectée depuis {ip}: {value[:100]}")
                        return JsonResponse({'detail': 'Requête invalide.'}, status=400)
        return self.get_response(request)
