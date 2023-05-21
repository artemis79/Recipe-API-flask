import heapq
import operator
from parsivar import Normalizer
from parsivar import Tokenizer

normalizer = Normalizer()
tokenizer = Tokenizer()


def titleMaxFunc(p):
    return p[1]


def getRecipeByName(title, meals):
    scoredMeals = []
    userWords = set(tokenizer.tokenize_words(normalizer.normalize(title)))
    for meal in meals:
        titleWords = set(tokenizer.tokenize_words(normalizer.normalize(meal['title'])))
        nominator = userWords.intersection(titleWords)
        denominator = userWords.union(titleWords)
        similarity = len(nominator)/len(denominator)
        scoredMeals.append((meal, similarity))

    meals = heapq.nlargest(min(len(scoredMeals), 10), scoredMeals, key=titleMaxFunc)

    topMeals = []
    for meal in meals:
        topMeals.append(meal[0])

    # print(len(topMeals))
    return topMeals


def maxFunc(p):
    intersect = p[2]
    ingredients = p[0]['ingredients']
    userIngredients = p[1]

    if len(ingredients) == len(userIngredients) and len(ingredients) == intersect:
        return 1000

    return intersect * 10 - (len(ingredients) - intersect)


def getRcipeByIngredient(userIngredients, meals):
    sameIngredients = []

    for meal in meals:
        mealIngredients = meal['ingredients']
        jVal = "|".join(mealIngredients)
        intersect = 0
        for i in userIngredients:
            if i in jVal:
                intersect += 1

        if intersect != 0:
            sameIngredients.append([meal, userIngredients, intersect])


    if sameIngredients:
        matchRecipes = heapq.nlargest(min(len(sameIngredients), 5), sameIngredients, key=maxFunc)
        result = []
        for element in matchRecipes:
            result.append(element[0])
        return result

    return None