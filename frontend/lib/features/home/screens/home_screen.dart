import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shimmer/shimmer.dart';
import '../../../core/theme/app_theme.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/category_provider.dart';
import '../../../providers/professional_provider.dart';
import '../../../providers/notification_provider.dart';
import '../../../models/category_model.dart';
import '../../../widgets/professional_card.dart';
import '../../notifications/screens/notifications_screen.dart';
import '../../search/screens/search_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0; // 0 = "Todos", 1+ = categories[index-1]

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CategoryProvider>().load();
      context.read<ProfessionalProvider>().search();
      context.read<NotificationProvider>().load();
    });
  }

  void _onCategoryTap(int index, List<CategoryModel> categories) {
    setState(() => _selectedIndex = index);
    final categoryId = index == 0 ? null : categories[index - 1].id;
    context.read<ProfessionalProvider>().search(categoryId: categoryId);
  }

  static IconData _iconFromString(String? name) {
    const map = <String, IconData>{
      'content_cut': Icons.content_cut,
      'spa': Icons.spa,
      'spa_outlined': Icons.spa_outlined,
      'face_retouching_natural': Icons.face_retouching_natural,
      'brush': Icons.brush,
      'brush_outlined': Icons.brush_outlined,
      'self_improvement': Icons.self_improvement,
      'colorize': Icons.colorize,
      'dry_cleaning': Icons.dry_cleaning,
      'face': Icons.face,
      'face_outlined': Icons.face_outlined,
      'fitness_center': Icons.fitness_center,
      'healing': Icons.healing,
      'local_florist': Icons.local_florist,
      'people': Icons.people,
      'volunteer_activism': Icons.volunteer_activism,
      'auto_fix_high': Icons.auto_fix_high,
      'palette': Icons.palette,
      'style': Icons.style,
    };
    return map[name] ?? Icons.star_outline;
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final catProvider = context.watch<CategoryProvider>();
    final proProvider = context.watch<ProfessionalProvider>();
    final notifProvider = context.watch<NotificationProvider>();
    final firstName = auth.user?.fullName.split(' ').first ?? '';
    final categories = catProvider.categories;

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // Greeting + notification button
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Olá, $firstName! 👋',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'Encontre o melhor serviço para você',
                            style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                    Stack(
                      children: [
                        IconButton(
                          onPressed: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                          ),
                          icon: const Icon(Icons.notifications_outlined),
                        ),
                        if (notifProvider.unreadCount > 0)
                          Positioned(
                            right: 8,
                            top: 8,
                            child: Container(
                              width: 16,
                              height: 16,
                              decoration: const BoxDecoration(
                                color: AppTheme.error,
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Text(
                                  '${notifProvider.unreadCount}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: AppTheme.primary,
                      child: Text(
                        auth.user?.fullName.substring(0, 1).toUpperCase() ?? '?',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // Search bar
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: GestureDetector(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const SearchScreen()),
                  ),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.divider),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.04),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.search, color: AppTheme.textSecondary),
                        SizedBox(width: 10),
                        Text(
                          'Buscar serviço ou profissional...',
                          style: TextStyle(color: AppTheme.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            // Categories row
            SliverToBoxAdapter(
              child: SizedBox(
                height: 90,
                child: catProvider.isLoading
                    ? _CategoryShimmer()
                    : ListView.separated(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        itemCount: categories.length + 1, // +1 for "Todos"
                        separatorBuilder: (_, __) => const SizedBox(width: 12),
                        itemBuilder: (ctx, i) {
                          final isAll = i == 0;
                          final label = isAll ? 'Todos' : categories[i - 1].name;
                          final icon = isAll
                              ? Icons.grid_view_rounded
                              : _iconFromString(categories[i - 1].icon);
                          final selected = _selectedIndex == i;

                          return GestureDetector(
                            onTap: () => _onCategoryTap(i, categories),
                            child: Column(
                              children: [
                                AnimatedContainer(
                                  duration: const Duration(milliseconds: 200),
                                  width: 56,
                                  height: 56,
                                  decoration: BoxDecoration(
                                    color: selected ? AppTheme.primary : Colors.white,
                                    borderRadius: BorderRadius.circular(16),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withOpacity(0.06),
                                        blurRadius: 8,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: Icon(
                                    icon,
                                    color: selected ? Colors.white : AppTheme.textSecondary,
                                    size: 24,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  label,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: selected ? FontWeight.bold : FontWeight.normal,
                                    color: selected ? AppTheme.primary : AppTheme.textSecondary,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          );
                        },
                      ),
              ),
            ),
            // Section header
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Profissionais',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Text(
                      '${proProvider.professionals.length} encontrados',
                      style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ),
            // Professionals list
            if (proProvider.isLoading)
              const SliverFillRemaining(
                child: Center(child: CircularProgressIndicator()),
              )
            else if (proProvider.professionals.isEmpty)
              const SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.search_off, size: 64, color: AppTheme.textSecondary),
                      SizedBox(height: 12),
                      Text(
                        'Nenhum profissional encontrado',
                        style: TextStyle(color: AppTheme.textSecondary),
                      ),
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

class _CategoryShimmer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey.shade200,
      highlightColor: Colors.grey.shade100,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        itemCount: 6,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (_, __) => Column(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            const SizedBox(height: 6),
            Container(
              width: 40,
              height: 10,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
