"""
Commande Django pour exécuter le worker email asynchrone
"""
from django.core.management.base import BaseCommand
from email_service.services import EmailWorker
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Exécute le worker pour traiter la file d\'attente d\'emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Intervalle en secondes entre chaque cycle de traitement (défaut: 30)'
        )
        parser.add_argument(
            '--max-emails',
            type=int,
            default=100,
            help='Nombre maximum d\'emails à traiter par cycle (défaut: 100)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Traiter un seul cycle puis quitter'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        max_emails = options['max_emails']
        once = options['once']

        self.stdout.write(self.style.SUCCESS(
            f'📧 Worker email démarré (interval={interval}s, max_emails={max_emails})'
        ))

        iteration = 0
        while True:
            iteration += 1
            self.stdout.write(f'\n[{timezone.now()}] Cycle {iteration}')

            try:
                processed = EmailWorker.process_queue(max_emails=max_emails)
                
                if processed > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ {processed} email(s) traités avec succès'
                    ))
                else:
                    self.stdout.write('ℹ️ Aucun email en attente')

            except Exception as e:
                logger.error(f'Erreur dans le worker email: {e}', exc_info=True)
                self.stdout.write(self.style.ERROR(f'❌ Erreur: {e}'))

            if once:
                break

            time.sleep(interval)
