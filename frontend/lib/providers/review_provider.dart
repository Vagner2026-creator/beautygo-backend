import 'package:flutter/material.dart';
import '../core/api/api_client.dart';
import '../models/review_model.dart';

class ReviewProvider extends ChangeNotifier {
  final _api = ApiClient();

  final Map<int, List<ReviewModel>> _cache = {};
  bool _isLoading = false;
  bool _isSubmitting = false;
  String? _error;
  int _total = 0;

  bool get isLoading => _isLoading;
  bool get isSubmitting => _isSubmitting;
  String? get error => _error;
  int get total => _total;

  List<ReviewModel> reviewsFor(int professionalId) =>
      _cache[professionalId] ?? [];

  Future<void> load(int professionalId, {bool refresh = false}) async {
    if (!refresh && _cache.containsKey(professionalId)) return;
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final response = await _api.get(
        '/reviews/professionals/$professionalId/reviews',
        params: {'page': 1, 'size': 20},
      );
      final items = (response.data['items'] as List?) ?? [];
      _total = response.data['total'] ?? 0;
      _cache[professionalId] = items.map((j) => ReviewModel.fromJson(j)).toList();
    } catch (_) {
      _error = 'Erro ao carregar avaliações';
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> create({
    required int professionalId,
    required int rating,
    String? comment,
  }) async {
    _isSubmitting = true;
    _error = null;
    notifyListeners();
    try {
      await _api.post('/reviews/', data: {
        'professional_id': professionalId,
        'rating': rating,
        if (comment != null && comment.isNotEmpty) 'comment': comment,
      });
      _cache.remove(professionalId);
      _isSubmitting = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      _isSubmitting = false;
      notifyListeners();
      return false;
    }
  }

  String _parseError(dynamic e) {
    try {
      final data = (e as dynamic).response?.data;
      if (data is Map && data['detail'] is String) return data['detail'];
      return 'Erro ao enviar avaliação.';
    } catch (_) {
      return 'Sem conexão com o servidor.';
    }
  }
}
