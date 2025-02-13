class Allergen:
    def __init__(self, symbol, full):
        self.symbol = symbol
        self.full = full

    def __str__(self):
        return self.symbol