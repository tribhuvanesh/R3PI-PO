#!flask/bin/python
import re, json
from flask import jsonify

from persistent_helpers import get_recipe_info

def route_command(recipe_id, text):
    """Decide if command is:
    a. Generic:
        - what is step <X>?
        - how much of <X> is required?
    b. Hardware related
        - what's the temperature of the oven?
        - is the oven ready?
    Route command accordingly

    @type recipe_id: number
    @type text: Request as String
    @return: Respose as String
    """
    text = text.lower()

    tokens = map(lambda x: x.strip().trim(), x.split())
    tokens = set(tokens)

    hardware_kw = set(['temperature', 'oven', 'owen'])

    if len(tokens & hardware_kw) > 0:
        response = exec_hardware_command(text)
    else:
        response = exec_generic_command(recipe_id, text)

    if response is None:
        # TODO Handle elegantly
        return None

    return response


def exec_generic_command(recipe_id, text):
    """Execute generic command:
    A. what is step <X>?
    B. how much of <X> is required?

    @type recipe_id: number
    @type text: Request as String
    @return: Respose as String
    """
    # Keywords for A and B
    step_kw = ['step']
    ing_qty_kw = ['how much', 'required', 'needed', 'need', 'how many']

    # Check what kind of a question it is
    step_match = sum([kw in text for kw in step_kw])
    ing_quantity_match = sum([kw in text for kw in ing_qty_kw])

    if step_match == 0 and ing_quantity_match == 0:
        return None
    elif step_match > 0 :
        respond_to_step(text, recipe_id)
    elif ing_quantity_match > 0:
        respond_to_ing_qty(text, recipe_id)
    else:
        return None


def exec_hardware_command(text):
    """Execute hardware-related command
    A. what is the temperature of the oven?
    B. is the oven ready?

    @type text: Request as String
    @return: Respose as String
    """
    # Keywords for A and B
    temp_kw = ['temperature', ]
    ready_kw = ['ready', ]

    # Check what kind of a question it is
    temp_match = sum([kw in text for kw in temp_kw])
    ready_match = sum([kw in text for kw in ready_kw])

    if temp_match == 0 and ready_kw == 0:
        return None
    elif temp_match > 0 :
        respond_to_step(text)
    elif ing_quantity_match > 0:
        ready_match(text)
    else:
        return None


def respond_to_step(text, recipe_id):
    """Respond to:
    'what is step <X>?'
    """
    # Which step is required?
    match = re.search('step (?P<step_num>\d+)', text)
    step_num = int(match.group('step_num'))

    # What are the steps in the recipe?
    recipe_info_str = get_recipe_info(recipe_id)
    recipe_info = json.loads(recipe_info_str)
    instructions = recipe_info["Instructions"].split('. ')
    num_instructions = len(instructions)

    # Construct response
    if step_num > num_instructions:
        response = "Step %d does not exist. There are %d steps." % (step_num, num_instructions)
    else:
        response = num_instructions[step_num-1]

    return jsonify({'response' : response})


def respond_to_ing_qty(text, recipe_id):
    """Respond to:
    'how much of <X> is required?'
    """
    # What is the ingredient?
    # Detect by simple pattern matching
    match = re.search('of (?P<ing>\w+) is', text)
    ingredient = match.group('ing')

    # What are the ingredients in this recipe?
    recipe_info_str = get_recipe_info(recipe_id)
    recipe_info = json.loads(recipe_info_str)
    # List of 'ingredient' dicts
    ingredients = recipe_info["Ingredients"]
    # Create a dict {ingredient_name -> quantity}
    ing_tuples = [(ing['Name'].lower(), int(ing['Quantity']), ing['Unit'].lower())]
    ing_dct = {name : quantity for name, quantity, unit in ing_tuples}

    # Construct a response
    if ingredient not in ing_dct.keys():
        response = "%s is not necessary" % ingredient
    else:
        response = "%d required" % ing_dct[ingredient]

    return jsonify({'response' : response})


def respond_to_temp(text):
    # What is the temperature?

    # Construct response
    pass


def respond_to_ready(text):
    # What is the state?

    # Construct response
    pass
