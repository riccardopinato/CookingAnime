import 'package:animekitchen/features/recipes/domain/recipe.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('recipe ingredients scale in detail and cooking without mutation', () {
    const rice = RecipeIngredient(id: 'rice', name: 'Riso', quantity: 150, unit: 'g');
    expect(rice.displayText, '150 g Riso');
    expect(rice.displayTextScaled(2), '300 g Riso');
    expect(rice.displayTextScaled(0.5), '75 g Riso');
    expect(rice.quantity, 150);
  });

  test('unquantified ingredient retains notes and wording', () {
    const salt = RecipeIngredient(id: 'salt', name: 'Sale', note: 'a piacere');
    expect(salt.displayTextScaled(3), 'Sale (a piacere)');
  });
}
