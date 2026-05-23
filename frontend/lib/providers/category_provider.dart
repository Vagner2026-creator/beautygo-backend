import 'package:flutter/material.dart';
import '../core/api/api_client.dart';
import '../models/category_model.dart';

class CategoryProvider extends ChangeNotifier {
  final _api = ApiClient();
  List<CategoryModel> _categories = [];
  bool _isLoading = false;
  bool _loaded = false;

  List<CategoryModel> get categories => _categories;
  bool get isLoading => _isLoading;

  Future<void> load() async {
    if (_loaded) return;
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _api.get('/categories/');
      final items = response.data as List;
      _categories = items
          .map((j) => CategoryModel.fromJson(j))
          .where((c) => c.isActive)
          .toList();
      _loaded = true;
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }
}
