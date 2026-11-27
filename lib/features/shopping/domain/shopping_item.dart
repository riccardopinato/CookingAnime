class ShoppingItem {
  const ShoppingItem({
    required this.id,
    required this.name,
    required this.recipeSource,
    this.quantity,
    this.unit,
    this.category = 'other',
    this.isBought = false,
  });

  final String id;
  final String name;
  final String recipeSource;
  final double? quantity;
  final String? unit;
  final String category;
  final bool isBought;

  String get displayText {
    if (quantity == null) return name;
    final value = quantity! == quantity!.roundToDouble()
        ? quantity!.toInt().toString()
        : quantity!.toStringAsFixed(2).replaceFirst(RegExp(r'0+$'), '').replaceFirst(RegExp(r'\.$'), '');
    return [value, if (unit != null && unit!.isNotEmpty) unit!, name].join(' ');
  }

  ShoppingItem copyWith({
    String? id,
    String? name,
    String? recipeSource,
    double? quantity,
    String? unit,
    String? category,
    bool? isBought,
  }) {
    return ShoppingItem(
      id: id ?? this.id,
      name: name ?? this.name,
      recipeSource: recipeSource ?? this.recipeSource,
      quantity: quantity ?? this.quantity,
      unit: unit ?? this.unit,
      category: category ?? this.category,
      isBought: isBought ?? this.isBought,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'recipeSource': recipeSource,
        'isBought': isBought,
        if (quantity != null) 'quantity': quantity,
        if (unit != null) 'unit': unit,
        'category': category,
      };

  factory ShoppingItem.fromJson(Map<String, dynamic> json) {
    return ShoppingItem(
      id: json['id'] as String,
      name: json['name'] as String,
      recipeSource: json['recipeSource'] as String,
      quantity: (json['quantity'] as num?)?.toDouble(),
      unit: json['unit'] as String?,
      category: json['category'] as String? ?? 'other',
      isBought: json['isBought'] as bool? ?? false,
    );
  }
}

String shoppingCategoryFromIngredientId(String canonicalId) {
  final id = canonicalId.toLowerCase();
  // Stable Italian canonical ingredient IDs avoid locale-dependent categorisation.
  // Ambiguous compounds remain 'other'; users can move items between groups.
  if (RegExp(r'(^|_)pollo($|_)|maiale|manzo|gamber|salmone|tonno|uov[oa]|pesce|anatra|granchio|vongol|calamar|buri|tofu|carne_macinat').hasMatch(id)) {
    return 'protein';
  }
  if (RegExp(r'latte|burro|panna|formagg|mozzarella|yogurt|ricotta').hasMatch(id)) {
    return 'dairy';
  }
  if (RegExp(r'cipoll|carot|cetriol|pomodor|daikon|fungh|patat|cavol|zenzero|aglio|spinac|porro|melanzan|zucchin|fragol|banana|limon|yuzu|mela|peperon|verdura|lattuga').hasMatch(id)) {
    return 'produce';
  }
  if (RegExp(r'riso|farina|pasta|noodle|udon|soba|pane|olio|zucchero|sale|soia|miso|mirin|dashi|miele|sesamo|katsuobushi|anko|panko|amido').hasMatch(id)) {
    return 'pantry';
  }
  return 'other';
}
