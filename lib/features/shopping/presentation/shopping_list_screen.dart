import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/decorative_characters/decorative_character_registry.dart';
import '../../../core/decorative_characters/decorative_character_stage.dart';
import '../../../core/theme/app_design_tokens.dart';
import '../../../core/widgets/app_empty_state.dart';
import '../../../l10n/app_localizations.dart';
import '../application/shopping_provider.dart';

class ShoppingListScreen extends ConsumerWidget {
  const ShoppingListScreen({super.key});

  String _categoryLabel(AppLocalizations l10n, String category) => switch (category) {
    'produce' => l10n.shoppingCategoryProduce,
    'protein' => l10n.shoppingCategoryProtein,
    'dairy' => l10n.shoppingCategoryDairy,
    'pantry' => l10n.shoppingCategoryPantry,
    _ => l10n.shoppingCategoryOther,
  };

  int _categoryRank(String category) => switch (category) {
    'produce' => 0,
    'protein' => 1,
    'dairy' => 2,
    'pantry' => 3,
    _ => 4,
  };


  Future<void> _showAddDialog(
    BuildContext context,
    WidgetRef ref,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    final controller = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(l10n.addIngredientTitle),
        content: TextField(
          controller: controller,
          autofocus: true,
          textInputAction: TextInputAction.done,
          decoration: InputDecoration(hintText: l10n.addIngredientHint),
          onSubmitted: (value) {
            if (value.trim().isEmpty) return;
            ref
                .read(shoppingProvider.notifier)
                .addManual(value, l10n.manualItemSource);
            Navigator.of(dialogContext).pop();
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            onPressed: () {
              final value = controller.text;
              if (value.trim().isEmpty) return;
              ref
                  .read(shoppingProvider.notifier)
                  .addManual(value, l10n.manualItemSource);
              Navigator.of(dialogContext).pop();
            },
            child: Text(l10n.addItem),
          ),
        ],
      ),
    );

    controller.dispose();
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final items = ref.watch(shoppingProvider);
    final hasBought = items.any((item) => item.isBought);
    final ordered = [...items]..sort((a, b) {
      final categoryOrder = _categoryRank(a.category).compareTo(_categoryRank(b.category));
      if (categoryOrder != 0) return categoryOrder;
      if (a.isBought != b.isBought) return a.isBought ? 1 : -1;
      return a.name.toLowerCase().compareTo(b.name.toLowerCase());
    });

    return Scaffold(
      backgroundColor: Colors.transparent,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddDialog(context, ref),
        icon: const Icon(Icons.add),
        label: Text(l10n.addItem),
      ),
      body: items.isEmpty
          ? AppEmptyState(
              icon: Icons.shopping_basket_outlined,
              title: l10n.shoppingEmptyTitle,
              body: l10n.shoppingEmptyBody,
              decoration: const DecorativeCharacterStage(
                slot: DecorativeSlot.shoppingEmpty,
                size: 132,
              ),
            )
          : Column(
              children: [
                if (hasBought)
                  Align(
                    alignment: Alignment.centerRight,
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(
                        AppSpacing.medium,
                        AppSpacing.small,
                        AppSpacing.medium,
                        0,
                      ),
                      child: TextButton.icon(
                        onPressed: () {
                          ref.read(shoppingProvider.notifier).clearBought();
                        },
                        icon: const Icon(Icons.delete_sweep_outlined),
                        label: Text(l10n.clearBought),
                      ),
                    ),
                  ),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.fromLTRB(
                      AppSpacing.medium,
                      AppSpacing.small,
                      AppSpacing.medium,
                      96,
                    ),
                    itemCount: ordered.length,
                    itemBuilder: (context, index) {
                      final item = ordered[index];
                      final showHeading = index == 0 || ordered[index - 1].category != item.category;
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (showHeading)
                            Padding(
                              padding: const EdgeInsets.fromLTRB(8, 16, 8, 12),
                              child: Text(_categoryLabel(l10n, item.category),
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w800,
                                )),
                            ),
                          Padding(
                        padding: const EdgeInsets.only(
                          bottom: AppSpacing.small,
                        ),
                        child: Dismissible(
                          key: ValueKey(item.id),
                          direction: DismissDirection.endToStart,
                          onDismissed: (_) {
                            ref.read(shoppingProvider.notifier).remove(item.id);
                          },
                          background: Container(
                            alignment: Alignment.centerRight,
                            padding: const EdgeInsets.only(
                              right: AppSpacing.large,
                            ),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.errorContainer,
                              borderRadius: BorderRadius.circular(
                                AppRadii.container,
                              ),
                            ),
                            child: Icon(
                              Icons.delete_outline,
                              color: Theme.of(context)
                                  .colorScheme
                                  .onErrorContainer,
                            ),
                          ),
                          child: Card(
                            elevation: 0,
                            clipBehavior: Clip.antiAlias,
                            color: item.isBought
                                ? Theme.of(context).colorScheme.surfaceContainerLow
                                : Theme.of(context).colorScheme.surfaceContainerHigh,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(AppRadii.card),
                            ),
                            child: CheckboxListTile(
                              value: item.isBought,
                              controlAffinity: ListTileControlAffinity.leading,
                              title: Text(
                                item.displayText,
                                style: TextStyle(
                                  decoration: item.isBought
                                      ? TextDecoration.lineThrough
                                      : null,
                                ),
                              ),
                              subtitle: Text(item.recipeSource),
                              secondary: PopupMenuButton<String>(
                                tooltip: l10n.shoppingChangeCategory,
                                icon: const Icon(Icons.tune_rounded),
                                initialValue: item.category,
                                onSelected: (category) => ref.read(shoppingProvider.notifier).setCategory(item.id, category),
                                itemBuilder: (_) => [
                                  for (final category in const ['produce', 'protein', 'dairy', 'pantry', 'other'])
                                    PopupMenuItem(value: category, child: Text(_categoryLabel(l10n, category))),
                                ],
                              ),
                              onChanged: (_) {
                                ref
                                    .read(shoppingProvider.notifier)
                                    .toggle(item.id);
                              },
                            ),
                          ),
                        ),
                          ),
                        ],
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }
}
