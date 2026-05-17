class NotificationModel {
  final int id;
  final int userId;
  final String title;
  final String message;
  final String type;
  final String? readAt;
  final String createdAt;

  NotificationModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.message,
    required this.type,
    this.readAt,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) => NotificationModel(
        id: json['id'],
        userId: json['user_id'],
        title: json['title'],
        message: json['message'],
        type: json['type'],
        readAt: json['read_at'],
        createdAt: json['created_at'],
      );

  bool get isRead => readAt != null;
}
