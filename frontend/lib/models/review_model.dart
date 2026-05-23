class ReviewModel {
  final int id;
  final int clientId;
  final int professionalId;
  final int rating;
  final String? comment;
  final DateTime createdAt;

  ReviewModel({
    required this.id,
    required this.clientId,
    required this.professionalId,
    required this.rating,
    this.comment,
    required this.createdAt,
  });

  factory ReviewModel.fromJson(Map<String, dynamic> json) => ReviewModel(
        id: json['id'],
        clientId: json['client_id'],
        professionalId: json['professional_id'],
        rating: json['rating'],
        comment: json['comment'],
        createdAt: DateTime.parse(json['created_at']),
      );
}
