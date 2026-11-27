class ShoppingItem {
  const ShoppingItem({
    required this.id,
    required this.name,
    required this.recipeSource,
    this.quantity,
    this.unit,
    this.isBought = false,
  });

  final String id;
  final String name;
  final String recipeSource;
  final double? quantity;
  final String? unit;
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
    bool? isBought,
  }) {
    return ShoppingItem(
      id: id ?? this.id,
      name: name ?? this.name,
      recipeSource: recipeSource ?? this.recipeSource,
      quantity: quantity ?? this.quantity,
      unit: unit ?? this.unit,
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
      };

  factory ShoppingItem.fromJson(Map<String, dynamic> json) {
    return ShoppingItem(
      id: json['id'] as String,
      name: json['name'] as String,
      recipeSource: json['recipeSource'] as String,
      quantity: (json['quantity'] as num?)?.toDouble(),
      unit: json['unit'] as String?,
      isBought: json['isBought'] as bool? ?? false,
    );
  }
}
