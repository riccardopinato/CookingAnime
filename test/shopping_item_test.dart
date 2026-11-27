import 'package:flutter_test/flutter_test.dart';
import 'package:animekitchen/features/shopping/domain/shopping_item.dart';

void main() {
  test('legacy shopping item JSON round trip preserves user state', () {
    const original = ShoppingItem(id: 'item-1', name: 'Soy sauce',
      recipeSource: 'Manual', isBought: true);
    final restored = ShoppingItem.fromJson(original.toJson());
    expect(restored.id, original.id);
    expect(restored.name, original.name);
    expect(restored.recipeSource, original.recipeSource);
    expect(restored.isBought, isTrue);
    expect(restored.quantity, isNull);
    expect(restored.category, 'other');
  });
  test('structured quantity and unit survive persistence', () {
    const item = ShoppingItem(id: 'i2', name: 'rice',
      recipeSource: 'Onigiri', quantity: 240, unit: 'g');
    final restored = ShoppingItem.fromJson(item.toJson());
    expect(restored.displayText, '240 g rice');
    expect(restored.quantity, 240);
    expect(restored.unit, 'g');
    expect(restored.copyWith(quantity: 360).displayText, '360 g rice');
  });
  test('source-ID categories are deterministic and editable', () {
    expect(shoppingCategoryFromIngredientId('cipollotto_fresco'), 'produce');
    expect(shoppingCategoryFromIngredientId('petto_di_pollo'), 'protein');
    expect(shoppingCategoryFromIngredientId('burro'), 'dairy');
    expect(shoppingCategoryFromIngredientId('farina_00'), 'pantry');
    expect(shoppingCategoryFromIngredientId('speciale'), 'other');
    const item = ShoppingItem(id: 'i3', name: 'onion',
      recipeSource: 'Ramen', category: 'produce');
    expect(ShoppingItem.fromJson(item.toJson()).category, 'produce');
  });

  test('manual legacy item decodes without optional quantitative fields', () {
    final restored = ShoppingItem.fromJson({
      'id': 'old', 'name': 'Salt', 'recipeSource': 'Manual',
      'isBought': false,
    });
    expect(restored.displayText, 'Salt');
  });
}
