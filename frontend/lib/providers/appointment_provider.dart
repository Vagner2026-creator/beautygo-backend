import 'package:flutter/material.dart';
import '../core/api/api_client.dart';
import '../models/appointment_model.dart';

class AppointmentProvider extends ChangeNotifier {
  final _api = ApiClient();
  List<AppointmentModel> _appointments = [];
  bool _isLoading = false;
  String? _error;

  List<AppointmentModel> get appointments => _appointments;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadClientAppointments() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _api.get('/appointments/client');
      final items = response.data['items'] as List;
      _appointments = items.map((j) => AppointmentModel.fromJson(j)).toList();
    } catch (_) {
      _error = 'Erro ao carregar agendamentos';
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadProfessionalAppointments() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _api.get('/appointments/professional');
      final items = response.data['items'] as List;
      _appointments = items.map((j) => AppointmentModel.fromJson(j)).toList();
    } catch (_) {
      _error = 'Erro ao carregar agendamentos';
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<AppointmentModel?> book({
    required int professionalId,
    required int serviceId,
    required String date,
    required String startTime,
    required String clientName,
    required String clientPhone,
    String? notes,
  }) async {
    try {
      final response = await _api.post('/appointments/', data: {
        'professional_id': professionalId,
        'service_id': serviceId,
        'appointment_date': date,
        'start_time': startTime,
        'client_name': clientName,
        'client_phone': clientPhone,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      });
      return AppointmentModel.fromJson(response.data);
    } catch (e) {
      _error = _parseError(e);
      notifyListeners();
      return null;
    }
  }

  Future<bool> confirm(int appointmentId) async {
    try {
      final response = await _api.patch('/appointments/$appointmentId/confirm');
      final updated = AppointmentModel.fromJson(response.data);
      _appointments = _appointments.map((a) => a.id == appointmentId ? updated : a).toList();
      notifyListeners();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> cancel(int appointmentId) async {
    try {
      final response = await _api.patch('/appointments/$appointmentId/cancel');
      final updated = AppointmentModel.fromJson(response.data);
      _appointments = _appointments.map((a) => a.id == appointmentId ? updated : a).toList();
      notifyListeners();
      return true;
    } catch (_) {
      return false;
    }
  }

  String _parseError(dynamic e) {
    try {
      final data = (e as dynamic).response?.data;
      if (data is Map && data['detail'] is String) return data['detail'];
      return 'Erro ao realizar agendamento';
    } catch (_) {
      return 'Sem conexão com o servidor';
    }
  }
}
