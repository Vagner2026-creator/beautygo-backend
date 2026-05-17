import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../providers/professional_provider.dart';
import '../../../widgets/professional_card.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchCtrl = TextEditingController();
  bool? _homeService;
  bool? _salonService;

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  void _search() {
    context.read<ProfessionalProvider>().search(
          keyword: _searchCtrl.text.trim(),
          homeService: _homeService,
          salonService: _salonService,
        );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ProfessionalProvider>();

    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _searchCtrl,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Buscar serviço ou profissional...',
            border: InputBorder.none,
            hintStyle: TextStyle(color: AppTheme.textSecondary),
          ),
          onSubmitted: (_) => _search(),
          onChanged: (v) { if (v.length > 2 || v.isEmpty) _search(); },
        ),
        actions: [
          IconButton(icon: const Icon(Icons.search), onPressed: _search),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showFilters(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // Active filters
          if (_homeService != null || _salonService != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.white,
              child: Row(
                children: [
                  const Text('Filtros: ', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  if (_salonService == true)
                    _FilterChip(label: 'Salão', onRemove: () { setState(() => _salonService = null); _search(); }),
                  if (_homeService == true)
                    _FilterChip(label: 'Domicílio', onRemove: () { setState(() => _homeService = null); _search(); }),
                ],
              ),
            ),
          Expanded(
            child: provider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : provider.professionals.isEmpty
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.search_off, size: 64, color: AppTheme.textSecondary),
                            SizedBox(height: 12),
                            Text('Nenhum resultado encontrado', style: TextStyle(color: AppTheme.textSecondary)),
                          ],
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: provider.professionals.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 12),
                        itemBuilder: (ctx, i) => ProfessionalCard(professional: provider.professionals[i]),
                      ),
          ),
        ],
      ),
    );
  }

  void _showFilters(BuildContext context) {
    bool? tempHome = _homeService;
    bool? tempSalon = _salonService;

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (_) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text('Filtros', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const Spacer(),
                  TextButton(
                    onPressed: () { setModalState(() { tempHome = null; tempSalon = null; }); },
                    child: const Text('Limpar'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text('Tipo de atendimento', style: TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _FilterOption(label: 'Salão', icon: Icons.store_outlined, selected: tempSalon == true, onTap: () => setModalState(() => tempSalon = tempSalon == true ? null : true))),
                  const SizedBox(width: 12),
                  Expanded(child: _FilterOption(label: 'Domicílio', icon: Icons.home_outlined, selected: tempHome == true, onTap: () => setModalState(() => tempHome = tempHome == true ? null : true))),
                ],
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  setState(() { _homeService = tempHome; _salonService = tempSalon; });
                  _search();
                },
                child: const Text('Aplicar filtros'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final VoidCallback onRemove;

  const _FilterChip({required this.label, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.primary, fontSize: 12, fontWeight: FontWeight.w500)),
          const SizedBox(width: 4),
          GestureDetector(onTap: onRemove, child: const Icon(Icons.close, size: 14, color: AppTheme.primary)),
        ],
      ),
    );
  }
}

class _FilterOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _FilterOption({required this.label, required this.icon, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: selected ? AppTheme.primary.withOpacity(0.1) : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: selected ? AppTheme.primary : AppTheme.divider, width: selected ? 2 : 1),
        ),
        child: Row(
          children: [
            Icon(icon, color: selected ? AppTheme.primary : AppTheme.textSecondary),
            const SizedBox(width: 8),
            Text(label, style: TextStyle(color: selected ? AppTheme.primary : AppTheme.textPrimary, fontWeight: selected ? FontWeight.bold : FontWeight.normal)),
          ],
        ),
      ),
    );
  }
}
