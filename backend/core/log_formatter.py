"""
SGHL — JSON Log Formatter compatible ELK Stack
================================================
Produit des logs JSON structurés lisibles par :
  - Filebeat (collecte) → Logstash (transformation) → Elasticsearch (stockage) → Kibana (visualisation)
  - Ou directement : Filebeat → Elasticsearch → Kibana (ELK simplifié)
"""
import json
import logging
import traceback
from datetime import datetime, timezone


class SGHLJsonFormatter(logging.Formatter):
    """
    Formate chaque entrée de log en JSON ligne-par-ligne.
    Format compatible @timestamp ECS (Elastic Common Schema).
    """

    SERVICE_NAME = 'sghl-backend'
    SERVICE_VERSION = '1.0.0'

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            # Champs ECS standards
            '@timestamp':    datetime.now(timezone.utc).isoformat(),
            'log.level':     record.levelname,
            'log.logger':    record.name,
            'message':       record.getMessage(),

            # Service
            'service.name':    self.SERVICE_NAME,
            'service.version': self.SERVICE_VERSION,
            'service.environment': 'development',  # override en prod via env

            # Source du log
            'log.origin.file.name': record.filename,
            'log.origin.file.line': record.lineno,
            'log.origin.function':  record.funcName,

            # Process
            'process.pid':     record.process,
            'process.name':    record.processName,
            'thread.id':       record.thread,
        }

        # Champs extra injectés par les vues Django (request context)
        for key in ('user_id', 'user_email', 'ip_address', 'request_id',
                    'patient_id', 'action', 'module', 'http_method',
                    'url_path', 'response_status', 'duration_ms'):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        # Exception si présente
        if record.exc_info:
            log_entry['error.type']       = record.exc_info[0].__name__ if record.exc_info[0] else None
            log_entry['error.message']    = str(record.exc_info[1]) if record.exc_info[1] else None
            log_entry['error.stack_trace'] = ''.join(traceback.format_exception(*record.exc_info))

        return json.dumps(log_entry, ensure_ascii=False, default=str)
