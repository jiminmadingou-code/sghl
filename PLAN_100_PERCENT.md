# 🚀 PLAN D'ACTION POUR ATTEINDRE 100% DE CONFORMITÉ

## 📊 État Actuel: 82% → Objectif: 100% (+18%)

---

## **PHASE 1: CRITIQUES (Impact: +15% - Délai: 3-4 semaines)**

### 1.1 Tests E2E Frontend (Vue.js) - Impact: +5%

#### Objectif
Automatiser les tests des flux utilisateur critiques sur le frontend Vue.js

#### Outils
- **Playwright** (recommandé): UI testing moderne, cross-browser
- Alternativement: **Cypress** ou **Selenium**

#### Fichiers à Créer

**1. Installation dépendances**
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

**2. Configuration Playwright** - `frontend/playwright.config.js`
```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

**3. Tests E2E** - `frontend/tests/e2e/auth.spec.js`
```javascript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('Login avec credentials valides', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test_user');
    await page.fill('input[name="password"]', 'test_password');
    await page.click('button:has-text("Connexion")');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('Affichage erreur login échoué', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'invalid');
    await page.fill('input[name="password"]', 'wrong');
    await page.click('button:has-text("Connexion")');
    await expect(page.locator('text=Identifiants invalides')).toBeVisible();
  });
});

test.describe('Patient Dashboard', () => {
  test.beforeEach(async ({ page, context }) => {
    // Login avant chaque test
    await page.goto('/login');
    await page.fill('input[name="username"]', 'patient@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.click('button:has-text("Connexion")');
    await page.waitForURL(/\/dashboard/);
  });

  test('Affichage historique médical', async ({ page }) => {
    await page.goto('/medical-history');
    await expect(page.locator('text=Historique Médical')).toBeVisible();
    const records = await page.locator('.medical-record').count();
    expect(records).toBeGreaterThan(0);
  });

  test('Télécharger résultats PDF', async ({ page }) => {
    await page.goto('/lab-results');
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Télécharger PDF")')
    ]);
    expect(download.suggestedFilename()).toContain('.pdf');
  });

  test('Prendre rendez-vous', async ({ page }) => {
    await page.goto('/appointments');
    await page.click('button:has-text("Nouveau RDV")');
    await page.selectOption('select[name="doctor"]', { label: 'Dr. Dupont' });
    await page.fill('input[type="date"]', '2026-07-15');
    await page.click('button:has-text("Confirmer")');
    await expect(page.locator('text=RDV confirmé')).toBeVisible();
  });
});

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin@sghl.com');
    await page.fill('input[name="password"]', 'AdminPass123!');
    await page.click('button:has-text("Connexion")');
    await page.waitForURL(/\/admin\/dashboard/);
  });

  test('Affichage KPIs temps réel', async ({ page }) => {
    await page.goto('/admin/dashboard');
    await expect(page.locator('[data-testid="kpi-patients"]')).toBeVisible();
    await expect(page.locator('[data-testid="kpi-occupation"]')).toBeVisible();
    await expect(page.locator('[data-testid="kpi-revenue"]')).toBeVisible();
  });

  test('Charger patients liste', async ({ page }) => {
    await page.goto('/admin/patients');
    await page.waitForLoadState('networkidle');
    const rows = await page.locator('table tbody tr').count();
    expect(rows).toBeGreaterThan(0);
  });
});
```

**4. Package.json scripts**
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug"
  }
}
```

**5. CI/CD Integration** - `.github/workflows/e2e-tests.yml`
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run build
      - run: cd frontend && npx playwright install
      - run: cd frontend && npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

### 1.2 Tests E2E Mobile (Flutter) - Impact: +5%

#### Objectif
Automatiser tests de l'application Flutter

#### Outils
- **Flutter Integration Tests** (natif)
- Alternativement: **Appium** pour cross-platform

#### Fichiers à Créer

**1. Integration Test** - `mobile/patient_app/integration_test/app_test.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:patient_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Patient App E2E Tests', () {
    testWidgets('Login Flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Vérifier écran de login
      expect(find.byType(TextField), findsWidgets);
      
      // Remplir credentials
      await tester.enterText(
        find.byKey(const ValueKey('username_field')),
        'patient@example.com'
      );
      await tester.enterText(
        find.byKey(const ValueKey('password_field')),
        'SecurePass123!'
      );
      
      // Tap login button
      await tester.tap(find.byKey(const ValueKey('login_btn')));
      await tester.pumpAndSettle();

      // Vérifier dashboard après login
      expect(find.byType(Dashboard), findsOneWidget);
    });

    testWidgets('Medical History View', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Login first
      await loginAsPatient(tester);

      // Navigate to medical history
      await tester.tap(find.byIcon(Icons.history));
      await tester.pumpAndSettle();

      // Verify medical records loaded
      expect(find.byType(MedicalRecordCard), findsWidgets);
    });

    testWidgets('Lab Results Download', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Login first
      await loginAsPatient(tester);

      // Navigate to lab results
      await tester.tap(find.byIcon(Icons.science));
      await tester.pumpAndSettle();

      // Tap download button
      await tester.tap(find.byKey(const ValueKey('download_pdf_btn')));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify download notification
      expect(find.byType(SnackBar), findsOneWidget);
    });

    testWidgets('Chat Real-time', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Login first
      await loginAsPatient(tester);

      // Navigate to chat
      await tester.tap(find.byIcon(Icons.chat));
      await tester.pumpAndSettle();

      // Send message
      await tester.enterText(
        find.byKey(const ValueKey('chat_input')),
        'Bonjour docteur'
      );
      await tester.tap(find.byKey(const ValueKey('send_btn')));
      await tester.pumpAndSettle();

      // Verify message sent
      expect(find.text('Bonjour docteur'), findsOneWidget);
    });
  });
}

Future<void> loginAsPatient(WidgetTester tester) async {
  await tester.enterText(
    find.byKey(const ValueKey('username_field')),
    'patient@example.com'
  );
  await tester.enterText(
    find.byKey(const ValueKey('password_field')),
    'SecurePass123!'
  );
  await tester.tap(find.byKey(const ValueKey('login_btn')));
  await tester.pumpAndSettle();
}
```

**2. Exécution tests**
```bash
cd mobile/patient_app

# Tests intégration sur device/émulateur
flutter test integration_test/app_test.dart

# Mode release
flutter test integration_test/app_test.dart --release
```

---

### 1.3 Tests de Charge API (Locust) - Impact: +3%

#### Objectif
Valider que l'API supporte la charge attendue (< 2s response time)

#### Fichiers à Créer

**1. Installation**
```bash
cd backend
pip install locust
```

**2. Locustfile** - `backend/tests/locustfile.py`
```python
from locust import HttpUser, task, between, events
import json
from datetime import datetime

class SGHLUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login au démarrage"""
        response = self.client.post(
            "/api/v1/auth/login/",
            json={
                "username": "test_user",
                "password": "test_password"
            }
        )
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed: {response.text}")
    
    @task(5)
    def get_patients(self):
        """Lister patients - 5x frequence"""
        self.client.get(
            "/api/v1/patients/?page=1&page_size=50",
            name="/api/v1/patients"
        )
    
    @task(3)
    def get_hospitalisations(self):
        """Lister hospitalisations - 3x frequence"""
        self.client.get(
            "/api/v1/hospitalisations/?page=1",
            name="/api/v1/hospitalisations"
        )
    
    @task(2)
    def get_dashboard(self):
        """Dashboard KPIs - 2x frequence"""
        self.client.get("/api/v1/dashboard/summary")
    
    @task(2)
    def get_lab_results(self):
        """Résultats labo"""
        self.client.get(
            "/api/v1/laboratoire/examens/?status=Validé",
            name="/api/v1/laboratoire/examens"
        )
    
    @task(1)
    def create_patient(self):
        """Créer patient - rare"""
        self.client.post(
            "/api/v1/patients/",
            json={
                "nom": "Dupont",
                "prenom": "Jean",
                "date_naissance": "1985-05-15",
                "sexe": "M",
                "email": f"patient_{datetime.now().timestamp()}@example.com"
            },
            name="/api/v1/patients POST"
        )
    
    @task(1)
    def get_audit_logs(self):
        """Lister audit trail"""
        self.client.get(
            "/api/v1/audit/?page=1&limit=50",
            name="/api/v1/audit"
        )


class AdminUser(HttpUser):
    """Utilisateur admin (charge plus légère)"""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login admin"""
        response = self.client.post(
            "/api/v1/auth/login/",
            json={
                "username": "admin_user",
                "password": "admin_password"
            }
        )
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_dashboard(self):
        """Dashboard stats"""
        self.client.get("/api/v1/dashboard/summary")
    
    @task(2)
    def get_health(self):
        """Health endpoint"""
        self.client.get("/api/v1/health/")
    
    @task(1)
    def get_financial_reports(self):
        """Rapports financiers"""
        self.client.get("/api/v1/facturation/rapports/")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🚀 Démarrage tests de charge...")
    print(f"   Timestamp: {datetime.now().isoformat()}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("✅ Tests de charge terminés")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    # Afficher statistiques
    for stat_name, stat in environment.stats.entries.items():
        print(f"\n{stat_name}:")
        print(f"   Requests: {stat.num_requests}")
        print(f"   Failures: {stat.num_failures}")
        print(f"   Avg Response: {stat.avg_response_time:.0f}ms")
        print(f"   Max Response: {stat.max_response_time:.0f}ms")
        print(f"   Min Response: {stat.min_response_time:.0f}ms")
```

**3. Script exécution tests**
```bash
#!/bin/bash
# backend/scripts/load_test.sh

cd "$(dirname "$0")/.."

echo "🔧 Préparation tests de charge..."

# Démarrer serveur si nécessaire
if ! curl -s http://localhost:8000/api/v1/health/ > /dev/null; then
    echo "⚠️  Serveur non accessible. Démarrez-le avec: python manage.py runserver"
    exit 1
fi

echo "✅ Serveur OK"
echo ""
echo "Tests scenarios:"
echo "  1. Charge normale (50 users)"
echo "  2. Charge moyenne (100 users)"
echo "  3. Charge élevée (200 users)"
echo "  4. Pic soudain (500 users, 1 min)"
echo ""

# Scenario 1: Normal
echo "📊 Scenario 1: Charge normale (50 utilisateurs, 5 min)..."
locust -f tests/locustfile.py \
    --headless \
    --users 50 \
    --spawn-rate 5 \
    --run-time 5m \
    --host http://localhost:8000 \
    --csv results/normal_50

# Scenario 2: Moyenne
echo "📊 Scenario 2: Charge moyenne (100 utilisateurs, 5 min)..."
locust -f tests/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host http://localhost:8000 \
    --csv results/medium_100

# Scenario 3: Élevée
echo "📊 Scenario 3: Charge élevée (200 utilisateurs, 5 min)..."
locust -f tests/locustfile.py \
    --headless \
    --users 200 \
    --spawn-rate 20 \
    --run-time 5m \
    --host http://localhost:8000 \
    --csv results/high_200

# Scenario 4: Pic
echo "📊 Scenario 4: Pic soudain (500 utilisateurs, 1 min)..."
locust -f tests/locustfile.py \
    --headless \
    --users 500 \
    --spawn-rate 100 \
    --run-time 1m \
    --host http://localhost:8000 \
    --csv results/spike_500

echo "✅ Tests terminés!"
echo ""
echo "📈 Résultats dans: results/"
```

**4. CI/CD - `.github/workflows/load-tests.yml`**
```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: sghl_test
          POSTGRES_USER: sghl_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: |
          cd backend
          pip install -r requirements.txt
          pip install locust
          
      - run: |
          cd backend
          python manage.py migrate
          python manage.py runserver &
          sleep 5
          
      - run: |
          cd backend
          locust -f tests/locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 3m \
            --host http://localhost:8000
      
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: load-test-results
          path: backend/results/
```

---

### 1.4 Finaliser Widgets Flutter - Impact: +5%

#### Objectif
Compléter l'interface utilisateur Flutter avec tous les écrans

#### Fichiers à Créer/Compléter

**1. Structure organiser** - `mobile/patient_app/lib/features/`
```
features/
├── auth/
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── register_screen.dart
│   │   └── mfa_screen.dart
│   ├── widgets/
│   │   └── login_form.dart
│   └── providers/
│       └── auth_provider.dart
├── appointments/
│   ├── screens/
│   │   ├── appointments_list_screen.dart
│   │   ├── appointment_detail_screen.dart
│   │   └── book_appointment_screen.dart
│   ├── widgets/
│   │   ├── appointment_card.dart
│   │   ├── calendar_picker.dart
│   │   └── doctor_selector.dart
│   └── providers/
│       └── appointments_provider.dart
├── medical_history/
│   ├── screens/
│   │   ├── medical_history_screen.dart
│   │   └── consultation_detail_screen.dart
│   ├── widgets/
│   │   └── medical_record_card.dart
│   └── providers/
│       └── medical_history_provider.dart
├── lab_results/
│   ├── screens/
│   │   ├── lab_results_screen.dart
│   │   └── result_detail_screen.dart
│   ├── widgets/
│   │   └── result_card.dart
│   └── providers/
│       └── lab_results_provider.dart
├── chat/
│   ├── screens/
│   │   ├── chat_list_screen.dart
│   │   └── chat_detail_screen.dart
│   ├── widgets/
│   │   ├── chat_bubble.dart
│   │   └── message_input.dart
│   └── providers/
│       └── chat_provider.dart
├── notifications/
│   ├── screens/
│   │   └── notifications_screen.dart
│   ├── widgets/
│   │   └── notification_item.dart
│   └── providers/
│       └── notifications_provider.dart
└── dashboard/
    ├── screens/
    │   └── dashboard_screen.dart
    ├── widgets/
    │   ├── quick_actions.dart
    │   ├── upcoming_appointments_card.dart
    │   └── health_summary_card.dart
    └── providers/
        └── dashboard_provider.dart
```

**2. Authentication Provider** - `mobile/patient_app/lib/features/auth/providers/auth_provider.dart`
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

class AuthState {
  final String? token;
  final String? userId;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;

  AuthState({
    this.token,
    this.userId,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });

  AuthState copyWith({
    String? token,
    String? userId,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) => AuthState(
    token: token ?? this.token,
    userId: userId ?? this.userId,
    isLoading: isLoading ?? this.isLoading,
    error: error ?? this.error,
    isAuthenticated: isAuthenticated ?? this.isAuthenticated,
  );
}

class AuthNotifier extends StateNotifier<AuthState> {
  final dio = Dio();
  late SharedPreferences prefs;

  AuthNotifier() : super(const AuthState()) {
    _init();
  }

  Future<void> _init() async {
    prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token != null) {
      state = state.copyWith(
        token: token,
        isAuthenticated: true,
      );
      dio.options.headers['Authorization'] = 'Bearer $token';
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await dio.post(
        'http://localhost:8000/api/v1/auth/login/',
        data: {'username': username, 'password': password},
      );

      final token = response.data['access'];
      final userId = response.data['user_id'];

      await prefs.setString('access_token', token);
      await prefs.setString('user_id', userId);

      dio.options.headers['Authorization'] = 'Bearer $token';

      state = state.copyWith(
        token: token,
        userId: userId,
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Erreur de connexion: ${e.toString()}',
      );
    }
  }

  Future<void> logout() async {
    await prefs.clear();
    state = const AuthState();
    dio.options.headers.remove('Authorization');
  }
}
```

**3. Login Screen** - `mobile/patient_app/lib/features/auth/screens/login_screen.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final usernameCtrl = TextEditingController();
    final passwordCtrl = TextEditingController();

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              // Logo
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.blue[600],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(
                  Icons.hospital_box,
                  size: 40,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 30),
              // Titre
              Text(
                'SGHL - Patient',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Système de Gestion Hospitalière',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 40),
              // Erreur
              if (authState.error != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    border: Border.all(color: Colors.red[300]!),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    authState.error!,
                    style: TextStyle(color: Colors.red[700]),
                  ),
                ),
              if (authState.error != null)
                const SizedBox(height: 20),
              // Username
              TextField(
                controller: usernameCtrl,
                key: const ValueKey('username_field'),
                decoration: InputDecoration(
                  hintText: 'Email ou identifiant',
                  prefixIcon: const Icon(Icons.person),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  filled: true,
                  fillColor: Colors.grey[50],
                ),
              ),
              const SizedBox(height: 15),
              // Password
              TextField(
                controller: passwordCtrl,
                key: const ValueKey('password_field'),
                obscureText: true,
                decoration: InputDecoration(
                  hintText: 'Mot de passe',
                  prefixIcon: const Icon(Icons.lock),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  filled: true,
                  fillColor: Colors.grey[50],
                ),
              ),
              const SizedBox(height: 30),
              // Login Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  key: const ValueKey('login_btn'),
                  onPressed: authState.isLoading
                    ? null
                    : () {
                      ref.read(authProvider.notifier).login(
                        usernameCtrl.text,
                        passwordCtrl.text,
                      );
                    },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: authState.isLoading
                    ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(Colors.white),
                      ),
                    )
                    : const Text(
                      'Connexion',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

**4. Dashboard Screen** - `mobile/patient_app/lib/features/dashboard/screens/dashboard_screen.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tableau de Bord'),
        elevation: 0,
        backgroundColor: Colors.blue[600],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Health Summary Card
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.blue[600]!, Colors.blue[400]!],
                ),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Santé Générale',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Bon',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 15),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _HealthMetric(
                        label: 'Température',
                        value: '37.2°C',
                        status: 'Normal',
                      ),
                      _HealthMetric(
                        label: 'Pouls',
                        value: '72',
                        status: 'Normal',
                      ),
                      _HealthMetric(
                        label: 'Pression',
                        value: '120/80',
                        status: 'Normal',
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Quick Actions
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Actions Rapides',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    childAspectRatio: 1.2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    children: [
                      _QuickActionCard(
                        icon: Icons.calendar_today,
                        label: 'Rendez-vous',
                        color: Colors.blue,
                        onTap: () {},
                      ),
                      _QuickActionCard(
                        icon: Icons.science,
                        label: 'Résultats',
                        color: Colors.green,
                        onTap: () {},
                      ),
                      _QuickActionCard(
                        icon: Icons.history,
                        label: 'Historique',
                        color: Colors.orange,
                        onTap: () {},
                      ),
                      _QuickActionCard(
                        icon: Icons.chat,
                        label: 'Messages',
                        color: Colors.purple,
                        onTap: () {},
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            // Upcoming Appointments
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Prochains Rendez-vous',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _UpcomingAppointmentCard(
                    doctor: 'Dr. Dupont',
                    specialty: 'Généraliste',
                    date: '2026-07-15',
                    time: '10:30',
                  ),
                  const SizedBox(height: 10),
                  _UpcomingAppointmentCard(
                    doctor: 'Dr. Martin',
                    specialty: 'Cardiologue',
                    date: '2026-07-20',
                    time: '14:00',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}

class _HealthMetric extends StatelessWidget {
  final String label;
  final String value;
  final String status;

  const _HealthMetric({
    required this.label,
    required this.value,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white70,
          ),
        ),
      ],
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: color.withOpacity(0.3),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UpcomingAppointmentCard extends StatelessWidget {
  final String doctor;
  final String specialty;
  final String date;
  final String time;

  const _UpcomingAppointmentCard({
    required this.doctor,
    required this.specialty,
    required this.date,
    required this.time,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.blue[100],
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(Icons.person, color: Colors.blue[600]),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  doctor,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  specialty,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(date),
              Text(
                time,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
```

---

### 1.5 Monitoring Prometheus/Grafana - Impact: +5%

#### Objectif
Configurer monitoring en temps réel de l'application

#### Fichiers à Créer

**1. Docker Compose Monitoring** - `monitoring/docker-compose.monitoring.yml`
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: sghl-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: sghl-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_SECURITY_ADMIN_USER=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: sghl-node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

**2. Prometheus Config** - `monitoring/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'sghl-monitor'

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics/'
    scrape_interval: 10s
    scrape_timeout: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

**3. Alert Rules** - `monitoring/alert_rules.yml`
```yaml
groups:
  - name: sghl_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          (sum(rate(django_http_requests_total{status=~"5.."}[5m])) /
           sum(rate(django_http_requests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreur élevé ({{ $value | humanizePercentage }})"

      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.99, django_http_request_duration_seconds_bucket) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Temps réponse lent: {{ $value }}s"

      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Utilisation mémoire élevée: {{ $value | humanizePercentage }}"

      - alert: DiskSpaceRunningOut
        expr: |
          (node_filesystem_avail_bytes{fstype=~"ext4|xfs"} / 
           node_filesystem_size_bytes{fstype=~"ext4|xfs"}) < 0.1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Espace disque faible: {{ $value | humanizePercentage }}"

      - alert: DatabaseConnectionPoolExhausted
        expr: |
          django_db_connection_pool_size - django_db_connection_pool_available < 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Pool de connexion DB presque épuisée"

      - alert: RedisMemoryHigh
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation mémoire Redis: {{ $value | humanizePercentage }}"
```

**4. Backend Django Metrics** - `backend/core/metrics.py`
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
http_requests_total = Counter(
    'django_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'django_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Database metrics
db_connection_pool_size = Gauge(
    'django_db_connection_pool_size',
    'Database connection pool size'
)

db_connection_pool_available = Gauge(
    'django_db_connection_pool_available',
    'Available database connections'
)

# Business metrics
active_patients = Gauge(
    'sghl_active_patients',
    'Total active patients'
)

bed_occupation_rate = Gauge(
    'sghl_bed_occupation_rate',
    'Hospital bed occupation rate',
    ['building', 'service']
)

pending_lab_exams = Gauge(
    'sghl_pending_lab_exams',
    'Pending laboratory examinations'
)

revenue_daily = Gauge(
    'sghl_revenue_daily',
    'Daily revenue'
)

# Middleware pour instrumenter les requêtes
class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Record metrics
        endpoint = request.path.split('/')[1] if request.path else 'unknown'
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
```

**5. Grafana Dashboards** - `monitoring/grafana/provisioning/dashboards/sghl-dashboard.json`
```json
{
  "dashboard": {
    "title": "SGHL - Monitoring",
    "panels": [
      {
        "title": "Requêtes HTTP (par seconde)",
        "targets": [
          {
            "expr": "sum(rate(django_http_requests_total[1m])) by (status)"
          }
        ]
      },
      {
        "title": "Temps de réponse (P99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, django_http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Patients Actifs",
        "targets": [
          {
            "expr": "sghl_active_patients"
          }
        ]
      },
      {
        "title": "Taux d'Occupation Lits",
        "targets": [
          {
            "expr": "sghl_bed_occupation_rate"
          }
        ]
      },
      {
        "title": "Examens Labo en Attente",
        "targets": [
          {
            "expr": "sghl_pending_lab_exams"
          }
        ]
      },
      {
        "title": "Revenu Quotidien",
        "targets": [
          {
            "expr": "sghl_revenue_daily"
          }
        ]
      },
      {
        "title": "Utilisation CPU",
        "targets": [
          {
            "expr": "1 - avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m]))"
          }
        ]
      },
      {
        "title": "Utilisation Mémoire",
        "targets": [
          {
            "expr": "1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)"
          }
        ]
      }
    ]
  }
}
```

---

## **PHASE 2: HAUTE PRIORITÉ (Impact: +3% - Délai: 1-2 semaines)**

### 2.1 Factures PDF Signées - Impact: +2%

**Fichier** - `backend/facturation/pdf_generator.py`

```python
from weasyprint import HTML, CSS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io

class FacturePDF:
    @staticmethod
    def generate(facture):
        """Générer PDF facture signée"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # En-tête
        story.append(Paragraph("FACTURE SGHL", styles['Title']))
        story.append(Paragraph(f"N° {facture.id}", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Dates
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
        )
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", date_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Patient
        story.append(Paragraph("CLIENT", styles['Heading3']))
        story.append(Paragraph(
            f"{facture.patient.prenom} {facture.patient.nom}<br/>"
            f"{facture.patient.adresse}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Détails
        story.append(Paragraph("DÉTAILS FACTURE", styles['Heading3']))
        
        # Table détails
        data = [['Description', 'Montant']]
        if facture.type_facture == 'Consultation':
            data.append(['Consultation médicale', f"{facture.montant_total} €"])
        elif facture.type_facture == 'Hospitalisation':
            data.append(['Séjour hospitalier', f"{facture.montant_total} €"])
        elif facture.type_facture == 'Examens':
            data.append(['Examens et analyses', f"{facture.montant_total} €"])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totaux
        totals_data = [
            ['Montant Total:', f"{facture.montant_total} €"],
            ['Montant Payé:', f"{facture.montant_paye} €"],
            ['Solde:', f"{facture.solde} €"],
        ]
        totals_table = Table(totals_data)
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Signature
        story.append(Paragraph("Signature Électronique", styles['Heading4']))
        story.append(Paragraph(
            f"Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br/>"
            f"Signé par: Système SGHL<br/>"
            f"Contrôle: {facture.id}",
            date_style
        ))
        
        doc.build(story)
        return buffer.getvalue()
    
    @staticmethod
    def generate_response(facture):
        """Retourner réponse HTTP avec PDF"""
        from django.http import HttpResponse
        
        pdf_bytes = FacturePDF.generate(facture)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.id}.pdf"'
        return response
```

### 2.2 Tests Charge Backend - Impact: +1%

(Déjà couverts dans Phase 1, section 1.3)

---

## **PHASE 3: MOYENNE PRIORITÉ (Impact: +3% - Délai: 2-3 semaines)**

### 3.1 HL7/FHIR Implementation - Impact: +2%

**Fichier** - `backend/interoperabilite/fhir_converter.py`

```python
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.observation import Observation
from fhir.resources.lab_result import DiagnosticReport
from fhir.resources.medication import Medication
from fhir.resources.medication_request import MedicationRequest
import json

class FHIRConverter:
    @staticmethod
    def patient_to_fhir(patient):
        """Convertir Patient SGHL vers FHIR"""
        fhir_patient = FHIRPatient(
            id=str(patient.id),
            name=[{
                "family": patient.nom,
                "given": [patient.prenom]
            }],
            birthDate=patient.date_naissance.isoformat(),
            gender="male" if patient.sexe == "M" else "female",
            telecom=[{
                "system": "email",
                "value": patient.email
            }],
            address=[{
                "use": "home",
                "text": patient.adresse
            }]
        )
        return fhir_patient.dict(by_alias=True, exclude_none=True)
    
    @staticmethod
    def constante_vitale_to_fhir(constante):
        """Convertir ConstanteVitale vers FHIR Observation"""
        
        code_mapping = {
            'Temperature': '8310-5',
            'Pouls': '8867-4',
            'Pression': '55284-4',
            'SaturationO2': '2708-6',
            'Glycemie': '2345-7',
        }
        
        observation = Observation(
            id=str(constante.id),
            status="final",
            subject={"reference": f"Patient/{constante.hospitalisation.patient.id}"},
            code={
                "coding": [{
                    "system": "http://loinc.org",
                    "code": code_mapping.get(constante.type_constante, "unknown")
                }]
            },
            valueQuantity={
                "value": constante.valeur,
                "unit": constante.unite or "N/A"
            },
            effectiveDateTime=constante.date_saisie.isoformat()
        )
        return observation.dict(by_alias=True, exclude_none=True)
    
    @staticmethod
    def examen_labo_to_fhir(examen):
        """Convertir ExamenLaboratoire vers FHIR DiagnosticReport"""
        
        report = DiagnosticReport(
            id=str(examen.id),
            status="final" if examen.statut == "Publié" else "preliminary",
            subject={"reference": f"Patient/{examen.patient.id}"},
            performer=[{
                "reference": f"Practitioner/{examen.valide_par.id}"
            }],
            code={
                "coding": [{
                    "system": "http://loinc.org",
                    "display": examen.type_examen
                }]
            },
            issued=examen.date_validation.isoformat() if examen.date_validation else None,
            conclusion=examen.resultat
        )
        return report.dict(by_alias=True, exclude_none=True)


class HL7Converter:
    @staticmethod
    def patient_to_hl7v2(patient):
        """Convertir Patient vers HL7 v2.x"""
        
        hl7_message = f"""MSH|^~\&|SGHL|HOSPITAL|RECEIVER|DEST|{datetime.now().isoformat()}||ADT^A01|MSG001|P|2.5
PID|1||{patient.id}^PID001||{patient.nom}^{patient.prenom}||{patient.date_naissance}|{patient.sexe}|||{patient.adresse}|||{patient.telephone}|{patient.email}|||||{patient.groupe_sanguin}
"""
        return hl7_message
```

### 3.2 WCAG Compliance Audit - Impact: +1%

**Checklist** - `WCAG_COMPLIANCE.md`

```markdown
# ✅ WCAG 2.1 AA Compliance Audit

## Color Contrast
- [ ] All text >= 4.5:1 ratio (normal text)
- [ ] All UI >= 3:1 ratio

## Keyboard Navigation
- [ ] All interactive elements accessible via Tab
- [ ] Focus visible with clear indicator
- [ ] Logical tab order

## Screen Reader Support
- [ ] All images have alt text
- [ ] Form labels associated with inputs
- [ ] Landmark regions defined (header, nav, main, footer)
- [ ] ARIA labels where needed

## Mobile Accessibility
- [ ] Touch targets >= 44x44 pixels
- [ ] Responsive design tested
- [ ] Orientation independent

## Forms
- [ ] Required fields marked
- [ ] Error messages clear
- [ ] Help text available
- [ ] Validation feedback immediate

## Text & Readability
- [ ] Font size >= 12px
- [ ] Line spacing >= 1.5
- [ ] Line length <= 80 characters
- [ ] Avoid CAPS LOCK only
```

---

## **PHASE 4: BASSE PRIORITÉ (Impact: +2% - Délai: 1-2 semaines)**

### 4.1 ELK Stack (Optionnel) - Impact: +1%

**Docker Compose** - `monitoring/docker-compose.elk.yml`

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: sghl-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: sghl-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: sghl-logstash
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: sghl-filebeat
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: filebeat -e -strict.perms=false
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### 4.2 Antivirus Integration - Impact: +1%

**Backend** - `backend/core/antivirus.py` (amélioration)

```python
import subprocess
import os
from pathlib import Path

class AntivirusScanner:
    """Wrapper pour ClamAV ou équivalent"""
    
    @staticmethod
    def scan_file(file_path):
        """Scanner un fichier avec ClamAV"""
        
        try:
            result = subprocess.run(
                ['clamscan', '-i', str(file_path)],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {'clean': True, 'threat': None}
            elif result.returncode == 1:
                threat = result.stdout.decode().split(': ')[-1].strip()
                return {'clean': False, 'threat': threat}
            else:
                return {'clean': None, 'error': 'Scan failed'}
                
        except subprocess.TimeoutExpired:
            return {'clean': None, 'error': 'Scan timeout'}
        except Exception as e:
            return {'clean': None, 'error': str(e)}
    
    @staticmethod
    def update_definitions():
        """Mettre à jour les signatures de virus"""
        try:
            subprocess.run(['freshclam'], check=True)
            return True
        except:
            return False


# Django Middleware
from django.core.files.uploadhandler import FileUploadHandler

class AntivirusUploadHandler(FileUploadHandler):
    """Vérifier fichiers uploadés"""
    
    def receive_data_chunk(self, raw_data, start):
        # Sauvegarder le chunk
        return raw_data
    
    def file_complete(self, file_size):
        # Scanner le fichier complet
        file_path = self.temp_file_location
        result = AntivirusScanner.scan_file(file_path)
        
        if not result['clean']:
            os.remove(file_path)
            raise ValueError(f"Malware detected: {result.get('threat')}")
```

---

## **RÉSUMÉ PLAN D'ACTION**

| Phase | Tâches | Impact | Délai |
|-------|--------|--------|-------|
| **1 (CRITIQUE)** | E2E Frontend + Mobile + Load Tests + Flutter Widgets + Monitoring | +15% | 3-4 sem |
| **2 (HAUTE)** | Factures PDF + Charge Backend | +3% | 1-2 sem |
| **3 (MOYENNE)** | HL7/FHIR + WCAG Audit | +3% | 2-3 sem |
| **4 (BASSE)** | ELK Stack + Antivirus | +2% | 1-2 sem |
| **TOTAL** | → **100%** | **+23%** | **~8 semaines** |

---

## **CHECKLIST SUIVI**

### Phase 1
- [ ] Tests E2E Playwright configurés (5%)
- [ ] Tests E2E Flutter intégrés (5%)
- [ ] Tests charge Locust validés (3%)
- [ ] Widgets Flutter finalisés (5%)
- [ ] Prometheus/Grafana déployés (5%)

### Phase 2
- [ ] Factures PDF signées générées (2%)
- [ ] Tests charge backend en CI/CD (1%)

### Phase 3
- [ ] Convertisseur FHIR implémenté (2%)
- [ ] Audit WCAG complété (1%)

### Phase 4
- [ ] ELK Stack opérationnel (1%)
- [ ] Scanner antivirus intégré (1%)

---

**Estimated timeline for 100% compliance: 8 weeks (starting Phase 1)**