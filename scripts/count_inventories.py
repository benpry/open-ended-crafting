from src.constants import INGREDIENTS

for domain in INGREDIENTS.keys():
    ingredients = INGREDIENTS[domain]
    print(f"Domain: {domain}")
    print(f"Number of ingredients: {len(ingredients)}")
    print("\n")
