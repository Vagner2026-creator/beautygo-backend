import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../../providers/notification_provider.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => context.read<NotificationProvider>().load());
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<NotificationProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificações'),
        actions: [
          if (provider.unreadCount > 0)
            TextButton(
              onPressed: () => provider.markAllRead(),
              child: const Text('Marcar tudo como lido', style: TextStyle(color: AppTheme.primary, fontSize: 13)),
            ),
        ],
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.notifications.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications_none, size: 64, color: AppTheme.textSecondary),
                      SizedBox(height: 12),
                      Text('Nenhuma notificação', style: TextStyle(color: AppTheme.textSecondary)),
                    ],
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: provider.notifications.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (ctx, i) {
                    final notif = provider.notifications[i];
                    final createdAt = DateTime.tryParse(notif.createdAt);
                    final timeStr = createdAt != null
                        ? DateFormat("d MMM 'às' HH:mm", 'pt_BR').format(createdAt.toLocal())
                        : '';

                    return GestureDetector(
                      onTap: () => provider.markRead(notif.id),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: notif.isRead ? Colors.white : AppTheme.primary.withOpacity(0.06),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: notif.isRead ? AppTheme.divider : AppTheme.primary.withOpacity(0.2)),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: _iconColor(notif.type).withOpacity(0.12),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(_iconData(notif.type), color: _iconColor(notif.type), size: 20),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(child: Text(notif.title, style: TextStyle(fontWeight: notif.isRead ? FontWeight.w500 : FontWeight.bold, fontSize: 14))),
                                      if (!notif.isRead)
                                        Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppTheme.primary, shape: BoxShape.circle)),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(notif.message, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13, height: 1.4)),
                                  const SizedBox(height: 6),
                                  Text(timeStr, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 11)),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }

  IconData _iconData(String type) {
    switch (type) {
      case 'appointment_new': return Icons.calendar_today_outlined;
      case 'appointment_confirmed': return Icons.check_circle_outline;
      case 'appointment_canceled': return Icons.cancel_outlined;
      case 'appointment_rescheduled': return Icons.update;
      default: return Icons.notifications_outlined;
    }
  }

  Color _iconColor(String type) {
    switch (type) {
      case 'appointment_new': return AppTheme.primary;
      case 'appointment_confirmed': return AppTheme.success;
      case 'appointment_canceled': return AppTheme.error;
      case 'appointment_rescheduled': return AppTheme.warning;
      default: return AppTheme.textSecondary;
    }
  }
}
