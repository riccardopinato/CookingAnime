import 'package:animekitchen/features/recipes/domain/recipe.dart';
import 'package:animekitchen/features/recipes/presentation/screens/cooking_mode_screen.dart';
import 'package:animekitchen/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _recipe = Recipe(
  id: 'recipe_ui_resume',
  contentVersion: 1,
  contentOrigin: RecipeContentOrigin.original,
  title: 'Riso di prova',
  animeSource: 'Test',
  prepMinutes: 5,
  cookMinutes: 10,
  servings: 2,
  difficulty: RecipeDifficulty.easy,
  ingredients: [
    RecipeIngredient(id: 'rice', name: 'Riso', quantity: 150, unit: 'g'),
  ],
  steps: [
    RecipeStep(id: 'wash', text: 'Lava il riso.'),
    RecipeStep(id: 'cook', text: 'Cuoci il riso.'),
  ],
);

Widget _app() => const MaterialApp(
  locale: Locale('it'),
  localizationsDelegates: [
    AppLocalizations.delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: AppLocalizations.supportedLocales,
  home: CookingModeScreen(recipe: _recipe, servings: 4),
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('cooking step and completion survive route recreation',
      (tester) async {
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();
    expect(find.text('Passaggio 1 / 2'), findsOneWidget);
    expect(find.text('Porzioni da preparare: 4'), findsOneWidget);

    await tester.tap(find.text('Segna come completato'));
    await tester.pumpAndSettle();
    expect(find.text('1 / 2'), findsOneWidget);
    await tester.tap(find.text('Successivo'));
    await tester.pumpAndSettle();
    expect(find.text('Passaggio 2 / 2'), findsOneWidget);

    // The ingredients accordion is below the fold on a phone viewport.
    await tester.scrollUntilVisible(
      find.text('Ingredienti'), 240,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Ingredienti'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('300 g Riso'), 150,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('300 g Riso'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();
    expect(find.text('Passaggio 2 / 2'), findsOneWidget);
    expect(find.text('1 / 2'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('stale step ids do not corrupt restored cooking session',
      (tester) async {
    SharedPreferences.setMockInitialValues({
      'cooking_progress_v1_recipe_ui_resume':
          '{"stepId":"deleted","completedStepIds":["wash","unknown"]}',
    });
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();
    expect(find.text('Passaggio 1 / 2'), findsOneWidget);
    expect(find.text('1 / 2'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
