import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/persistence/shared_preferences_provider.dart';
import '../../recipes/domain/recipe.dart';
import '../data/shared_preferences_shopping_repository.dart';
import '../domain/shopping_item.dart';
import '../domain/shopping_repository.dart';

final shoppingRepositoryProvider = Provider<ShoppingRepository>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SharedPreferencesShoppingRepository(prefs);
});

class ShoppingNotifier extends Notifier<List<ShoppingItem>> {
  @override
  List<ShoppingItem> build() {
    return ref.watch(shoppingRepositoryProvider).loadItems();
  }

  void addManual(String name, String sourceLabel) {
    final trimmed = name.trim();
    if (trimmed.isEmpty) return;

    final item = ShoppingItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      name: trimmed,
      recipeSource: sourceLabel,
    );
    state = [...state, item];
    _persist();
  }

  /// Import a recipe without modifying the canonical culinary catalog.
  /// Only ingredients with matching normalized label AND unit are summed.
  /// Manual entries and unquantified items are never silently merged.
  void addRecipe(Recipe recipe, {required int servings}) {
    if (servings < 1 || servings > 99 || recipe.servings < 1) return;
    final multiplier = servings / recipe.servings;
    final updated = [...state];
    final stamp = DateTime.now().microsecondsSinceEpoch;
    for (var index = 0; index < recipe.ingredients.length; index++) {
      final ingredient = recipe.ingredients[index];
      final name = ingredient.name.trim();
      if (name.isEmpty) continue;
      final unit = ingredient.unit?.trim();
      final amount = ingredient.quantity == null
          ? null
          : ingredient.quantity! * multiplier;
      final normalized = name.toLowerCase().replaceAll(RegExp(r'\\s+'), ' ');
      final match = updated.indexWhere((item) =>
          !item.isBought &&
          item.quantity != null &&
          amount != null &&
          item.name.trim().toLowerCase().replaceAll(RegExp(r'\\s+'), ' ') == normalized &&
          (item.unit ?? '').trim().toLowerCase() ==
              (unit ?? '').toLowerCase() &&
          item.recipeSource != '' &&
          item.recipeSource != 'Manual');
      if (match >= 0) {
        final existing = updated[match];
        updated[match] = existing.copyWith(
          quantity: existing.quantity! + amount!,
          recipeSource: existing.recipeSource.contains(recipe.title)
              ? existing.recipeSource
              : '${existing.recipeSource} · ${recipe.title}',
        );
      } else {
        updated.add(ShoppingItem(
          id: 'recipe-$stamp-$index',
          name: name,
          unit: unit,
          quantity: amount,
          recipeSource: recipe.title,
        ));
      }
    }
    state = updated;
    _persist();
  }

  void toggle(String id) {
    state = [
      for (final item in state)
        if (item.id == id)
          item.copyWith(isBought: !item.isBought)
        else
          item,
    ];
    _persist();
  }

  void remove(String id) {
    state = state.where((item) => item.id != id).toList(growable: false);
    _persist();
  }

  void clearBought() {
    state = state.where((item) => !item.isBought).toList(growable: false);
    _persist();
  }

  void _persist() {
    unawaited(ref.read(shoppingRepositoryProvider).saveItems(state));
  }
}

final shoppingProvider =
    NotifierProvider<ShoppingNotifier, List<ShoppingItem>>(
  ShoppingNotifier.new,
);
