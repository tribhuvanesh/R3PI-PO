#!flask/bin/python
__author__ = 'tribhu'

import json

from flask import Flask, jsonify, abort, make_response, url_for, request
from flask.ext.cors import CORS, cross_origin

import requests

from persistent_helpers import get_recipe_info, get_recipe_short_descriptions
from parse_helper import route_command

app = Flask(__name__, static_url_path='')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/recipes/api/v1.0/recipes', methods=['GET'])
@cross_origin()
def get_recipes():
    """
    @return: a JSON RecipeList object
    """
    return get_recipe_short_descriptions()


@app.route('/recipes/api/v1.0/recipe_info', methods=['GET'])
@cross_origin()
def get_recipes_info():
    """
    @return: a JSON RecipeList object
    """
    recipe_id =  int(request.args.get('recipe_id'))
    return get_recipe_info(recipe_id)


@app.route('/recipes/api/v1.0/ask', methods=['GET'])
@cross_origin()
def get_recipe():
    """get_recipe requires two GET parameters:
    a. recipe_id - the recipe ID number
    b. text - the (sepeech-converted) textual command

    @return: a JSON Recipe object
    """
    recipe_id =  int(request.args.get('recipe_id'))
    text = request.args.get('text')
    response_json = route_command(text, recipe_id)

    if response_json == None:
        abort(404)
    return response_json

@app.route('/tokens/api/v1.0/watson_token', methods=['GET'])
@cross_origin()
def get_watson_token():
    """
    @return: a JSON RecipeList object
    """
    from creds import watson_username, watson_password
    service_url = 'https://stream.watsonplatform.net/text-to-speech/api'
    r = requests.get('https://stream.watsonplatform.net/authorization/api/v1/token?url=%s' % service_url,
                     auth=(watson_username, watson_password))
    return json.dumps({'response': r.text})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def make_public_task(recipe):
    new_recipe = {}
    for field in recipe:
        if field == 'id':
            new_recipe['uri'] = url_for('get_recipe', recipe_id=recipe['id'], _external=True)
        else:
            new_recipe[field] = recipe[field]
    return new_recipe


if __name__ == '__main__':
    app.run(debug=True)
