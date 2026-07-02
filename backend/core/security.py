"""
Module de sécurité avancé pour le SGHL
- Chiffrement AES-256
- Rate Limiting
- Validation des entrées
"""
import hashlib
import hmac
import secrets
import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
import re


class AESCipher:
    """Chiffrement AES-256 pour données sensibles."""
    
    def __init__(self, key=None):
        """
        Initialiser le chiffre avec une clé.
        Si aucune clé n'est fournie, utilise SECRET_KEY.
        """
        from django.conf import settings
        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            # Dérivation de clé depuis SECRET_KEY
            self.key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    
    def encrypt(self, plaintext):
        """Chiffrer une chaîne de caractères."""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        # Initialisation vector aléatoire
        iv = secrets.token_bytes(16)
        
        # Padding PKCS7
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Chiffrement AES-CBC
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Retourner IV + ciphertext
        return iv + ciphertext
    
    def decrypt(self, ciphertext):
        """Déchiffrer une chaîne de caractères."""
        if isinstance(ciphertext, str):
            ciphertext = bytes.fromhex(ciphertext)
        
        # Extraire IV et ciphertext
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        
        # Déchiffrement
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        # Unpadding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode()


class RateLimiter:
    """Système de rate limiting pour protection contre brute-force."""
    
    def __init__(self, max_attempts=5, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.prefix = 'rate_limit_'
    
    def _get_key(self, identifier, action):
        return f"{self.prefix}{action}_{identifier}"
    
    def check(self, identifier, action):
        """
        Vérifier si l'action est autorisée pour l'identifiant.
        Retourne (allowed, remaining_attempts)
        """
        key = self._get_key(identifier, action)
        attempts = cache.get(key, 0)
        
        if attempts >= self.max_attempts:
            return False, 0
        
        return True, self.max_attempts - attempts
    
    def increment(self, identifier, action):
        """Incrémenter le compteur d'tentatives."""
        key = self._get_key(identifier, action)
        attempts = cache.get(key, 0)
        
        if attempts == 0:
            # Premier essai - définir l'expiration
            cache.set(key, 1, timeout=self.window_seconds)
        else:
            cache.set(key, attempts + 1, timeout=self.window_seconds)
    
    def reset(self, identifier, action):
        """Réinitialiser le compteur."""
        key = self._get_key(identifier, action)
        cache.delete(key)


class SecurityValidator:
    """Validateurs de sécurité pour les entrées utilisateur."""
    
    # Expressions régulières pour validation
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$',
        'cip10': r'^[A-Z]{3}-[0-9]{4}$',  # Code CIM-10 format
        'password_strong': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    }
    
    @staticmethod
    def validate_email(email):
        if not re.match(SecurityValidator.PATTERNS['email'], email):
            raise ValidationError("Format d'email invalide")
        return email
    
    @staticmethod
    def validate_phone(phone):
        if phone and not re.match(SecurityValidator.PATTERNS['phone'], phone):
            raise ValidationError("Format de téléphone invalide")
        return phone
    
    @staticmethod
    def validate_password_strength(password):
        """Valider la force du mot de passe."""
        if not re.match(SecurityValidator.PATTERNS['password_strong'], password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une majuscule, une minuscule, "
                "un chiffre et un caractère spécial (@$!%*?&)"
            )
        return password
    
    @staticmethod
    def sanitize_html(text):
        """Nettoyer le texte des balises HTML potentiellement dangereuses."""
        if not text:
            return text
        # Supprimer les balises script et autres éléments dangereux
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', cleaned, flags=re.IGNORECASE)
        return cleaned
    
    @staticmethod
    def validate_cim10_code(code):
        """Valider un code CIM-10."""
        if not re.match(SecurityValidator.PATTERNS['cip10'], code.upper()):
            raise ValidationError("Format de code CIM-10 invalide (ex: A00-1234)")
        return code.upper()


class MFAHandler:
    """Gestion de l'authentification à deux facteurs (MFA)."""
    
    def __init__(self):
        self.prefix = 'mfa_'
        self.code_expiry = 300  # 5 minutes
    
    def generate_code(self, user_id):
        """Générer un code MFA à 6 chiffres."""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        key = f"{self.prefix}{user_id}"
        cache.set(key, code, timeout=self.code_expiry)
        return code
    
    def verify_code(self, user_id, code):
        """Vérifier le code MFA."""
        key = f"{self.prefix}{user_id}"
        expected_code = cache.get(key)
        
        if not expected_code:
            return False
        
        if hmac.compare_digest(expected_code, code):
            cache.delete(key)
            return True
        return False
    
    def invalidate_code(self, user_id):
        """Invalider le code MFA actuel."""
        key = f"{self.prefix}{user_id}"
        cache.delete(key)


class TokenManager:
    """Gestion sécurisée des tokens JWT avec rotation."""
    
    @staticmethod
    def rotate_refresh_token(refresh_token):
        """
        Valider et faire tourner le refresh token.
        Retourne (new_access, new_refresh) ou None si invalide.
        """
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            token = RefreshToken(refresh_token)
            # Valider le token
            token.verify()
            
            # Créer une nouvelle paire de tokens
            new_refresh = RefreshToken()
            new_access = new_refresh.access_token
            
            # Blacklist l'ancien refresh token
            token.blacklist()
            
            return str(new_access), str(new_refresh)
        except Exception:
            return None
    
    @staticmethod
    def generate_api_key():
        """Générer une clé API sécurisée."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key):
        """Hasher une clé API pour stockage sécurisé."""
        return hashlib.sha256(api_key.encode()).hexdigest()


# Instanciation globale
aes_cipher = AESCipher()
rate_limiter = RateLimiter()
mfa_handler = MFAHandler()
security_validator = SecurityValidator()
