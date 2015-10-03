#!flask/bin/python
import json
import os
import urllib2
import httplib2 as http
import requests

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from flask import Flask, jsonify
from creds import bigOvenAPIkey

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
    """
    1. Get listing of files in the directory
    2. Make array of integers with the names of the files
    """

    dirListing = os.listdir("recipeJSONs/")
    lst = []
    tempName = []

    for item in dirListing:
        if ".json" in item:
            tempName = os.path.splitext(item)[0]
            lst.append(int(tempName))

    response = json.dumps({'response' : lst})
    return response
    #return jsonify({'list': recipe_blob_dct.keys()})


def get_recipe_info(recipe_id):
    """Information about the recipe

    @type recipe_id: number
    @return: a JSON object
    """

    """
    1. Get list of files
    2. If recipe_id present in list, get the contents of the files
    3. Else, make API call to get the JSON data from bigOven
    4. jsonify the data and return
    """

    dct = json.loads(get_recipe_ids())
    lst = dct['response']
    if recipe_id not in lst:
        url_path = "http://api.bigoven.com/recipe/" + str(recipe_id) + "?api_key=" + bigOvenAPIkey
        headers = {'content-type': 'application/json'}
        req = requests.get(url_path, headers=headers)
        content = req.content
        recipe_info_str = json.loads(content)
        response = recipe_info_str
    else:
        json_fname = "%d.json" % recipe_id
        json_path = os.path.join("recipeJSONs",  json_fname)
        recipe_info_str = open(json_path).read()
        response = recipe_info_str
    return response

def main():
    print get_recipe_info(158905)


if __name__ == '__main__':
    main()
