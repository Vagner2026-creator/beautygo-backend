import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/professional_model.dart';
import '../../../models/service_model.dart';
import '../../../providers/professional_provider.dart';
import '../../../providers/auth_provider.dart';
import '../../appointments/screens/booking_screen.dart';

class ProfessionalProfileScreen extends StatefulWidget {
  final ProfessionalModel professional;

  const ProfessionalProfileScreen({super.key, required this.professional});

  @override
  State<ProfessionalProfileScreen> createState() => _ProfessionalProfileScreenState();
}

class _ProfessionalProfileScreenState extends State<ProfessionalProfileScreen> {
  List<ServiceModel> _services = [];
  bool _loadingServices = true;

  @override
  void initState() {
    super.initState();
    _loadServices();
  }

  Future<void> _loadServices() async {
    final services = await context.read<ProfessionalProvider>().getServices(widget.professional.id);
    if (mounted) {
      setState(() {
        _services = services;
        _loadingServices = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final pro = widget.professional;
    final user = context.read<AuthProvider>().user;
    final isClient = user?.isClient ?? false;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 220,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppTheme.primary, AppTheme.secondary],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(height: 40),
                      CircleAvatar(
                        radius: 48,
                        backgroundColor: Colors.white,
                        child: Text(
                          pro.businessName.substring(0, 1).toUpperCase(),
                          style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 36),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(pro.businessName, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                          if (pro.isVerified) ...[
                            const SizedBox(width: 6),
                            const Icon(Icons.verified, color: Colors.white, size: 18),
                          ],
                        ],
                      ),
                      if (pro.specialty != null)
                        Text(pro.specialty!, style: const TextStyle(color: Colors.white70, fontSize: 14)),
                    ],
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Stats row
                  Row(
                    children: [
                      _Stat(value: pro.rating.toStringAsFixed(1), label: 'Avaliação', icon: Icons.star, color: Colors.amber),
                      _Stat(value: '${pro.ratingCount}', label: 'Avaliações', icon: Icons.reviews_outlined, color: AppTheme.primary),
                      _Stat(value: '${pro.experienceYears}', label: 'Anos exp.', icon: Icons.workspace_premium_outlined, color: AppTheme.secondary),
                    ],
                  ),
                  const SizedBox(height: 20),
                  // Service type chips
                  Wrap(
                    spacing: 8,
                    children: [
                      if (pro.salonService)
                        Chip(
                          avatar: const Icon(Icons.store_outlined, size: 16),
                          label: const Text('Atende no salão'),
                          backgroundColor: AppTheme.primary.withOpacity(0.08),
                          labelStyle: const TextStyle(color: AppTheme.primary, fontSize: 12),
                        ),
                      if (pro.homeService)
                        Chip(
                          avatar: const Icon(Icons.home_outlined, size: 16),
                          label: const Text('Atende a domicílio'),
                          backgroundColor: AppTheme.secondary.withOpacity(0.08),
                          labelStyle: const TextStyle(color: AppTheme.secondary, fontSize: 12),
                        ),
                    ],
                  ),
                  // Location
                  if (pro.address != null || pro.neighborhood != null) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined, color: AppTheme.textSecondary, size: 18),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            [pro.neighborhood, pro.address].where((e) => e != null).join(' — '),
                            style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ],
                  // Description
                  if (pro.description != null) ...[
                    const SizedBox(height: 20),
                    Text('Sobre', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text(pro.description!, style: const TextStyle(color: AppTheme.textSecondary, height: 1.5)),
                  ],
                  // Services
                  const SizedBox(height: 24),
                  Text('Serviços', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  if (_loadingServices)
                    const Center(child: CircularProgressIndicator())
                  else if (_services.isEmpty)
                    const Text('Nenhum serviço cadastrado', style: TextStyle(color: AppTheme.textSecondary))
                  else
                    ..._services.map((s) => _ServiceTile(
                          service: s,
                          onBook: isClient ? () => _bookService(s) : null,
                        )),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _bookService(ServiceModel service) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => BookingScreen(professional: widget.professional, service: service),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;
  final Color color;

  const _Stat({required this.value, required this.label, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 16)),
            Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _ServiceTile extends StatelessWidget {
  final ServiceModel service;
  final VoidCallback? onBook;

  const _ServiceTile({required this.service, this.onBook});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.divider),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.spa_outlined, color: AppTheme.primary, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(service.name, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                const SizedBox(height: 2),
                Text('${service.formattedDuration} · ${service.formattedPrice}', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
              ],
            ),
          ),
          if (onBook != null)
            TextButton(
              onPressed: onBook,
              style: TextButton.styleFrom(foregroundColor: AppTheme.primary),
              child: const Text('Agendar'),
            ),
        ],
      ),
    );
  }
}
