import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

class LocationProvider extends ChangeNotifier {
  Position? _position;
  bool _isLoading = false;
  String? _error;

  Position? get position => _position;
  double? get lat => _position?.latitude;
  double? get lng => _position?.longitude;
  bool get hasLocation => _position != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Requests permission (if needed) and obtains the current position.
  /// Returns true on success, false on denial or error.
  Future<bool> requestLocation() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        _error = 'Serviço de localização desativado. Ative-o nas configurações do dispositivo.';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        _error = permission == LocationPermission.deniedForever
            ? 'Permissão negada permanentemente. Ative a localização nas configurações do app.'
            : 'Permissão de localização negada.';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      _position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.medium,
          timeLimit: Duration(seconds: 10),
        ),
      );
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (_) {
      _error = 'Não foi possível obter sua localização. Tente novamente.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void clearLocation() {
    _position = null;
    _error = null;
    notifyListeners();
  }
}
