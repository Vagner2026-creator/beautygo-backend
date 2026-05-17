class UserModel {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String role;
  final bool isActive;
  final bool isVerified;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    required this.role,
    required this.isActive,
    required this.isVerified,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'],
        email: json['email'],
        fullName: json['full_name'],
        phone: json['phone'],
        role: json['role'],
        isActive: json['is_active'] ?? true,
        isVerified: json['is_verified'] ?? false,
      );

  bool get isClient => role == 'client';
  bool get isProfessional => role == 'professional';
  bool get isAdmin => role == 'admin';
}
