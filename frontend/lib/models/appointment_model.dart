class AppointmentModel {
  final int id;
  final int clientId;
  final int professionalId;
  final int serviceId;
  final String appointmentDate;
  final String startTime;
  final String endTime;
  final String status;
  final String clientName;
  final String clientPhone;
  final String? notes;
  final String createdAt;

  AppointmentModel({
    required this.id,
    required this.clientId,
    required this.professionalId,
    required this.serviceId,
    required this.appointmentDate,
    required this.startTime,
    required this.endTime,
    required this.status,
    required this.clientName,
    required this.clientPhone,
    this.notes,
    required this.createdAt,
  });

  factory AppointmentModel.fromJson(Map<String, dynamic> json) => AppointmentModel(
        id: json['id'],
        clientId: json['client_id'],
        professionalId: json['professional_id'],
        serviceId: json['service_id'],
        appointmentDate: json['appointment_date'],
        startTime: json['start_time'],
        endTime: json['end_time'],
        status: json['status'],
        clientName: json['client_name'],
        clientPhone: json['client_phone'],
        notes: json['notes'],
        createdAt: json['created_at'],
      );

  bool get isPending => status == 'PENDING';
  bool get isConfirmed => status == 'CONFIRMED';
  bool get isCanceled => status == 'CANCELED';
  bool get isCompleted => status == 'COMPLETED';

  String get statusLabel {
    switch (status) {
      case 'PENDING': return 'Pendente';
      case 'CONFIRMED': return 'Confirmado';
      case 'CANCELED': return 'Cancelado';
      case 'COMPLETED': return 'Concluído';
      default: return status;
    }
  }
}
