import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/professional_model.dart';
import '../../../models/review_model.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/review_provider.dart';
import 'write_review_screen.dart';

class ReviewsScreen extends StatefulWidget {
  final ProfessionalModel professional;

  const ReviewsScreen({super.key, required this.professional});

  @override
  State<ReviewsScreen> createState() => _ReviewsScreenState();
}

class _ReviewsScreenState extends State<ReviewsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReviewProvider>().load(widget.professional.id, refresh: true);
    });
  }

  Future<void> _openWriteReview() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => WriteReviewScreen(professional: widget.professional),
      ),
    );
    if (result == true && mounted) {
      context.read<ReviewProvider>().load(widget.professional.id, refresh: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ReviewProvider>();
    final user = context.read<AuthProvider>().user;
    final reviews = provider.reviewsFor(widget.professional.id);
    final pro = widget.professional;

    return Scaffold(
      appBar: AppBar(
        title: Text('Avaliações — ${pro.businessName}'),
        actions: [
          if (user?.isClient == true)
            TextButton.icon(
              onPressed: _openWriteReview,
              icon: const Icon(Icons.rate_review_outlined, size: 18),
              label: const Text('Avaliar'),
            ),
        ],
      ),
      body: Column(
        children: [
          // Summary header
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
            child: Row(
              children: [
                Column(
                  children: [
                    Text(
                      pro.rating.toStringAsFixed(1),
                      style: const TextStyle(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primary,
                      ),
                    ),
                    RatingBarIndicator(
                      rating: pro.rating,
                      itemCount: 5,
                      itemSize: 18,
                      itemBuilder: (_, __) =>
                          const Icon(Icons.star_rounded, color: Colors.amber),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${pro.ratingCount} avaliações',
                      style: const TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 24),
                Expanded(child: _RatingBars(reviews: reviews)),
              ],
            ),
          ),
          const Divider(height: 1),
          // Reviews list
          Expanded(
            child: provider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : reviews.isEmpty
                    ? _EmptyState(onReview: user?.isClient == true ? _openWriteReview : null)
                    : RefreshIndicator(
                        onRefresh: () => context
                            .read<ReviewProvider>()
                            .load(widget.professional.id, refresh: true),
                        child: ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: reviews.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (_, i) => _ReviewCard(review: reviews[i]),
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: user?.isClient == true
          ? FloatingActionButton.extended(
              onPressed: _openWriteReview,
              icon: const Icon(Icons.rate_review_outlined),
              label: const Text('Avaliar'),
              backgroundColor: AppTheme.primary,
            )
          : null,
    );
  }
}

class _RatingBars extends StatelessWidget {
  final List<ReviewModel> reviews;
  const _RatingBars({required this.reviews});

  @override
  Widget build(BuildContext context) {
    if (reviews.isEmpty) return const SizedBox();
    final counts = List.filled(5, 0);
    for (final r in reviews) {
      if (r.rating >= 1 && r.rating <= 5) counts[r.rating - 1]++;
    }
    return Column(
      children: List.generate(5, (i) {
        final star = 5 - i;
        final count = counts[star - 1];
        final pct = reviews.isEmpty ? 0.0 : count / reviews.length;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 2),
          child: Row(
            children: [
              Text('$star', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              const SizedBox(width: 4),
              const Icon(Icons.star, size: 12, color: Colors.amber),
              const SizedBox(width: 6),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: pct,
                    backgroundColor: AppTheme.divider,
                    valueColor: const AlwaysStoppedAnimation(Colors.amber),
                    minHeight: 6,
                  ),
                ),
              ),
              const SizedBox(width: 6),
              SizedBox(
                width: 20,
                child: Text(
                  '$count',
                  style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ),
        );
      }),
    );
  }
}

class _ReviewCard extends StatelessWidget {
  final ReviewModel review;
  const _ReviewCard({required this.review});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: AppTheme.primary.withOpacity(0.15),
                child: const Icon(Icons.person, size: 18, color: AppTheme.primary),
              ),
              const SizedBox(width: 10),
              Expanded(
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
                    Text(
                      _formatDate(review.createdAt),
                      style: const TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (review.comment != null && review.comment!.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              review.comment!,
              style: const TextStyle(fontSize: 14, height: 1.5, color: AppTheme.textPrimary),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}';
  }
}

class _EmptyState extends StatelessWidget {
  final VoidCallback? onReview;
  const _EmptyState({this.onReview});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.rate_review_outlined, size: 64, color: AppTheme.textSecondary),
          const SizedBox(height: 12),
          const Text(
            'Nenhuma avaliação ainda',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 6),
          const Text(
            'Seja o primeiro a avaliar este profissional!',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
          if (onReview != null) ...[
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: onReview,
              icon: const Icon(Icons.star_outline),
              label: const Text('Deixar avaliação'),
            ),
          ],
        ],
      ),
    );
  }
}
