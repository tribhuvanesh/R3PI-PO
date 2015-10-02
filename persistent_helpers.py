#!flask/bin/python
import json
from flask import Flask, jsonify

recipe_blob_dct = {
    1 : {
        'id': 1,
        'title': 'Chicken Alfredo',
        'description': 'Chicken & Pasta & Cream.',
        'img': 'https://c1.staticflickr.com/3/2504/3874012191_48ec021023.jpg'
    },
    2 : {
        'id': 2,
        'title': 'Lasagna',
        'description': 'Garfield\'s Favorite.',
        'img': 'https://upload.wikimedia.org/wikipedia/commons/6/6b/Lasagna_(1).jpg'
    },
    3 : {
        'id': 3,
        'title': 'Pizza',
        'description': 'Best served cold, just like revenge.',
        'img': 'https://upload.wikimedia.org/wikipedia/commons/9/95/Pizza_with_various_toppings.jpg'
    }
}


def get_recipe_ids():
    """Returns a list of valid recipe IDS

    @return: a JSON object - list of recipe IDs, where recipe ID is a number
    """
    return jsonify({'list': recipe_blob_dct.keys()})


def get_recipe_info(recipe_id):
    """Information about the recipe

    @type recipe_id: number
    @return: a JSON object
    """
    if recipe_id not in recipe_blob_dct.keys():
        return None
    else:
        return jsonify(recipe_blob_dct[recipe_id])
