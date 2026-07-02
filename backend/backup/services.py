"""
Services de backup et restauration
"""
import subprocess
import os
import hashlib
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import tempfile

logger = logging.getLogger(__name__)


class BackupService:
    """Service pour gérer les backups"""
    
    @staticmethod
    def backup_database(execution_id: int) -> str:
        """
        Créer un backup de la base de données PostgreSQL
        
        Returns:
            Chemin du fichier de backup
        """
        from backup.models import BackupExecution
        
        execution = BackupExecution.objects.get(id=execution_id)
        execution.status = 'running'
        execution.start_time = timezone.now()
        execution.save()
        
        try:
            # Configuration DB
            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default'].get('USER', '')
            db_host = settings.DATABASES['default'].get('HOST', '')
            db_port = settings.DATABASES['default'].get('PORT', '')
            
            # Créer fichier temporaire
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"/tmp/backup_{db_name}_{timestamp}.sql"
            
            # Construire commande pg_dump
            cmd = ['pg_dump']
            if db_user:
                cmd.extend(['-U', db_user])
            if db_host:
                cmd.extend(['-h', db_host])
            if db_port:
                cmd.extend(['-p', db_port])
            cmd.extend(['--format=plain', '--encoding=UTF-8'])
            cmd.append(db_name)
            
            # Exécuter backup
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env={**os.environ, 'PGPASSWORD': settings.DATABASES['default'].get('PASSWORD', '')}
                )
            
            if result.returncode != 0:
                raise Exception(f"pg_dump échoué: {result.stderr.decode()}")
            
            # Calculer checksum
            checksum = BackupService._calculate_checksum(backup_file)
            
            # Mettre à jour execution
            execution.file_path = backup_file
            execution.checksum = checksum
            execution.file_size = os.path.getsize(backup_file)
            execution.status = 'success'
            execution.end_time = timezone.now()
            execution.duration_seconds = (execution.end_time - execution.start_time).seconds
            execution.save()
            
            logger.info(f"Backup réussi: {backup_file} ({checksum})")
            
            return backup_file
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.end_time = timezone.now()
            execution.save()
            logger.error(f"Backup échoué: {e}")
            raise
    
    @staticmethod
    def backup_media(execution_id: int) -> str:
        """
        Créer un backup des fichiers médias
        
        Returns:
            Chemin de l'archive
        """
        from backup.models import BackupExecution
        
        execution = BackupExecution.objects.get(id=execution_id)
        execution.status = 'running'
        execution.start_time = timezone.now()
        execution.save()
        
        try:
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"/tmp/backup_media_{timestamp}.tar.gz"
            
            # Créer archive
            subprocess.run(
                ['tar', '-czf', backup_file, '-C', os.path.dirname(media_root), os.path.basename(media_root)],
                check=True
            )
            
            # Calculer checksum
            checksum = BackupService._calculate_checksum(backup_file)
            
            # Mettre à jour execution
            execution.file_path = backup_file
            execution.checksum = checksum
            execution.file_size = os.path.getsize(backup_file)
            execution.status = 'success'
            execution.end_time = timezone.now()
            execution.duration_seconds = (execution.end_time - execution.start_time).seconds
            execution.save()
            
            logger.info(f"Backup médias réussi: {backup_file}")
            
            return backup_file
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.end_time = timezone.now()
            execution.save()
            logger.error(f"Backup médias échoué: {e}")
            raise
    
    @staticmethod
    def _calculate_checksum(file_path: str) -> str:
        """Calculer le checksum SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def upload_to_s3(file_path: str, bucket: str, destination_key: str):
        """
        Uploader un fichier vers S3
        
        Args:
            file_path: Chemin local du fichier
            bucket: Nom du bucket S3
            destination_key: Clé de destination dans S3
        """
        try:
            import boto3
            
            s3 = boto3.client('s3')
            s3.upload_file(file_path, bucket, destination_key)
            
            logger.info(f"Fichier uploadé vers S3: s3://{bucket}/{destination_key}")
            
        except ImportError:
            logger.warning("boto3 non installé, upload S3 skipped")
        except Exception as e:
            logger.error(f"Upload S3 échoué: {e}")
            raise
    
    @staticmethod
    def encrypt_file(file_path: str, passphrase: str) -> str:
        """
        Chiffrer un fichier avec GPG
        
        Returns:
            Chemin du fichier chiffré
        """
        encrypted_file = f"{file_path}.gpg"
        
        try:
            subprocess.run(
                ['gpg', '--symmetric', '--cipher-algo', 'AES256', 
                 '--passphrase', passphrase, '--batch', '--yes',
                 '-o', encrypted_file, file_path],
                check=True
            )
            
            logger.info(f"Fichier chiffré: {encrypted_file}")
            return encrypted_file
            
        except Exception as e:
            logger.error(f"Chiffrement échoué: {e}")
            raise
    
    @staticmethod
    def cleanup_old_backups(destination: str, retention_days: int):
        """
        Supprimer les backups plus vieux que retention_days
        
        Args:
            destination: Chemin local ou S3 bucket
            retention_days: Nombre de jours de rétention
        """
        threshold = timezone.now() - timedelta(days=retention_days)
        
        # Supprimer fichiers locaux
        if destination.startswith('/'):
            for file in os.listdir(destination):
                file_path = os.path.join(destination, file)
                if os.path.getmtime(file_path) < threshold.timestamp():
                    os.remove(file_path)
                    logger.info(f"Backup supprimé: {file_path}")
        
        # Supprimer S3
        elif destination.startswith('s3://'):
            try:
                import boto3
                bucket_name = destination.replace('s3://', '').split('/')[0]
                prefix = '/'.join(destination.replace('s3://', '').split('/')[1:])
                
                s3 = boto3.client('s3')
                
                paginator = s3.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        if obj['LastModified'].replace(tzinfo=None) < threshold:
                            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                            logger.info(f"S3 objet supprimé: {obj['Key']}")
                            
            except ImportError:
                logger.warning("boto3 non installé, cleanup S3 skipped")
            except Exception as e:
                logger.error(f"Cleanup S3 échoué: {e}")


class RestoreService:
    """Service pour restaurer des backups"""
    
    @staticmethod
    def restore_database(backup_file: str, target_db: str) -> bool:
        """
        Restaurer une base de données depuis un backup
        
        Args:
            backup_file: Chemin du fichier de backup
            target_db: Nom de la base cible
        
        Returns:
            True si succès
        """
        try:
            # Configuration DB
            db_user = settings.DATABASES['default'].get('USER', '')
            db_host = settings.DATABASES['default'].get('HOST', '')
            db_port = settings.DATABASES['default'].get('PORT', '')
            
            # Construire commande psql
            cmd = ['psql']
            if db_user:
                cmd.extend(['-U', db_user])
            if db_host:
                cmd.extend(['-h', db_host])
            if db_port:
                cmd.extend(['-p', db_port])
            cmd.extend(['-d', target_db, '-f', backup_file])
            
            # Exécuter restauration
            result = subprocess.run(
                cmd,
                env={**os.environ, 'PGPASSWORD': settings.DATABASES['default'].get('PASSWORD', '')},
                capture_output=True
            )
            
            if result.returncode != 0:
                raise Exception(f"psql échoué: {result.stderr.decode()}")
            
            logger.info(f"Restauration réussie: {backup_file} -> {target_db}")
            return True
            
        except Exception as e:
            logger.error(f"Restauration échouée: {e}")
            raise
    
    @staticmethod
    def verify_integrity(backup_file: str, expected_checksum: str) -> bool:
        """
        Vérifier l'intégrité d'un backup
        
        Args:
            backup_file: Chemin du fichier
            expected_checksum: Checksum attendu
        
        Returns:
            True si checksum valide
        """
        actual_checksum = BackupService._calculate_checksum(backup_file)
        
        if actual_checksum != expected_checksum:
            logger.error(f"Checksum mismatch: {actual_checksum} != {expected_checksum}")
            return False
        
        logger.info(f"Intégrité vérifiée: {backup_file}")
        return True
