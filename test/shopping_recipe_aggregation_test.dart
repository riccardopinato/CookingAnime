import 'package:animekitchen/features/recipes/domain/recipe.dart';
import 'package:animekitchen/features/shopping/application/shopping_provider.dart';
import 'package:animekitchen/features/shopping/data/shared_preferences_shopping_repository.dart';
import 'package:animekitchen/features/shopping/domain/shopping_item.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

Recipe _recipe(String id, String title, double grams, {String unit = 'g'}) =>
    Recipe(
      id: id,
      contentVersion: 1,
      contentOrigin: RecipeContentOrigin.original,
      title: title,
      animeSource: 'Test',
      prepMinutes: 10,
      cookMinutes: 20,
      servings: 2,
      difficulty: RecipeDifficulty.easy,
      ingredients: [
        RecipeIngredient(
          id: 'riso_cotto',
          name: 'rice',
          quantity: grams,
          unit: unit,
        ),
        const RecipeIngredient(
          id: 'cipollotto_fresco',
          name: 'spring onion',
          quantity: 1,
          unit: 'piece',
        ),
      ],
      steps: const [RecipeStep(id: 'step_one', text: 'Cook the rice.')],
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('recipe ingredient quantities scale and merge only in the same unit', () async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    final container = ProviderContainer(
      overrides: [
        shoppingRepositoryProvider.overrideWithValue(
          SharedPreferencesShoppingRepository(prefs),
        ),
      ],
    );
    addTearDown(container.dispose);
    final notifier = container.read(shoppingProvider.notifier);
    notifier.addManual('rice', 'Manual');
    notifier.addRecipe(_recipe('r1', 'A', 100), servings: 4);
    var items = container.read(shoppingProvider);
    expect(items.where((i) => i.name == 'rice'), hasLength(2));
    expect(items.first.quantity, isNull);
    expect(items.last.category, 'produce');

    notifier.addRecipe(_recipe('r2', 'B', 70), servings: 2);
    items = container.read(shoppingProvider);
    final rice = items.singleWhere((i) => i.name == 'rice' && i.quantity != null);
    expect(rice.quantity, 270); // 100 × (4/2) + 70 × (2/2).
    expect(rice.recipeSource, contains('A'));
    expect(rice.recipeSource, contains('B'));

    notifier.addRecipe(_recipe('r3', 'C', 50, unit: 'ml'), servings: 2);
    items = container.read(shoppingProvider);
    expect(items.where((i) => i.name == 'rice' && i.quantity != null), hasLength(2));

    notifier.setCategory(rice.id, 'pantry');
    expect(container.read(shoppingProvider).firstWhere((i) => i.id == rice.id).category, 'pantry');
    notifier.setCategory(rice.id, 'invalid');
    expect(container.read(shoppingProvider).firstWhere((i) => i.id == rice.id).category, 'pantry');
  });

  test('legacy shopping data remains readable without category or quantity', () async {
    SharedPreferences.setMockInitialValues({
      'shopping_list_items_v1': [
        '{"id":"old","name":"Salt","recipeSource":"Manuale","isBought":true}',
      ],
    });
    final prefs = await SharedPreferences.getInstance();
    final repository = SharedPreferencesShoppingRepository(prefs);
    final items = repository.loadItems();
    expect(items, hasLength(1));
    expect(items.single.category, 'other');
    expect(items.single.isBought, isTrue);
    expect(items.single.displayText, 'Salt');
    await repository.saveItems(items);
    expect(ShoppingItem.fromJson(items.single.toJson()).id, 'old');
  });
}
