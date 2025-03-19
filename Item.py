class Item:
    def __init__(self, name, allergens, meal_type):
        while name and name[-1].isupper():
            name = name[:-1]

        if ':' in name :
            name = name.split(':')[0]

        self.name = name.title()
        self.allergens = allergens
        self.meal_type = meal_type

    def __str__(self):
        allergens_str = ', '.join([str(allergen) for allergen in self.allergens])

        return f'{self.name} [{allergens_str}]'

'''
    def __str__(self):
        result = self.meal_type + " " + self.name + " ["

        for allergen in self.allergens:
            result += allergen.symbol + " "

        result += "]"

        return result
'''
