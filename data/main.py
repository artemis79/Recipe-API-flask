import json
from linguistic import normalizer

normalizerAgent = normalizer.Normalizer()

def normalizeTitle(title):
    return normalizerAgent.normalize_text(title)


def normalizeIngredients(ingredients):
    ingredients = ingredients.split(',')
    normalizedIngredients = []
    for ingredient in ingredients:
        ingredient.strip()
        normalizedIngredients.append(normalizerAgent.normalize_text(ingredient))

    return normalizedIngredients


if __name__ == '__main__':
    meals = []
    with open('digi-apis.json', 'r', encoding='utf-8') as handle:
        recipes = [json.loads(line) for line in handle]

    print(len(recipes))
    for recipe in recipes:
        if 'ingredients' not in recipe.keys():
            continue

        title = recipe['title']
        ingredients = recipe['ingredients']

        title = normalizeTitle(title)
        ingredients = normalizeIngredients(ingredients)

        if title and 'filteredContent' in recipe.keys():
            meals.append({'title': title, 'ingredients': ingredients, 'recipe': recipe['filteredContent']})


    with open('../meals.json', 'w', encoding='utf-8') as f:
        json.dump(meals, f, ensure_ascii=False)
