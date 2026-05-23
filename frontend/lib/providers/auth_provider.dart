import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/api/api_client.dart';
import '../models/user_model.dart';

class AuthProvider extends ChangeNotifier {
  UserModel? _user;
  bool _isLoading = false;
  String? _error;

  UserModel? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _user != null;

  final _api = ApiClient();

  Future<void> checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token == null) return;
    try {
      final response = await _api.get('/auth/me');
      _user = UserModel.fromJson(response.data);
      notifyListeners();
    } catch (_) {
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final response = await _api.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', response.data['access_token']);
      await prefs.setString('refresh_token', response.data['refresh_token']);
      final meResponse = await _api.get('/auth/me');
      _user = UserModel.fromJson(meResponse.data);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String fullName,
    required String role,
    String? phone,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      await _api.post('/auth/register', data: {
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': role,
        if (phone != null) 'phone': phone,
      });
      return await login(email, password);
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateProfile({String? fullName, String? phone}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final body = <String, dynamic>{};
      if (fullName != null) body['full_name'] = fullName;
      body['phone'] = phone;
      final response = await _api.patch('/users/me', data: body);
      _user = UserModel.fromJson(response.data);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> changePassword({required String current, required String newPass}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      await _api.post('/auth/change-password', data: {
        'current_password': current,
        'new_password': newPass,
      });
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    _user = null;
    notifyListeners();
  }

  String _parseError(dynamic e) {
    try {
      final data = (e as dynamic).response?.data;
      if (data is Map && data['detail'] is String) return data['detail'];
      return 'Ocorreu um erro. Tente novamente.';
    } catch (_) {
      return 'Sem conexão com o servidor.';
    }
  }
}
