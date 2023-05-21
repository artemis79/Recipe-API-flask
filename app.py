#!/usr/bin/env python
# encoding: utf-8
from linguistic import normalizer
import json
from flask import Flask, jsonify, request
from data import Records

meals = []
normalizerAgent = normalizer.Normalizer()
with open('meals.json', 'r', encoding='utf-8') as f:
    meals = json.loads(f.read())

app = Flask(__name__)


@app.route('/title', methods=['GET'])
def title_record():
    title = request.args.get('title')
    title = normalizerAgent.normalize_text(title)

    if title:
        meal = Records.getRecipeByName(title, meals)
        if meal:
            return jsonify(meal)

        return jsonify({'error': 'data not found'})


@app.route('/ingredients', methods=['GET'])
def ingredients_records():
    ingredients = request.args.get('ingredients').split(',')
    ingredients = [normalizerAgent.normalize_text(ingredient) for ingredient in ingredients]

    with open('meals.json', 'r', encoding='utf-8') as f:
        data = f.read()
        meals = json.loads(data)

    if ingredients:
        meal = Records.getRcipeByIngredient(ingredients, meals)
        if meal:
            return jsonify(meal)

    return jsonify({'error': 'data not found'})


app.run()