class ServiceModel {
  final int id;
  final int professionalId;
  final String name;
  final String? description;
  final double price;
  final int durationMinutes;
  final bool isActive;

  ServiceModel({
    required this.id,
    required this.professionalId,
    required this.name,
    this.description,
    required this.price,
    required this.durationMinutes,
    required this.isActive,
  });

  factory ServiceModel.fromJson(Map<String, dynamic> json) => ServiceModel(
        id: json['id'],
        professionalId: json['professional_id'],
        name: json['name'],
        description: json['description'],
        price: double.tryParse(json['price'].toString()) ?? 0.0,
        durationMinutes: json['duration_minutes'],
        isActive: json['is_active'] ?? true,
      );

  String get formattedPrice => 'R\$ ${price.toStringAsFixed(2).replaceAll('.', ',')}';
  String get formattedDuration =>
      durationMinutes >= 60
          ? '${durationMinutes ~/ 60}h${durationMinutes % 60 > 0 ? '${durationMinutes % 60}min' : ''}'
          : '${durationMinutes}min';
}
