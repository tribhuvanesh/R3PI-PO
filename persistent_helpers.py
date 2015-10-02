#!flask/bin/python
import json

def get_recipe_ids():
    """Returns a list of valid recipe IDS

    @return: list of recipe IDs, where recipe ID is a number
    """
    return []


def get_recipe_info(recipe_id):
    """Information about the recipe

    @type recipe_id: number
    @return: a JSON object
    """
    return json.dumps("{}")
