#!flask/bin/python
__author__ = 'tribhu'

from flask import Flask, jsonify, abort, make_response, url_for, request

app = Flask(__name__)

recipe_blob_list = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/recipes/api/v1.0/recipes', methods=['GET'])
def get_recipes():
    return jsonify({'recipes': [make_public_task(recipe_blob) for recipe_blob in recipe_blob_list]})


@app.route('/recipes/api/v1.0/ask', methods=['GET'])
def get_recipe():
    recipe_id =  int(request.args.get('recipe_id'))
    text = request.args.get('text')
    recipe_blob = [recipe_blob for recipe_blob in recipe_blob_list if recipe_blob['id'] == recipe_id]
    if len(recipe_blob) == 0:
        abort(404)
    return jsonify({'recipes': recipe_blob[0]})


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
