import 'dart:async';

import 'package:flutter/material.dart';

import '../data/auth/auth_api_client.dart';
import '../data/auth/auth_config.dart';
import '../data/auth/auth_session.dart';
import '../data/auth/secure_session_store.dart';
import '../data/local/local_database.dart';
import '../data/local/secure_database_key_store.dart';
import '../data/repositories/fitness_models.dart';
import '../data/repositories/local_fitness_repository.dart';

class PersoneliseApp extends StatelessWidget {
  const PersoneliseApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF247C73);
    return MaterialApp(
      title: 'Personelise Gym',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.light),
        scaffoldBackgroundColor: const Color(0xFFF5F7F6),
        appBarTheme: const AppBarTheme(
          centerTitle: false,
          backgroundColor: Color(0xFFF5F7F6),
          surfaceTintColor: Colors.transparent,
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          color: Colors.white,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
            side: const BorderSide(color: Color(0xFFE5EBE8)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFE0E8E4)),
          ),
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark),
      ),
      themeMode: ThemeMode.system,
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final _sessionStore = SecureSessionStore(store: FlutterSecureKeyValueStore());
  final _database = LocalDatabase();
  late final LocalFitnessRepository _profiles = LocalFitnessRepository(_database);
  AuthApiClient? _api;
  AuthSession? _session;
  bool _loading = true;
  bool _busy = false;
  bool _showSignup = false;
  bool _needsProfile = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final uri = AuthConfig.baseUri;
    if (uri != null) _api = AuthApiClient(baseUri: uri);
    unawaited(_restoreSession());
  }

  Future<void> _restoreSession() async {
    try {
      final session = await _sessionStore.read();
      if (session != null) {
        final profile = await _profiles.getProfile(session.userId);
        if (!mounted) return;
        setState(() {
          _session = session;
          _needsProfile = profile == null;
          _loading = false;
        });
      } else if (mounted) {
        setState(() => _loading = false);
      }
    } catch (_) {
      if (mounted) setState(() {
        _loading = false;
        _error = 'Secure storage could not be opened. Your saved data was not reset.';
      });
    }
  }

  Future<void> _authenticate({
    required String email,
    required String password,
    required String displayName,
  }) async {
    final api = _api;
    if (api == null) return;
    setState(() { _busy = true; _error = null; });
    try {
      final session = _showSignup
          ? await api.signUp(email: email, password: password, displayName: displayName)
          : await api.signIn(email: email, password: password);
      await _sessionStore.save(session);
      final profile = await _profiles.getProfile(session.userId);
      if (!mounted) return;
      setState(() {
        _session = session;
        _needsProfile = profile == null;
        _busy = false;
      });
    } on AuthApiException catch (error) {
      if (mounted) setState(() { _busy = false; _error = error.message; });
    } catch (_) {
      if (mounted) setState(() {
        _busy = false;
        _error = 'Could not connect. Check your internet connection and try again.';
      });
    }
  }

  Future<void> _saveProfile({
    required String displayName,
    required String height,
    required String weight,
    required String goal,
  }) async {
    final session = _session;
    if (session == null) return;
    final heightValue = double.tryParse(height);
    final weightValue = double.tryParse(weight);
    final goalValue = goal.trim().isEmpty ? null : double.tryParse(goal);
    if (displayName.trim().length < 2 ||
        heightValue == null || heightValue < 80 || heightValue > 250 ||
        weightValue == null || weightValue < 20 || weightValue > 400 ||
        (goal.trim().isNotEmpty && (goalValue == null || goalValue < 20 || goalValue > 400))) {
      setState(() => _error = 'Enter a name, height (80–250 cm), and valid weight (20–400 kg).');
      return;
    }
    setState(() { _busy = true; _error = null; });
    try {
      final now = DateTime.now().toUtc();
      final old = await _profiles.getProfile(session.userId);
      await _profiles.saveProfile(FitnessProfile(
        userId: session.userId,
        displayName: displayName.trim(),
        heightCm: heightValue,
        currentWeightKg: weightValue,
        goalWeightKg: goalValue,
        createdAt: old?.createdAt ?? now,
        updatedAt: now,
      ));
      if (mounted) setState(() { _needsProfile = false; _busy = false; });
    } catch (_) {
      if (mounted) setState(() {
        _busy = false;
        _error = 'Profile could not be saved securely on this device.';
      });
    }
  }

  Future<void> _logout() async {
    final session = _session;
    if (session == null) return;
    setState(() { _busy = true; _error = null; });
    try {
      final api = _api;
      if (api != null) await api.logout(session);
      await _sessionStore.clear();
      if (mounted) setState(() {
        _session = null;
        _needsProfile = false;
        _busy = false;
        _showSignup = false;
      });
    } catch (_) {
      if (mounted) setState(() {
        _busy = false;
        _error = 'Server sign-out failed. Keep your connection and retry so this token can be revoked.';
      });
    }
  }

  @override
  void dispose() {
    _api?.close();
    unawaited(_database.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final session = _session;
    if (session != null && !_needsProfile) {
      return AppShell(
        email: session.email,
        busy: _busy,
        onLogout: _logout,
      );
    }
    if (session != null) {
      return ProfileSetupScreen(
        email: session.email,
        busy: _busy,
        error: _error,
        onSave: _saveProfile,
      );
    }
    return AuthScreen(
      apiConfigured: _api != null,
      isSignup: _showSignup,
      busy: _busy,
      error: _error,
      onModeChanged: (value) => setState(() { _showSignup = value; _error = null; }),
      onSubmit: _authenticate,
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({
    required this.apiConfigured,
    required this.isSignup,
    required this.busy,
    required this.error,
    required this.onModeChanged,
    required this.onSubmit,
    super.key,
  });

  final bool apiConfigured;
  final bool isSignup;
  final bool busy;
  final String? error;
  final ValueChanged<bool> onModeChanged;
  final Future<void> Function({
    required String email,
    required String password,
    required String displayName,
  }) onSubmit;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.fitness_center_rounded, size: 46, color: Color(0xFF247C73)),
                  const SizedBox(height: 18),
                  Text('Personelise Gym', textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
                  const SizedBox(height: 8),
                  Text(widget.isSignup ? 'Create your private fitness account' : 'Your personal training space',
                    textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
                  const SizedBox(height: 28),
                  if (!widget.apiConfigured)
                    const Card(child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Text('Account service is not configured yet. Set AUTH_API_BASE_URL to your deployed Apps Script Web App URL when the backend is ready. No local demo account is created.'),
                    ))
                  else ...[
                    if (widget.isSignup) ...[
                      TextField(controller: _name, textCapitalization: TextCapitalization.words,
                        decoration: const InputDecoration(labelText: 'Your name')),
                      const SizedBox(height: 12),
                    ],
                    TextField(controller: _email, keyboardType: TextInputType.emailAddress,
                      autocorrect: false, decoration: const InputDecoration(labelText: 'Email address')),
                    const SizedBox(height: 12),
                    TextField(controller: _password, obscureText: true,
                      decoration: InputDecoration(labelText: 'Password',
                        helperText: widget.isSignup ? 'Use at least 12 characters' : null)),
                    if (widget.error != null) ...[
                      const SizedBox(height: 12),
                      Text(widget.error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                    ],
                    const SizedBox(height: 18),
                    FilledButton(
                      onPressed: widget.busy ? null : () {
                        final email = _email.text.trim();
                        final password = _password.text;
                        if (!email.contains('@') || password.isEmpty ||
                            (widget.isSignup && (_name.text.trim().length < 2 || password.length < 12))) {
                          return;
                        }
                        widget.onSubmit(email: email, password: password, displayName: _name.text.trim());
                      },
                      child: widget.busy
                          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                          : Text(widget.isSignup ? 'Create account' : 'Sign in'),
                    ),
                    TextButton(
                      onPressed: widget.busy ? null : () => widget.onModeChanged(!widget.isSignup),
                      child: Text(widget.isSignup ? 'Already have an account? Sign in' : 'New here? Create an account'),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class ProfileSetupScreen extends StatefulWidget {
  const ProfileSetupScreen({
    required this.email,
    required this.busy,
    required this.error,
    required this.onSave,
    super.key,
  });

  final String email;
  final bool busy;
  final String? error;
  final Future<void> Function({
    required String displayName,
    required String height,
    required String weight,
    required String goal,
  }) onSave;

  @override
  State<ProfileSetupScreen> createState() => _ProfileSetupScreenState();
}

class _ProfileSetupScreenState extends State<ProfileSetupScreen> {
  final _name = TextEditingController();
  final _height = TextEditingController();
  final _weight = TextEditingController();
  final _goal = TextEditingController();

  @override
  void dispose() {
    _name.dispose(); _height.dispose(); _weight.dispose(); _goal.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Set up your profile')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(widget.email, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 18),
          TextField(controller: _name, textCapitalization: TextCapitalization.words,
            decoration: const InputDecoration(labelText: 'Display name')),
          const SizedBox(height: 12),
          TextField(controller: _height, keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Height (cm)')),
          const SizedBox(height: 12),
          TextField(controller: _weight, keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Current weight (kg)')),
          const SizedBox(height: 12),
          TextField(controller: _goal, keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Goal weight (kg, optional)')),
          if (widget.error != null) ...[
            const SizedBox(height: 12),
            Text(widget.error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
          const SizedBox(height: 20),
          FilledButton(
            onPressed: widget.busy ? null : () => widget.onSave(
              displayName: _name.text, height: _height.text,
              weight: _weight.text, goal: _goal.text,
            ),
            child: widget.busy
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Save profile'),
          ),
        ],
      ),
    );
  }
}

class AppShell extends StatefulWidget {
  const AppShell({required this.email, required this.busy, required this.onLogout, super.key});
  final String email;
  final bool busy;
  final VoidCallback onLogout;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;
  static const _destinations = <NavigationDestination>[
    NavigationDestination(icon: Icon(Icons.space_dashboard_outlined), selectedIcon: Icon(Icons.space_dashboard), label: 'Home'),
    NavigationDestination(icon: Icon(Icons.fitness_center_outlined), selectedIcon: Icon(Icons.fitness_center), label: 'Workout'),
    NavigationDestination(icon: Icon(Icons.insights_outlined), selectedIcon: Icon(Icons.insights), label: 'Progress'),
    NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
  ];
  static const _titles = ['Your fitness', 'Workout', 'Progress', 'Profile'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_selectedIndex], style: const TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: widget.busy ? null : widget.onLogout,
            icon: const Icon(Icons.logout_rounded),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: _PlaceholderPage(
          title: _titles[_selectedIndex],
          description: _selectedIndex == 0
              ? 'Signed in as ${widget.email}. Your personal training space is ready for the next development phase.'
              : 'This section will be added in its development phase.',
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        destinations: _destinations,
        onDestinationSelected: (index) => setState(() => _selectedIndex = index),
      ),
    );
  }
}

class _PlaceholderPage extends StatelessWidget {
  const _PlaceholderPage({required this.title, required this.description});
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.fitness_center_rounded, size: 48, color: Color(0xFF247C73)),
              const SizedBox(height: 18),
              Text(title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              Text(description, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
      ),
    );
  }
}
