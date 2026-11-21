import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:animekitchen/features/recipes/data/recipe_catalog_source.dart';
import 'package:animekitchen/features/recipes/data/versioned_recipe_catalog_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('production Flutter repository loads all 162 recipes in six languages', () async {
    const locales = ['it', 'en', 'es', 'fr', 'de', 'pt'];
    final source = AssetRecipeCatalogSource(rootBundle);
    for (final locale in locales) {
      final recipes = await VersionedRecipeCatalogRepository(
        source: source,
        localeCode: locale,
      ).loadPublishedRecipes();
      expect(recipes.length, 162, reason: 'locale $locale');
      expect(recipes.map((r) => r.id).toSet().length, 162, reason: 'locale $locale');
      for (final recipe in recipes) {
        expect(recipe.title.trim(), isNotEmpty);
        expect(recipe.ingredients, isNotEmpty);
        expect(recipe.steps, isNotEmpty);
        expect(recipe.ingredients.every((i) => i.name.trim().isNotEmpty), isTrue);
        expect(recipe.steps.every((s) => s.text.trim().isNotEmpty), isTrue);
        expect(recipe.contentVersion, greaterThan(0));
      }
    }
  });

  test('corrected sanma and tofu cases reach the Flutter runtime', () async {
    final source = AssetRecipeCatalogSource(rootBundle);
    final en = await VersionedRecipeCatalogRepository(
      source: source,
      localeCode: 'en',
    ).loadPublishedRecipes();
    final sanma = en.singleWhere((r) => r.id == 'recipe_000080');
    expect(sanma.steps.firstWhere((s) => s.id == 'step_2').text,
        contains('Score the skin'));
    final tofu = en.singleWhere((r) => r.id == 'recipe_000136');
    expect(tofu.steps.firstWhere((s) => s.id == 'step_6').text,
        contains('tofu skewers'));

    final de = await VersionedRecipeCatalogRepository(
      source: source,
      localeCode: 'de',
    ).loadPublishedRecipes();
    final germanSanma = de.singleWhere((r) => r.id == 'recipe_000080');
    expect(germanSanma.ingredients
        .firstWhere((i) => i.id == 'fettine_di_limone_o_sudachi').name,
        contains('Sudachischeiben'));
  });
}
