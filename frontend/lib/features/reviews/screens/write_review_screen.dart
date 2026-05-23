import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/professional_model.dart';
import '../../../providers/review_provider.dart';

class WriteReviewScreen extends StatefulWidget {
  final ProfessionalModel professional;

  const WriteReviewScreen({super.key, required this.professional});

  @override
  State<WriteReviewScreen> createState() => _WriteReviewScreenState();
}

class _WriteReviewScreenState extends State<WriteReviewScreen> {
  int _rating = 5;
  final _commentCtrl = TextEditingController();

  static const _labels = ['Muito ruim', 'Ruim', 'Regular', 'Bom', 'Excelente'];

  @override
  void dispose() {
    _commentCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final provider = context.read<ReviewProvider>();
    final ok = await provider.create(
      professionalId: widget.professional.id,
      rating: _rating,
      comment: _commentCtrl.text.trim().isEmpty ? null : _commentCtrl.text.trim(),
    );
    if (!mounted) return;
    if (ok) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Avaliação enviada! Obrigado pelo feedback.'),
          backgroundColor: AppTheme.success,
        ),
      );
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(provider.error ?? 'Erro ao enviar avaliação'),
          backgroundColor: AppTheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isSubmitting = context.watch<ReviewProvider>().isSubmitting;
    final pro = widget.professional;

    return Scaffold(
      appBar: AppBar(title: const Text('Avaliar profissional')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Professional info header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  backgroundColor: AppTheme.primary.withOpacity(0.15),
                  child: Text(
                    pro.businessName.substring(0, 1).toUpperCase(),
                    style: const TextStyle(
                      color: AppTheme.primary,
                      fontWeight: FontWeight.bold,
                      fontSize: 22,
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        pro.businessName,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      if (pro.specialty != null)
                        Text(
                          pro.specialty!,
                          style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          // Rating
          const Text(
            'Sua nota',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Center(
            child: RatingBar.builder(
              initialRating: _rating.toDouble(),
              minRating: 1,
              itemCount: 5,
              itemSize: 48,
              itemPadding: const EdgeInsets.symmetric(horizontal: 4),
              itemBuilder: (_, __) =>
                  const Icon(Icons.star_rounded, color: Colors.amber),
              onRatingUpdate: (r) => setState(() => _rating = r.toInt()),
            ),
          ),
          const SizedBox(height: 10),
          Center(
            child: Text(
              _labels[_rating - 1],
              style: const TextStyle(
                color: AppTheme.primary,
                fontWeight: FontWeight.w600,
                fontSize: 15,
              ),
            ),
          ),
          const SizedBox(height: 28),
          // Comment
          const Text(
            'Comentário (opcional)',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _commentCtrl,
            maxLines: 4,
            maxLength: 500,
            decoration: const InputDecoration(
              hintText: 'Conte sua experiência com este profissional...',
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: isSubmitting ? null : _submit,
            child: isSubmitting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Enviar avaliação'),
          ),
        ],
      ),
    );
  }
}
