class CategoryModel {
  final int id;
  final String name;
  final String? icon;
  final bool isActive;

  const CategoryModel({
    required this.id,
    required this.name,
    this.icon,
    required this.isActive,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) => CategoryModel(
        id: json['id'],
        name: json['name'],
        icon: json['icon'],
        isActive: json['is_active'] ?? true,
      );
}
