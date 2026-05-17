import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/appointment_model.dart';
import '../../../providers/appointment_provider.dart';
import '../../../providers/auth_provider.dart';

class AppointmentsScreen extends StatefulWidget {
  const AppointmentsScreen({super.key});

  @override
  State<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends State<AppointmentsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _load();
  }

  void _load() {
    final user = context.read<AuthProvider>().user;
    final provider = context.read<AppointmentProvider>();
    if (user?.isProfessional == true) {
      provider.loadProfessionalAppointments();
    } else {
      provider.loadClientAppointments();
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AppointmentProvider>();
    final user = context.read<AuthProvider>().user;
    final isProfessional = user?.isProfessional ?? false;

    final active = provider.appointments.where((a) => a.isPending || a.isConfirmed).toList();
    final history = provider.appointments.where((a) => a.isCanceled || a.isCompleted).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agendamentos'),
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppTheme.primary,
          unselectedLabelColor: AppTheme.textSecondary,
          indicatorColor: AppTheme.primary,
          tabs: [
            Tab(text: 'Ativos (${active.length})'),
            Tab(text: 'Histórico (${history.length})'),
          ],
        ),
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _AppointmentList(appointments: active, isProfessional: isProfessional, onRefresh: _load),
                _AppointmentList(appointments: history, isProfessional: isProfessional, onRefresh: _load),
              ],
            ),
    );
  }
}

class _AppointmentList extends StatelessWidget {
  final List<AppointmentModel> appointments;
  final bool isProfessional;
  final VoidCallback onRefresh;

  const _AppointmentList({required this.appointments, required this.isProfessional, required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    if (appointments.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.calendar_today_outlined, size: 64, color: AppTheme.textSecondary),
            SizedBox(height: 12),
            Text('Nenhum agendamento aqui', style: TextStyle(color: AppTheme.textSecondary)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: appointments.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (ctx, i) => _AppointmentCard(appointment: appointments[i], isProfessional: isProfessional, onRefresh: onRefresh),
      ),
    );
  }
}

class _AppointmentCard extends StatelessWidget {
  final AppointmentModel appointment;
  final bool isProfessional;
  final VoidCallback onRefresh;

  const _AppointmentCard({required this.appointment, required this.isProfessional, required this.onRefresh});

  Color get _statusColor {
    switch (appointment.status) {
      case 'PENDING': return AppTheme.warning;
      case 'CONFIRMED': return AppTheme.success;
      case 'CANCELED': return AppTheme.error;
      case 'COMPLETED': return AppTheme.textSecondary;
      default: return AppTheme.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.read<AppointmentProvider>();
    final date = DateTime.tryParse(appointment.appointmentDate);
    final dateStr = date != null ? DateFormat("d 'de' MMMM 'de' yyyy", 'pt_BR').format(date) : appointment.appointmentDate;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Column(
        children: [
          // Status header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: _statusColor.withOpacity(0.08),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Container(width: 8, height: 8, decoration: BoxDecoration(color: _statusColor, shape: BoxShape.circle)),
                const SizedBox(width: 8),
                Text(appointment.statusLabel, style: TextStyle(color: _statusColor, fontWeight: FontWeight.w600, fontSize: 13)),
                const Spacer(),
                Text('Nº ${appointment.id}', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.calendar_today_outlined, size: 16, color: AppTheme.primary),
                    const SizedBox(width: 6),
                    Text(dateStr, style: const TextStyle(fontWeight: FontWeight.w600)),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.access_time, size: 16, color: AppTheme.primary),
                    const SizedBox(width: 6),
                    Text('${appointment.startTime} - ${appointment.endTime}'),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.person_outlined, size: 16, color: AppTheme.primary),
                    const SizedBox(width: 6),
                    Text(appointment.clientName),
                    const SizedBox(width: 8),
                    const Icon(Icons.phone_outlined, size: 14, color: AppTheme.textSecondary),
                    const SizedBox(width: 4),
                    Text(appointment.clientPhone, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
                if (appointment.notes != null) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.notes_outlined, size: 16, color: AppTheme.textSecondary),
                      const SizedBox(width: 6),
                      Expanded(child: Text(appointment.notes!, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13))),
                    ],
                  ),
                ],
                // Actions
                if (appointment.isPending || appointment.isConfirmed) ...[
                  const SizedBox(height: 12),
                  const Divider(height: 1),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      if (isProfessional && appointment.isPending)
                        TextButton.icon(
                          onPressed: () async {
                            final ok = await provider.confirm(appointment.id);
                            if (ok) onRefresh();
                          },
                          icon: const Icon(Icons.check_circle_outline, size: 18),
                          label: const Text('Confirmar'),
                          style: TextButton.styleFrom(foregroundColor: AppTheme.success),
                        ),
                      TextButton.icon(
                        onPressed: () => _showCancelDialog(context, provider),
                        icon: const Icon(Icons.cancel_outlined, size: 18),
                        label: const Text('Cancelar'),
                        style: TextButton.styleFrom(foregroundColor: AppTheme.error),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showCancelDialog(BuildContext context, AppointmentProvider provider) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Cancelar agendamento?'),
        content: const Text('Esta ação não pode ser desfeita.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Não')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              final ok = await provider.cancel(appointment.id);
              if (ok) onRefresh();
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.error),
            child: const Text('Sim, cancelar'),
          ),
        ],
      ),
    );
  }
}
