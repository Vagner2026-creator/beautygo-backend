import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/professional_model.dart';
import '../features/professional/screens/professional_profile_screen.dart';

class ProfessionalCard extends StatelessWidget {
  final ProfessionalModel professional;

  const ProfessionalCard({super.key, required this.professional});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ProfessionalProfileScreen(professional: professional)),
      ),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 12, offset: const Offset(0, 4))],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header image / avatar
            Container(
              height: 120,
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                gradient: LinearGradient(
                  colors: [AppTheme.primary.withOpacity(0.8), AppTheme.secondary.withOpacity(0.8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Stack(
                children: [
                  if (professional.profileImageUrl != null)
                    ClipRRect(
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                      child: Image.network(professional.profileImageUrl!, fit: BoxFit.cover, width: double.infinity, height: 120,
                        errorBuilder: (_, __, ___) => const SizedBox(),
                      ),
                    ),
                  Positioned(
                    bottom: 12,
                    left: 12,
                    child: CircleAvatar(
                      radius: 28,
                      backgroundColor: Colors.white,
                      child: Text(
                        professional.businessName.substring(0, 1).toUpperCase(),
                        style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 22),
                      ),
                    ),
                  ),
                  if (professional.isVerified)
                    const Positioned(
                      top: 10,
                      right: 10,
                      child: Icon(Icons.verified, color: Colors.white, size: 20),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(professional.businessName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15), maxLines: 1, overflow: TextOverflow.ellipsis),
                      ),
                      const Icon(Icons.star, color: Colors.amber, size: 16),
                      const SizedBox(width: 2),
                      Text(professional.rating.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      Text(' (${professional.ratingCount})', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                    ],
                  ),
                  if (professional.specialty != null) ...[
                    const SizedBox(height: 4),
                    Text(professional.specialty!, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      if (professional.neighborhood != null) ...[
                        const Icon(Icons.location_on_outlined, size: 14, color: AppTheme.textSecondary),
                        const SizedBox(width: 2),
                        Expanded(child: Text(professional.neighborhood!, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary), maxLines: 1, overflow: TextOverflow.ellipsis)),
                      ],
                      if (professional.distanceKm != null) ...[
                        const SizedBox(width: 8),
                        Text('${professional.distanceKm!.toStringAsFixed(1)} km', style: const TextStyle(fontSize: 12, color: AppTheme.primary, fontWeight: FontWeight.w500)),
                      ],
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      if (professional.homeService)
                        _Tag(label: 'Domicílio', color: AppTheme.secondary.withOpacity(0.12), textColor: AppTheme.secondary),
                      if (professional.homeService && professional.salonService) const SizedBox(width: 6),
                      if (professional.salonService)
                        _Tag(label: 'Salão', color: AppTheme.primary.withOpacity(0.1), textColor: AppTheme.primary),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  final String label;
  final Color color;
  final Color textColor;

  const _Tag({required this.label, required this.color, required this.textColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
      child: Text(label, style: TextStyle(fontSize: 11, color: textColor, fontWeight: FontWeight.w500)),
    );
  }
}
