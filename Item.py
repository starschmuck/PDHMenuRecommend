class Item:
    def __init__(self, name, allergens, meal_type):
        self.name = name
        self.allergens = allergens
        self.meal_type = meal_type

    def __str__(self):
        result = self.meal_type + " " + self.name + " ["

        for allergen in self.allergens:
            result += allergen.symbol + " "

        result += "]"

        return result
