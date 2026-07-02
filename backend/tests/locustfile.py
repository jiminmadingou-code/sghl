"""
Tests de charge SGHL avec Locust.
Usage:
  locust -f locustfile.py --host=http://localhost:8000
  locust -f locustfile.py --headless -u 100 -r 10 -t 5m --host=http://localhost:8000
"""
from locust import HttpUser, task, between, events
import json
import random


class SGHLUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Authentification au démarrage."""
        response = self.client.post('/api/v1/auth/login/', json={
            'username': 'admin',
            'password': 'Admin@2025!'
        }, catch_response=True)
        if response.status_code == 200:
            self.token = response.json().get('access')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})
        else:
            response.failure(f'Login échoué: {response.status_code}')

    @task(5)
    def get_dashboard(self):
        self.client.get('/api/v1/dashboard/summary', name='Dashboard Summary')

    @task(4)
    def list_patients(self):
        self.client.get('/api/v1/patients/', name='List Patients')

    @task(3)
    def search_patient(self):
        noms = ['Diallo', 'Koné', 'Traoré', 'Bah', 'Camara']
        self.client.get(f'/api/v1/patients/?search={random.choice(noms)}', name='Search Patient')

    @task(3)
    def list_hospitalisations(self):
        self.client.get('/api/v1/hospitalisations/', name='List Hospitalisations')

    @task(2)
    def list_examens_labo(self):
        self.client.get('/api/v1/laboratoire/', name='List Examens Labo')

    @task(2)
    def list_pharmacie(self):
        self.client.get('/api/v1/pharmacie/inventaire/', name='Inventaire Pharmacie')

    @task(2)
    def list_factures(self):
        self.client.get('/api/v1/facturation/', name='List Factures')

    @task(1)
    def health_check(self):
        self.client.get('/api/v1/sante/', name='Health Check')

    @task(1)
    def kpi_hospitalisations(self):
        self.client.get('/api/v1/dashboard/kpi/hospitalisations', name='KPI Hospitalisations')

    @task(1)
    def kpi_finances(self):
        self.client.get('/api/v1/dashboard/kpi/finances', name='KPI Finances')

    @task(1)
    def list_personnel(self):
        self.client.get('/api/v1/personnel/', name='List Personnel')

    @task(1)
    def list_rdv(self):
        self.client.get('/api/v1/rendez-vous/', name='List RDV')

    @task(1)
    def alertes_stock(self):
        self.client.get('/api/v1/pharmacie/alertes/', name='Alertes Stock')


class SGHLAdminUser(HttpUser):
    """Simule un administrateur avec des opérations d'écriture."""
    wait_time = between(3, 8)
    weight = 1  # Moins fréquent que les lectures

    def on_start(self):
        response = self.client.post('/api/v1/auth/login/', json={
            'username': 'admin', 'password': 'Admin@2025!'
        })
        if response.status_code == 200:
            self.token = response.json().get('access')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(2)
    def create_patient(self):
        self.client.post('/api/v1/patients/', json={
            'prenom': f'Test{random.randint(1000,9999)}',
            'nom': 'LoadTest',
            'date_naissance': '1990-01-01',
            'sexe': 'M',
            'telephone': f'6{random.randint(10000000,99999999)}'
        }, name='Create Patient')

    @task(1)
    def create_examen(self):
        self.client.post('/api/v1/laboratoire/', json={
            'patient_id': 1,
            'prescripteur_id': 1,
            'type_examen': 'NFS',
            'priorite': 'Normal'
        }, name='Create Examen')


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🚀 Démarrage des tests de charge SGHL")
    print(f"   Host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    print(f"\n📊 Résultats:")
    print(f"   Requêtes totales : {stats.num_requests}")
    print(f"   Échecs           : {stats.num_failures}")
    print(f"   Temps réponse P95: {stats.get_response_time_percentile(0.95):.0f}ms")
    print(f"   Temps réponse P99: {stats.get_response_time_percentile(0.99):.0f}ms")
    print(f"   RPS moyen        : {stats.current_rps:.1f}")
