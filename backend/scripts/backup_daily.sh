#!/bin/bash
# Script de backup quotidien pour SGHL
# À exécuter via cron: 0 2 * * * /app/scripts/backup_daily.sh

set -e

# Configuration
BACKUP_DIR="/backup"
LOG_FILE="/var/log/sghl/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
APP_NAME="sghl"

# Colors pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Début
log "=========================================="
log "Démarrage backup $APP_NAME"
log "=========================================="

# Créer répertoire backup
mkdir -p $BACKUP_DIR
mkdir -p $(dirname $LOG_FILE)

# Backup base de données
log "${YELLOW}Backup base de données...${NC}"
DB_BACKUP="${BACKUP_DIR}/db_${DATE}.sql"

if [ ! -z "$DB_HOST" ]; then
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $DB_BACKUP 2>> $LOG_FILE
else
    pg_dump -U $DB_USER -d $DB_NAME > $DB_BACKUP 2>> $LOG_FILE
fi

if [ $? -eq 0 ]; then
    log "${GREEN}✓ Backup DB réussi: $DB_BACKUP${NC}"
    
    # Calculer checksum
    CHECKSUM=$(sha256sum $DB_BACKUP | cut -d' ' -f1)
    echo $CHECKSUM > "${DB_BACKUP}.sha256"
    log "Checksum: $CHECKSUM"
    
    # Chiffrer si KEY_GPG défini
    if [ ! -z "$GPG_PASSPHRASE" ]; then
        log "${YELLOW}Chiffrement du backup...${NC}"
        gpg --symmetric --cipher-algo AES256 \
            --passphrase "$GPG_PASSPHRASE" \
            --batch --yes \
            -o "${DB_BACKUP}.gpg" $DB_BACKUP
        
        if [ $? -eq 0 ]; then
            log "${GREEN}✓ Chiffrement réussi${NC}"
            rm $DB_BACKUP  # Supprimer fichier non chiffré
        fi
    fi
else
    log "${RED}✗ Backup DB échoué${NC}"
    exit 1
fi

# Backup fichiers médias
if [ -d "$MEDIA_ROOT" ]; then
    log "${YELLOW}Backup fichiers médias...${NC}"
    MEDIA_BACKUP="${BACKUP_DIR}/media_${DATE}.tar.gz"
    
    tar -czf $MEDIA_BACKUP -C $(dirname $MEDIA_ROOT) $(basename $MEDIA_ROOT) 2>> $LOG_FILE
    
    if [ $? -eq 0 ]; then
        log "${GREEN}✓ Backup médias réussi: $MEDIA_BACKUP${NC}"
        
        # Checksum
        CHECKSUM=$(sha256sum $MEDIA_BACKUP | cut -d' ' -f1)
        echo $CHECKSUM > "${MEDIA_BACKUP}.sha256"
        
        # Chiffrer si KEY_GPG défini
        if [ ! -z "$GPG_PASSPHRASE" ]; then
            gpg --symmetric --cipher-algo AES256 \
                --passphrase "$GPG_PASSPHRASE" \
                --batch --yes \
                -o "${MEDIA_BACKUP}.gpg" $MEDIA_BACKUP
            
            if [ $? -eq 0 ]; then
                rm $MEDIA_BACKUP
            fi
        fi
    else
        log "${RED}✗ Backup médias échoué${NC}"
    fi
fi

# Upload S3 si configuré
if [ ! -z "$AWS_BUCKET" ]; then
    log "${YELLOW}Upload vers S3...${NC}"
    
    if [ -f "${DB_BACKUP}.gpg" ]; then
        aws s3 cp "${DB_BACKUP}.gpg" "s3://${AWS_BUCKET}/${APP_NAME}/db_${DATE}.gpg" 2>> $LOG_FILE
    else
        aws s3 cp $DB_BACKUP "s3://${AWS_BUCKET}/${APP_NAME}/db_${DATE}.sql" 2>> $LOG_FILE
    fi
    
    if [ $? -eq 0 ]; then
        log "${GREEN}✓ Upload S3 réussi${NC}"
    else
        log "${RED}✗ Upload S3 échoué${NC}"
    fi
fi

# Cleanup anciens backups (30 jours)
log "${YELLOW}Nettoyage backups anciens de 30 jours...${NC}"
find $BACKUP_DIR -name "*.sql*" -mtime +30 -delete 2>> $LOG_FILE
find $BACKUP_DIR -name "*.tar.gz*" -mtime +30 -delete 2>> $LOG_FILE

log "${GREEN}Cleanup terminé${NC}"

# Fin
log "=========================================="
log "Backup terminé avec succès"
log "=========================================="

exit 0
