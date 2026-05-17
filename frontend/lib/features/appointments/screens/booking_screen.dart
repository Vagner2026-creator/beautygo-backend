import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/professional_model.dart';
import '../../../models/service_model.dart';
import '../../../providers/appointment_provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/professional_provider.dart';

class BookingScreen extends StatefulWidget {
  final ProfessionalModel professional;
  final ServiceModel service;

  const BookingScreen({super.key, required this.professional, required this.service});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  String? _selectedSlot;
  List<String> _slots = [];
  bool _loadingSlots = false;

  final _nameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  int _step = 0;

  @override
  void initState() {
    super.initState();
    final user = context.read<AuthProvider>().user;
    _nameCtrl.text = user?.fullName ?? '';
    _loadSlots();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _phoneCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadSlots() async {
    setState(() { _loadingSlots = true; _selectedSlot = null; });
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);
    final slots = await context.read<ProfessionalProvider>().getAvailableSlots(
      professionalId: widget.professional.id,
      date: dateStr,
      serviceId: widget.service.id,
    );
    if (mounted) setState(() { _slots = slots; _loadingSlots = false; });
  }

  Future<void> _confirm() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedSlot == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Selecione um horário')));
      return;
    }
    final provider = context.read<AppointmentProvider>();
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);
    final result = await provider.book(
      professionalId: widget.professional.id,
      serviceId: widget.service.id,
      date: dateStr,
      startTime: _selectedSlot!,
      clientName: _nameCtrl.text.trim(),
      clientPhone: _phoneCtrl.text.trim(),
      notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
    );
    if (!mounted) return;
    if (result != null) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(width: 72, height: 72, decoration: BoxDecoration(color: AppTheme.success.withOpacity(0.1), shape: BoxShape.circle),
                child: const Icon(Icons.check_circle, color: AppTheme.success, size: 40)),
              const SizedBox(height: 16),
              const Text('Agendado!', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
              const SizedBox(height: 8),
              Text('Agendamento enviado com sucesso! Aguarde a confirmação do profissional.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey[600])),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
                Navigator.pop(context);
              },
              child: const Text('Ver meus agendamentos'),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(provider.error ?? 'Erro ao agendar'), backgroundColor: AppTheme.error),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agendar Serviço')),
      body: Column(
        children: [
          // Progress indicator
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            child: Row(
              children: List.generate(3, (i) => Expanded(
                child: Row(
                  children: [
                    _StepCircle(index: i, currentStep: _step),
                    if (i < 2) Expanded(child: Container(height: 2, color: _step > i ? AppTheme.primary : AppTheme.divider)),
                  ],
                ),
              )),
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: [
                _buildStep0(),
                _buildStep1(),
                _buildStep2(),
              ][_step],
            ),
          ),
          _buildBottomBar(),
        ],
      ),
    );
  }

  Widget _buildStep0() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Service summary
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.06), borderRadius: BorderRadius.circular(16)),
          child: Row(
            children: [
              Container(width: 48, height: 48, decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.15), borderRadius: BorderRadius.circular(12)),
                child: const Icon(Icons.spa_outlined, color: AppTheme.primary)),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(widget.service.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text('${widget.service.formattedDuration} · ${widget.service.formattedPrice}', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
              ])),
            ],
          ),
        ),
        const SizedBox(height: 24),
        Text('Selecione a data', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        SizedBox(
          height: 80,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: 14,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (ctx, i) {
              final date = DateTime.now().add(Duration(days: i + 1));
              final selected = DateFormat('yyyy-MM-dd').format(date) == DateFormat('yyyy-MM-dd').format(_selectedDate);
              return GestureDetector(
                onTap: () { setState(() => _selectedDate = date); _loadSlots(); },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 56,
                  decoration: BoxDecoration(
                    color: selected ? AppTheme.primary : Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: selected ? AppTheme.primary : AppTheme.divider),
                  ),
                  child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                    Text(DateFormat('EEE', 'pt_BR').format(date).substring(0, 3), style: TextStyle(fontSize: 11, color: selected ? Colors.white70 : AppTheme.textSecondary)),
                    const SizedBox(height: 4),
                    Text('${date.day}', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: selected ? Colors.white : AppTheme.textPrimary)),
                    Text(DateFormat('MMM', 'pt_BR').format(date), style: TextStyle(fontSize: 11, color: selected ? Colors.white70 : AppTheme.textSecondary)),
                  ]),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 24),
        Text('Horários disponíveis', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        if (_loadingSlots)
          const Center(child: CircularProgressIndicator())
        else if (_slots.isEmpty)
          const Center(child: Padding(padding: EdgeInsets.all(20), child: Text('Sem horários disponíveis para esta data', style: TextStyle(color: AppTheme.textSecondary))))
        else
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: _slots.map((slot) {
              final sel = _selectedSlot == slot;
              return GestureDetector(
                onTap: () => setState(() => _selectedSlot = slot),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: sel ? AppTheme.primary : Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: sel ? AppTheme.primary : AppTheme.divider),
                  ),
                  child: Text(slot, style: TextStyle(fontWeight: FontWeight.w500, color: sel ? Colors.white : AppTheme.textPrimary)),
                ),
              );
            }).toList(),
          ),
      ],
    );
  }

  Widget _buildStep1() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Seus dados de contato', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          const Text('O profissional precisa dessas informações para confirmar.', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
          const SizedBox(height: 20),
          TextFormField(
            controller: _nameCtrl,
            decoration: const InputDecoration(labelText: 'Nome completo', prefixIcon: Icon(Icons.person_outlined)),
            validator: (v) => v == null || v.trim().isEmpty ? 'Informe seu nome' : null,
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _phoneCtrl,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(labelText: 'Telefone / WhatsApp', prefixIcon: Icon(Icons.phone_outlined)),
            validator: (v) => v == null || v.trim().length < 8 ? 'Telefone inválido' : null,
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _notesCtrl,
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'Observações (opcional)', prefixIcon: Icon(Icons.notes_outlined), alignLabelWithHint: true),
          ),
        ],
      ),
    );
  }

  Widget _buildStep2() {
    final dateFormatted = DateFormat("EEEE, d 'de' MMMM", 'pt_BR').format(_selectedDate);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Confirme seu agendamento', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 20),
        _SummaryRow(icon: Icons.store_outlined, label: 'Profissional', value: widget.professional.businessName),
        _SummaryRow(icon: Icons.spa_outlined, label: 'Serviço', value: widget.service.name),
        _SummaryRow(icon: Icons.attach_money, label: 'Valor', value: widget.service.formattedPrice),
        _SummaryRow(icon: Icons.timer_outlined, label: 'Duração', value: widget.service.formattedDuration),
        _SummaryRow(icon: Icons.calendar_today_outlined, label: 'Data', value: dateFormatted),
        _SummaryRow(icon: Icons.access_time, label: 'Horário', value: _selectedSlot ?? '-'),
        _SummaryRow(icon: Icons.person_outlined, label: 'Nome', value: _nameCtrl.text),
        _SummaryRow(icon: Icons.phone_outlined, label: 'Telefone', value: _phoneCtrl.text),
        if (_notesCtrl.text.isNotEmpty)
          _SummaryRow(icon: Icons.notes_outlined, label: 'Obs.', value: _notesCtrl.text),
      ],
    );
  }

  Widget _buildBottomBar() {
    final appProvider = context.watch<AppointmentProvider>();
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, -2))]),
      child: Row(
        children: [
          if (_step > 0)
            Expanded(
              child: OutlinedButton(
                onPressed: () => setState(() => _step--),
                style: OutlinedButton.styleFrom(minimumSize: const Size(0, 52), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))),
                child: const Text('Voltar'),
              ),
            ),
          if (_step > 0) const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: appProvider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : ElevatedButton(
                    onPressed: () {
                      if (_step == 0) {
                        if (_selectedSlot == null) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Selecione um horário'))); return; }
                        setState(() => _step = 1);
                      } else if (_step == 1) {
                        if (_formKey.currentState!.validate()) setState(() => _step = 2);
                      } else {
                        _confirm();
                      }
                    },
                    child: Text(_step < 2 ? 'Continuar' : 'Confirmar Agendamento'),
                  ),
          ),
        ],
      ),
    );
  }
}

class _StepCircle extends StatelessWidget {
  final int index;
  final int currentStep;

  const _StepCircle({required this.index, required this.currentStep});

  @override
  Widget build(BuildContext context) {
    final done = currentStep > index;
    final active = currentStep == index;
    final labels = ['Data & Hora', 'Contato', 'Confirmação'];
    return Column(
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            color: done || active ? AppTheme.primary : AppTheme.divider,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: done
                ? const Icon(Icons.check, color: Colors.white, size: 16)
                : Text('${index + 1}', style: TextStyle(color: done || active ? Colors.white : AppTheme.textSecondary, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
        ),
        const SizedBox(height: 4),
        Text(labels[index], style: TextStyle(fontSize: 10, color: active ? AppTheme.primary : AppTheme.textSecondary, fontWeight: active ? FontWeight.bold : FontWeight.normal)),
      ],
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _SummaryRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppTheme.primary),
          const SizedBox(width: 12),
          SizedBox(width: 80, child: Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13))),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14))),
        ],
      ),
    );
  }
}
