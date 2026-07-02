"""
SGHL — Moteur Antivirus / Scanner de fichiers
==============================================
Analyse les fichiers uploadés avant stockage :
  1. Contrôle MIME type strict
  2. Vérification taille maximale
  3. Signatures de malwares (magic bytes)
  4. Détection heuristique (scripts dans PDF/images)
  5. Calcul d'entropie (détection fichiers chiffrés/compressés suspects)
  6. Quarantaine automatique des fichiers suspects
  7. Audit trail de chaque scan
"""
import hashlib
import math
import os
import re
import struct
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional

logger = logging.getLogger('sghl.antivirus')

# ── Types MIME autorisés par contexte ────────────────────────────────────────
ALLOWED_MIME = {
    'documents': {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    },
    'images': {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
    },
    'all': {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    },
}

# Taille maximale par type (en octets)
MAX_FILE_SIZES = {
    'image/jpeg':       10 * 1024 * 1024,   # 10 MB
    'image/png':        10 * 1024 * 1024,
    'image/gif':         5 * 1024 * 1024,
    'application/pdf':  50 * 1024 * 1024,   # 50 MB
    'default':          20 * 1024 * 1024,   # 20 MB
}

# ── Signatures de malwares (magic bytes) ─────────────────────────────────────
# Format : (nom, offset, pattern_bytes)
MALWARE_SIGNATURES = [
    # Exécutables Windows/Linux
    ('EXE_DOS',    0, b'MZ'),
    ('ELF_LINUX',  0, b'\x7fELF'),
    ('COM_FILE',   0, b'\xe9'),

    # Archives chiffrées suspects
    ('RAR_SFX',    0, b'Rar!\x1a\x07'),

    # Macros Office malveillantes (OLE2)
    ('OLE2_MACRO', 0, b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'),

    # Scripts dans fichiers
    ('POWERSHELL', 0, b'\xff\xfe'),           # PowerShell UTF-16
    ('JAVA_CLASS', 0, b'\xca\xfe\xba\xbe'),  # Java .class

    # Patterns heuristiques dans contenu
    ('JS_EVAL',        None, b'eval(unescape('),
    ('JS_DOCUMENT',    None, b'document.write(unescape('),
    ('PHP_EXEC',       None, b'<?php'),
    ('SHELL_WGET',     None, b'wget http'),
    ('SHELL_CURL',     None, b'curl http'),
    ('PYTHON_EXEC',    None, b'__import__('),
    ('BASE64_EXEC',    None, b'base64_decode(exec('),
    ('IFRAME_INJECT',  None, b'<iframe src='),
    ('VBSCRIPT',       None, b'<script language="vbscript"'),
    ('MSHTA',          None, b'mshta.exe'),
    ('REGSVR32',       None, b'regsvr32 /s /n'),
    ('CERTUTIL',       None, b'certutil -decode'),
]

# ── Magic bytes pour vérification MIME réelle ────────────────────────────────
MAGIC_BYTES = {
    b'\xff\xd8\xff':          'image/jpeg',
    b'\x89PNG\r\n\x1a\n':    'image/png',
    b'GIF87a':                'image/gif',
    b'GIF89a':                'image/gif',
    b'%PDF':                  'application/pdf',
    b'PK\x03\x04':            'application/zip',
    b'\xd0\xcf\x11\xe0':      'application/msword',
    b'BM':                    'image/bmp',
    b'RIFF':                  'image/webp',
}


@dataclass
class ScanResult:
    is_clean:       bool = True
    threats:        list = field(default_factory=list)
    warnings:       list = field(default_factory=list)
    file_hash:      str  = ''
    mime_detected:  str  = ''
    file_size:      int  = 0
    entropy:        float = 0.0
    scan_duration_ms: int = 0
    quarantined:    bool = False
    timestamp:      str  = ''

    def to_dict(self):
        return {
            'is_clean':         self.is_clean,
            'threats':          self.threats,
            'warnings':         self.warnings,
            'file_hash':        self.file_hash,
            'mime_detected':    self.mime_detected,
            'file_size':        self.file_size,
            'entropy':          round(self.entropy, 4),
            'scan_duration_ms': self.scan_duration_ms,
            'quarantined':      self.quarantined,
            'timestamp':        self.timestamp,
        }


class AntivirusEngine:
    """Moteur de scan antivirus pour fichiers médicaux uploadés."""

    QUARANTINE_DIR = Path('/tmp/sghl_quarantine')

    def __init__(self):
        self.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Point d'entrée principal ─────────────────────────────────────────────
    def scan(self, file_obj: BinaryIO, filename: str,
             declared_mime: str = '', context: str = 'all') -> ScanResult:
        """
        Scanne un fichier uploadé.
        Returns ScanResult avec is_clean=False si menace détectée.
        """
        start = datetime.now()
        result = ScanResult(timestamp=start.isoformat())

        try:
            content = file_obj.read()
            file_obj.seek(0)
        except Exception as e:
            result.is_clean = False
            result.threats.append(f'LECTURE_IMPOSSIBLE: {e}')
            return result

        result.file_size  = len(content)
        result.file_hash  = hashlib.sha256(content).hexdigest()
        result.entropy    = self._calc_entropy(content)

        # 1. Taille maximale
        self._check_size(content, declared_mime, result)

        # 2. MIME réel vs déclaré
        self._check_mime(content, filename, declared_mime, context, result)

        # 3. Signatures malwares
        self._check_signatures(content, result)

        # 4. Heuristiques (scripts cachés)
        self._check_heuristics(content, filename, result)

        # 5. Entropie suspecte (fichiers chiffrés/obfusqués)
        self._check_entropy(result)

        # 6. Quarantaine si infecté
        if not result.is_clean:
            self._quarantine(content, result.file_hash, filename)
            result.quarantined = True

        result.scan_duration_ms = int((datetime.now() - start).total_seconds() * 1000)

        # Log systématique
        log_level = logging.WARNING if not result.is_clean else logging.INFO
        logger.log(log_level,
            f"[ANTIVIRUS] {'INFECTÉ' if not result.is_clean else 'CLEAN'} | "
            f"file={filename} | hash={result.file_hash[:16]}... | "
            f"size={result.file_size}B | entropy={result.entropy:.2f} | "
            f"threats={result.threats} | {result.scan_duration_ms}ms"
        )

        return result

    # ── Contrôle taille ──────────────────────────────────────────────────────
    def _check_size(self, content: bytes, mime: str, result: ScanResult):
        max_size = MAX_FILE_SIZES.get(mime, MAX_FILE_SIZES['default'])
        if len(content) > max_size:
            result.is_clean = False
            result.threats.append(
                f'TAILLE_EXCESSIVE: {len(content)} octets > max {max_size} octets'
            )
        elif len(content) == 0:
            result.is_clean = False
            result.threats.append('FICHIER_VIDE')

    # ── Contrôle MIME ────────────────────────────────────────────────────────
    def _check_mime(self, content: bytes, filename: str,
                    declared_mime: str, context: str, result: ScanResult):
        # Détecter le vrai MIME depuis les magic bytes
        detected = 'application/octet-stream'
        for magic, mime in MAGIC_BYTES.items():
            if content[:len(magic)] == magic:
                detected = mime
                break
        result.mime_detected = detected

        allowed = ALLOWED_MIME.get(context, ALLOWED_MIME['all'])

        # Extension suspecte
        ext = Path(filename).suffix.lower()
        DANGEROUS_EXTENSIONS = {
            '.exe', '.bat', '.cmd', '.sh', '.ps1', '.vbs', '.js',
            '.jar', '.com', '.pif', '.scr', '.msi', '.dll', '.php',
            '.py', '.rb', '.pl', '.asp', '.aspx', '.cgi',
        }
        if ext in DANGEROUS_EXTENSIONS:
            result.is_clean = False
            result.threats.append(f'EXTENSION_DANGEREUSE: {ext}')

        # MIME non autorisé
        if detected not in allowed and detected != 'application/octet-stream':
            result.is_clean = False
            result.threats.append(f'MIME_NON_AUTORISE: {detected}')

        # Discordance MIME déclaré vs réel
        if declared_mime and detected != 'application/octet-stream':
            if declared_mime != detected:
                result.warnings.append(
                    f'MIME_DISCORDANT: déclaré={declared_mime}, détecté={detected}'
                )

    # ── Signatures malwares ──────────────────────────────────────────────────
    def _check_signatures(self, content: bytes, result: ScanResult):
        for name, offset, pattern in MALWARE_SIGNATURES:
            if offset is not None:
                # Vérification à un offset fixe
                if content[offset:offset + len(pattern)] == pattern:
                    result.is_clean = False
                    result.threats.append(f'SIGNATURE_MALWARE: {name}')
            else:
                # Recherche dans tout le contenu
                if pattern in content:
                    # Certains patterns sont des avertissements (ex: PHP peut être légitime)
                    if name in ('PHP_EXEC', 'IFRAME_INJECT', 'VBSCRIPT'):
                        result.is_clean = False
                        result.threats.append(f'CONTENU_MALVEILLANT: {name}')
                    else:
                        result.warnings.append(f'PATTERN_SUSPECT: {name}')

    # ── Heuristiques ─────────────────────────────────────────────────────────
    def _check_heuristics(self, content: bytes, filename: str, result: ScanResult):
        # Vérifier polyglot (fichier valide + payload caché)
        # Un PDF valide ne doit pas contenir de séquence EXE
        ext = Path(filename).suffix.lower()
        if ext == '.pdf' and b'MZ' in content[1024:]:
            result.is_clean = False
            result.threats.append('POLYGLOT_PDF_EXE: payload exécutable dans PDF')

        # Trop de null bytes (padded malware)
        null_ratio = content.count(b'\x00') / max(len(content), 1)
        if null_ratio > 0.5 and ext not in ('.pdf',):
            result.warnings.append(f'NULL_BYTES_EXCESSIFS: {null_ratio:.1%}')

        # Longues chaînes base64 (payload encodé)
        b64_matches = re.findall(rb'[A-Za-z0-9+/]{200,}={0,2}', content)
        if len(b64_matches) > 3:
            result.warnings.append(
                f'BASE64_CHAINES_LONGUES: {len(b64_matches)} chaînes suspectes'
            )

    # ── Entropie ─────────────────────────────────────────────────────────────
    def _check_entropy(self, result: ScanResult):
        # Entropie > 7.5 = fichier probablement chiffré ou compressé (suspect)
        if result.entropy > 7.8:
            result.warnings.append(
                f'ENTROPIE_ELEVEE: {result.entropy:.2f}/8.0 (possible obfuscation)'
            )

    # ── Calcul entropie Shannon ───────────────────────────────────────────────
    @staticmethod
    def _calc_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        length = len(data)
        entropy = 0.0
        for f in freq:
            if f > 0:
                p = f / length
                entropy -= p * math.log2(p)
        return entropy

    # ── Quarantaine ───────────────────────────────────────────────────────────
    def _quarantine(self, content: bytes, file_hash: str, original_name: str):
        """Déplace le fichier infecté en quarantaine."""
        try:
            qpath = self.QUARANTINE_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash[:8]}_{Path(original_name).name}.quarantine"
            qpath.write_bytes(content)
            logger.critical(
                f"[QUARANTAINE] Fichier infecté isolé: {qpath} | original={original_name} | hash={file_hash}"
            )
        except Exception as e:
            logger.error(f"[QUARANTAINE] Échec isolation: {e}")


# ── Singleton global ──────────────────────────────────────────────────────────
antivirus = AntivirusEngine()


# ── Décorateur / helper pour les vues Django ────────────────────────────────
def scan_uploaded_file(file_obj, filename: str, declared_mime: str = '',
                       context: str = 'all') -> ScanResult:
    """
    Fonction helper à appeler dans toute vue Django qui reçoit un fichier.

    Usage:
        result = scan_uploaded_file(request.FILES['document'], 'rapport.pdf', 'application/pdf')
        if not result.is_clean:
            raise HttpError(400, f"Fichier rejeté: {result.threats}")
    """
    return antivirus.scan(file_obj, filename, declared_mime, context)


def require_clean_file(file_obj, filename: str, declared_mime: str = '',
                       context: str = 'all'):
    """
    Lance une HttpError 400 si le fichier est infecté.
    Utiliser directement dans les endpoints Django Ninja.
    """
    from ninja.errors import HttpError
    from audit.models import AuditTrail

    result = scan_uploaded_file(file_obj, filename, declared_mime, context)

    # Enregistrer le scan dans l'audit trail
    try:
        AuditTrail.objects.create(
            action_type='VIEW',
            model_name='FileScan',
            object_id=0,
            details={
                'filename':      filename,
                'hash':          result.file_hash,
                'is_clean':      result.is_clean,
                'threats':       result.threats,
                'warnings':      result.warnings,
                'mime_detected': result.mime_detected,
                'file_size':     result.file_size,
                'entropy':       result.entropy,
                'quarantined':   result.quarantined,
            }
        )
    except Exception:
        pass

    if not result.is_clean:
        raise HttpError(
            400,
            f"Fichier rejeté par l'antivirus. Menaces détectées: {', '.join(result.threats)}"
        )

    return result
