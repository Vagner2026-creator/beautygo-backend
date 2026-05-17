import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/professional_provider.dart';
import '../../../providers/notification_provider.dart';
import '../../../widgets/professional_card.dart';
import '../../search/screens/search_screen.dart';
import '../../notifications/screens/notifications_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _searchCtrl = TextEditingController();

  final List<Map<String, dynamic>> _categories = [
    {'label': 'Todos', 'icon': Icons.grid_view_rounded, 'id': null},
    {'label': 'Cabelo', 'icon': Icons.content_cut, 'id': 1},
    {'label': 'Unhas', 'icon': Icons.spa_outlined, 'id': 2},
    {'label': 'Sobrancelha', 'icon': Icons.face_retouching_natural, 'id': 3},
    {'label': 'Maquiagem', 'icon': Icons.brush_outlined, 'id': 4},
    {'label': 'Massagem', 'icon': Icons.self_improvement, 'id': 5},
  ];

  int _selectedCategory = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ProfessionalProvider>().search();
      context.read<NotificationProvider>().load();
    });
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  void _onCategoryTap(int index) {
    setState(() => _selectedCategory = index);
    final cat = _categories[index];
    context.read<ProfessionalProvider>().search(categoryId: cat['id']);
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final proProvider = context.watch<ProfessionalProvider>();
    final notifProvider = context.watch<NotificationProvider>();
    final firstName = auth.user?.fullName.split(' ').first ?? '';

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Olá, $firstName! 👋', style: Theme.of(context).textTheme.titleLarge),
                          const SizedBox(height: 2),
                          const Text('Encontre o melhor serviço para você', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                        ],
                      ),
                    ),
                    Stack(
                      children: [
                        IconButton(
                          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NotificationsScreen())),
                          icon: const Icon(Icons.notifications_outlined),
                        ),
                        if (notifProvider.unreadCount > 0)
                          Positioned(
                            right: 8,
                            top: 8,
                            child: Container(
                              width: 16,
                              height: 16,
                              decoration: const BoxDecoration(color: AppTheme.error, shape: BoxShape.circle),
                              child: Center(child: Text('${notifProvider.unreadCount}', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold))),
                            ),
                          ),
                      ],
                    ),
                    const CircleAvatar(
                      radius: 20,
                      backgroundColor: AppTheme.primary,
                      child: Icon(Icons.person, color: Colors.white, size: 20),
                    ),
                  ],
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: GestureDetector(
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SearchScreen())),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.divider),
                      boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2))],
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.search, color: AppTheme.textSecondary),
                        SizedBox(width: 10),
                        Text('Buscar serviço ou profissional...', style: TextStyle(color: AppTheme.textSecondary)),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: SizedBox(
                height: 90,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: _categories.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 12),
                  itemBuilder: (ctx, i) {
                    final cat = _categories[i];
                    final selected = _selectedCategory == i;
                    return GestureDetector(
                      onTap: () => _onCategoryTap(i),
                      child: Column(
                        children: [
                          AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            width: 56,
                            height: 56,
                            decoration: BoxDecoration(
                              color: selected ? AppTheme.primary : Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 8, offset: const Offset(0, 2))],
                            ),
                            child: Icon(cat['icon'] as IconData, color: selected ? Colors.white : AppTheme.textSecondary, size: 24),
                          ),
                          const SizedBox(height: 6),
                          Text(cat['label'] as String, style: TextStyle(fontSize: 11, fontWeight: selected ? FontWeight.bold : FontWeight.normal, color: selected ? AppTheme.primary : AppTheme.textSecondary)),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Profissionais', style: Theme.of(context).textTheme.titleMedium),
                    Text('${proProvider.professionals.length} encontrados', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
            ),
            if (proProvider.isLoading)
              const SliverFillRemaining(child: Center(child: CircularProgressIndicator()))
            else if (proProvider.professionals.isEmpty)
              const SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.search_off, size: 64, color: AppTheme.textSecondary),
                      SizedBox(height: 12),
                      Text('Nenhum profissional encontrado', style: TextStyle(color: AppTheme.textSecondary)),
                    ],
                  ),
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (ctx, i) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: ProfessionalCard(professional: proProvider.professionals[i]),
                    ),
                    childCount: proProvider.professionals.length,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
