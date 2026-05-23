import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/professional_model.dart';
import '../../../models/review_model.dart';
import '../../../models/service_model.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/professional_provider.dart';
import '../../../providers/review_provider.dart';
import '../../appointments/screens/booking_screen.dart';
import '../../reviews/screens/reviews_screen.dart';
import '../../reviews/screens/write_review_screen.dart';

class ProfessionalProfileScreen extends StatefulWidget {
  final ProfessionalModel professional;

  const ProfessionalProfileScreen({super.key, required this.professional});

  @override
  State<ProfessionalProfileScreen> createState() =>
      _ProfessionalProfileScreenState();
}

class _ProfessionalProfileScreenState extends State<ProfessionalProfileScreen> {
  List<ServiceModel> _services = [];
  bool _loadingServices = true;
  String? _profileImageUrl;
  bool _uploadingPhoto = false;

  @override
  void initState() {
    super.initState();
    _profileImageUrl = widget.professional.profileImageUrl;
    _loadServices();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReviewProvider>().load(widget.professional.id);
    });
  }

  Future<void> _loadServices() async {
    final services = await context
        .read<ProfessionalProvider>()
        .getServices(widget.professional.id);
    if (mounted) {
      setState(() {
        _services = services;
        _loadingServices = false;
      });
    }
  }

  Future<void> _uploadPhoto() async {
    setState(() => _uploadingPhoto = true);
    final url =
        await context.read<ProfessionalProvider>().uploadProfileImage();
    if (mounted) {
      setState(() {
        if (url != null) _profileImageUrl = url;
        _uploadingPhoto = false;
      });
      if (url != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Foto atualizada com sucesso!'),
            backgroundColor: AppTheme.success,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final pro = widget.professional;
    final user = context.read<AuthProvider>().user;
    final isClient = user?.isClient ?? false;
    final isOwnProfile = user?.id == pro.userId && (user?.isProfessional ?? false);
    final reviews = context.watch<ReviewProvider>().reviewsFor(pro.id);

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 240,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Stack(
                fit: StackFit.expand,
                children: [
                  // Background gradient
                  Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [AppTheme.primary, AppTheme.secondary],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                  ),
                  // Background photo if available
                  if (_profileImageUrl != null)
                    CachedNetworkImage(
                      imageUrl: _profileImageUrl!,
                      fit: BoxFit.cover,
                      errorWidget: (_, __, ___) => const SizedBox(),
                      color: Colors.black.withOpacity(0.4),
                      colorBlendMode: BlendMode.darken,
                    ),
                  // Content
                  SafeArea(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 40),
                        Stack(
                          children: [
                            CircleAvatar(
                              radius: 48,
                              backgroundColor: Colors.white,
                              child: _profileImageUrl != null
                                  ? ClipOval(
                                      child: CachedNetworkImage(
                                        imageUrl: _profileImageUrl!,
                                        fit: BoxFit.cover,
                                        width: 96,
                                        height: 96,
                                        errorWidget: (_, __, ___) =>
                                            _InitialAvatar(pro.businessName),
                                        placeholder: (_, __) =>
                                            _InitialAvatar(pro.businessName),
                                      ),
                                    )
                                  : _InitialAvatar(pro.businessName),
                            ),
                            if (isOwnProfile)
                              Positioned(
                                right: 0,
                                bottom: 0,
                                child: GestureDetector(
                                  onTap: _uploadingPhoto ? null : _uploadPhoto,
                                  child: Container(
                                    width: 30,
                                    height: 30,
                                    decoration: const BoxDecoration(
                                      color: Colors.white,
                                      shape: BoxShape.circle,
                                    ),
                                    child: _uploadingPhoto
                                        ? const Padding(
                                            padding: EdgeInsets.all(6),
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                              color: AppTheme.primary,
                                            ),
                                          )
                                        : const Icon(
                                            Icons.camera_alt,
                                            size: 16,
                                            color: AppTheme.primary,
                                          ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              pro.businessName,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            if (pro.isVerified) ...[
                              const SizedBox(width: 6),
                              const Icon(Icons.verified, color: Colors.white, size: 18),
                            ],
                          ],
                        ),
                        if (pro.specialty != null)
                          Text(
                            pro.specialty!,
                            style: const TextStyle(color: Colors.white70, fontSize: 14),
                          ),
                      ],
                    ),
                  ),
                ],
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
                      _Stat(
                        value: pro.rating.toStringAsFixed(1),
                        label: 'Avaliação',
                        icon: Icons.star,
                        color: Colors.amber,
                      ),
                      _Stat(
                        value: '${pro.ratingCount}',
                        label: 'Avaliações',
                        icon: Icons.reviews_outlined,
                        color: AppTheme.primary,
                      ),
                      _Stat(
                        value: '${pro.experienceYears}',
                        label: 'Anos exp.',
                        icon: Icons.workspace_premium_outlined,
                        color: AppTheme.secondary,
                      ),
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
                          labelStyle:
                              const TextStyle(color: AppTheme.primary, fontSize: 12),
                        ),
                      if (pro.homeService)
                        Chip(
                          avatar: const Icon(Icons.home_outlined, size: 16),
                          label: const Text('Atende a domicílio'),
                          backgroundColor: AppTheme.secondary.withOpacity(0.08),
                          labelStyle:
                              const TextStyle(color: AppTheme.secondary, fontSize: 12),
                        ),
                    ],
                  ),
                  // Location
                  if (pro.address != null || pro.neighborhood != null) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined,
                            color: AppTheme.textSecondary, size: 18),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            [pro.neighborhood, pro.address]
                                .where((e) => e != null)
                                .join(' — '),
                            style: const TextStyle(
                                color: AppTheme.textSecondary, fontSize: 13),
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
                    Text(
                      pro.description!,
                      style:
                          const TextStyle(color: AppTheme.textSecondary, height: 1.5),
                    ),
                  ],
                  // Services
                  const SizedBox(height: 24),
                  Text('Serviços', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  if (_loadingServices)
                    const Center(child: CircularProgressIndicator())
                  else if (_services.isEmpty)
                    const Text(
                      'Nenhum serviço cadastrado',
                      style: TextStyle(color: AppTheme.textSecondary),
                    )
                  else
                    ..._services.map(
                      (s) => _ServiceTile(
                        service: s,
                        onBook: isClient ? () => _bookService(s) : null,
                      ),
                    ),
                  // Reviews section
                  const SizedBox(height: 28),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Avaliações',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      TextButton(
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) =>
                                ReviewsScreen(professional: pro),
                          ),
                        ),
                        child: const Text('Ver todas'),
                      ),
                    ],
                  ),
                  if (isClient)
                    OutlinedButton.icon(
                      onPressed: () async {
                        final result = await Navigator.push<bool>(
                          context,
                          MaterialPageRoute(
                            builder: (_) => WriteReviewScreen(professional: pro),
                          ),
                        );
                        if (result == true && mounted) {
                          context
                              .read<ReviewProvider>()
                              .load(pro.id, refresh: true);
                        }
                      },
                      icon: const Icon(Icons.rate_review_outlined, size: 18),
                      label: const Text('Deixar avaliação'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.primary,
                        side: const BorderSide(color: AppTheme.primary),
                        minimumSize: const Size(double.infinity, 44),
                      ),
                    ),
                  const SizedBox(height: 12),
                  if (reviews.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(
                        child: Text(
                          'Ainda não há avaliações',
                          style: TextStyle(color: AppTheme.textSecondary),
                        ),
                      ),
                    )
                  else
                    ...reviews.take(3).map((r) => _ReviewPreview(review: r)),
                  const SizedBox(height: 32),
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
        builder: (_) =>
            BookingScreen(professional: widget.professional, service: service),
      ),
    );
  }
}

class _InitialAvatar extends StatelessWidget {
  final String name;
  const _InitialAvatar(this.name);

  @override
  Widget build(BuildContext context) {
    return Text(
      name.substring(0, 1).toUpperCase(),
      style: const TextStyle(
        color: AppTheme.primary,
        fontWeight: FontWeight.bold,
        fontSize: 36,
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;
  final Color color;

  const _Stat({
    required this.value,
    required this.label,
    required this.icon,
    required this.color,
  });

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
            Text(
              value,
              style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 16),
            ),
            Text(
              label,
              style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            ),
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
            child:
                const Icon(Icons.spa_outlined, color: AppTheme.primary, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  service.name,
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                const SizedBox(height: 2),
                Text(
                  '${service.formattedDuration} · ${service.formattedPrice}',
                  style: const TextStyle(
                      color: AppTheme.textSecondary, fontSize: 13),
                ),
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

class _ReviewPreview extends StatelessWidget {
  final ReviewModel review;
  const _ReviewPreview({required this.review});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RatingBarIndicator(
            rating: review.rating.toDouble(),
            itemCount: 5,
            itemSize: 14,
            itemBuilder: (_, __) =>
                const Icon(Icons.star_rounded, color: Colors.amber),
          ),
          if (review.comment != null && review.comment!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              review.comment!,
              style: const TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
                height: 1.4,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ],
      ),
    );
  }
}
