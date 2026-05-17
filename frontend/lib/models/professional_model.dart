class ProfessionalModel {
  final int id;
  final int userId;
  final String businessName;
  final String? description;
  final String? specialty;
  final int experienceYears;
  final double rating;
  final int ratingCount;
  final bool isAvailable;
  final String? address;
  final String? neighborhood;
  final String? profileImageUrl;
  final bool homeService;
  final bool salonService;
  final double? distanceKm;
  final bool isVerified;

  ProfessionalModel({
    required this.id,
    required this.userId,
    required this.businessName,
    this.description,
    this.specialty,
    required this.experienceYears,
    required this.rating,
    required this.ratingCount,
    required this.isAvailable,
    this.address,
    this.neighborhood,
    this.profileImageUrl,
    required this.homeService,
    required this.salonService,
    this.distanceKm,
    this.isVerified = false,
  });

  factory ProfessionalModel.fromJson(Map<String, dynamic> json) => ProfessionalModel(
        id: json['id'],
        userId: json['user_id'],
        businessName: json['business_name'],
        description: json['description'],
        specialty: json['specialty'],
        experienceYears: json['experience_years'] ?? 0,
        rating: double.tryParse(json['rating'].toString()) ?? 0.0,
        ratingCount: json['rating_count'] ?? 0,
        isAvailable: json['is_available'] ?? true,
        address: json['address'],
        neighborhood: json['neighborhood'],
        profileImageUrl: json['profile_image_url'],
        homeService: json['home_service'] ?? false,
        salonService: json['salon_service'] ?? true,
        distanceKm: json['distance_km'] != null
            ? double.tryParse(json['distance_km'].toString())
            : null,
        isVerified: json['is_verified'] ?? false,
      );
}
