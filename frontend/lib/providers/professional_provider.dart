import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../core/api/api_client.dart';
import '../models/professional_model.dart';
import '../models/service_model.dart';

class ProfessionalProvider extends ChangeNotifier {
  final _api = ApiClient();
  List<ProfessionalModel> _professionals = [];
  bool _isLoading = false;
  String? _error;

  List<ProfessionalModel> get professionals => _professionals;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> search({
    String? keyword,
    int? categoryId,
    double? lat,
    double? lng,
    double? maxDistanceKm,
    bool? homeService,
    bool? salonService,
    int page = 1,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final params = <String, dynamic>{
        'page': page,
        'size': 20,
        if (keyword != null && keyword.isNotEmpty) 'keyword': keyword,
        if (categoryId != null) 'category_id': categoryId,
        if (lat != null) 'lat': lat,
        if (lng != null) 'lng': lng,
        if (maxDistanceKm != null) 'max_distance_km': maxDistanceKm,
        if (homeService != null) 'home_service': homeService,
        if (salonService != null) 'salon_service': salonService,
      };
      final response = await _api.get('/search/', params: params);
      final items = response.data['items'] as List;
      _professionals = items.map((j) => ProfessionalModel.fromJson(j)).toList();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = 'Erro ao buscar profissionais';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<ProfessionalModel?> getById(int id) async {
    try {
      final response = await _api.get('/professionals/$id');
      return ProfessionalModel.fromJson(response.data);
    } catch (_) {
      return null;
    }
  }

  Future<List<ServiceModel>> getServices(int professionalId) async {
    try {
      final response = await _api.get('/services/professional/$professionalId');
      final items = response.data as List;
      return items.map((j) => ServiceModel.fromJson(j)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<String?> uploadProfileImage() async {
    try {
      final picker = ImagePicker();
      final file = await picker.pickImage(source: ImageSource.gallery, imageQuality: 80);
      if (file == null) return null;

      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(file.path, filename: file.name),
      });
      final uploadResp = await _api.post('/media/upload', data: formData);
      final fileUrl = uploadResp.data['file_url'] as String;

      await _api.patch('/professionals/me', data: {'profile_image_url': fileUrl});
      return fileUrl;
    } catch (_) {
      return null;
    }
  }

  Future<List<String>> getAvailableSlots({
    required int professionalId,
    required String date,
    required int serviceId,
  }) async {
    try {
      final response = await _api.get(
        '/availability/professional/$professionalId/slots',
        params: {'date': date, 'service_id': serviceId},
      );
      return List<String>.from(response.data);
    } catch (_) {
      return [];
    }
  }
}
