#!flask/bin/python
import re, json
from flask import jsonify

import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

from persistent_helpers import get_recipe_info

stemmer = SnowballStemmer("english")
stop = stopwords.words('english')

def route_command(text, recipe_id):
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
    recipe_id = int(recipe_id)

    tokens = map(lambda x: x.strip(), text.split())
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
    C. where do i use <X>?
    D. how many calories does this contain?
    E. how long do i <X>?

    @type recipe_id: number
    @type text: Request as String
    @return: Respose as String
    """
    # Keywords for A
    step_kw = ['step']
    # Keywords for B
    ing_qty_kw = ['how much', 'required', 'needed', 'need', 'how many']
    # Keywords for C
    step_use_kw = ['where', 'do i use']
    # Keywords for D
    cal_kw = ['calories']
    # Keywords for E
    duration_kw = ['how long do i']

    # Check what kind of a question it is
    step_match = sum([kw in text for kw in step_kw])
    ing_quantity_match = sum([kw in text for kw in ing_qty_kw])
    step_use_match = sum([kw in text for kw in step_use_kw])
    cal_match = sum([kw in text for kw in cal_kw])
    duration_match =  sum([kw in text for kw in duration_kw])

    if cal_match > 0:
        return respond_to_cal(text, recipe_id)
    elif duration_match > 0:
        return respond_to_duration(text, recipe_id)
    elif step_use_match > 0:
        return respond_to_step_use(text, recipe_id)
    elif step_match > 0 :
        return respond_to_step(text, recipe_id)
    elif ing_quantity_match > 0:
        return respond_to_ing_qty(text, recipe_id)
    else:
        print 'All routes failed'
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
        return respond_to_step(text)
    elif ing_quantity_match > 0:
        return ready_match(text)
    else:
        return None


def respond_to_step(text, recipe_id):
    """Respond to:
    'what is step <X>?'
    """
    # Which step is required?
    match = re.search('step[s]?\s+(number\s+)?(?P<step_num>\w+)', text)
    step_str = match.group('step_num')

    try:
        step_num = int(step_str)
    except ValueError:
        step_num = text2int(step_str)

    # What are the steps in the recipe?
    recipe_info_str = json.loads(get_recipe_info(recipe_id))
    recipe_info = recipe_info_str['response']
    raw_instructions = recipe_info["Instructions"].replace('\r', '').replace('\n', '')
    instructions = raw_instructions.split('. ')
    num_instructions = len(instructions)

    # Construct response
    if step_num > num_instructions:
        response = "Step %d does not exist. There are %d steps." % (step_num, num_instructions)
    else:
        response = instructions[step_num-1]

    return json.dumps({'response' : response})


def respond_to_ing_qty(text, recipe_id):
    """Respond to:
    'how much <X> is required?'
    """
    # What is the ingredient?
    # Detect by simple pattern matching
    match = re.search('how (much|many) (?P<ing>[\w -]+)', text)
    query_ingredient = match.group('ing')

    # What are the ingredients in this recipe?
    recipe_info_str = json.loads(get_recipe_info(recipe_id))
    recipe_info = recipe_info_str['response']
    # List of 'ingredient' dicts
    ingredients = recipe_info["Ingredients"]
    # Create a dict {ingredient_name -> quantity}
    ing_dct = {}
    for ing in ingredients:
        name = ing['Name'].lower()
        quantity = ing['Quantity']
        units = ing.get('Unit', '')

        ing_dct[name] = (quantity, units)

    # What's the quantity required?
    # Clean up recipe tokens
    # a. tokenize the ingredients
    recipe_tokens = nltk.word_tokenize(query_ingredient)
    # b. stem the tokens
    recipe_tokens = set([stemmer.stem(token) for token in recipe_tokens])
    candidates = []
    for dct_ing in ing_dct:
        query_tokens = nltk.word_tokenize(dct_ing)
        query_tokens = set([stemmer.stem(token) for token in query_tokens])
        num_matches = len(recipe_tokens & query_tokens)
        if num_matches > 0:
            candidates += [(dct_ing, num_matches)]

    candidates = sorted(candidates, key=lambda x:-x[1])

    if len(candidates) == 0:
        response = "%s is not necessary" % query_ingredient
    #elif len(candidates) == 1:
    else:
        response = "%s %s required" % ing_dct[candidates[0][0]]
    #else:
    #    response = "Did you mean %s? %s %s required" % (candidates[0][0], ing_dct[candidates[0][0]][0], ing_dct[candidates[0][0]][1])

    return json.dumps({'response' : response})


def respond_to_duration(text, recipe_id):
    """Respond to
    how long do i <X>
    <X> can be "bake the cake", or whatever
    """
    # Detect <X> by simple pattern matching
    match = re.search('how long do i (?P<action>[\w\s -]+)', text)
    query_action = match.group('action')

    # Get tokens
    action_tokens = recipe_tokens = nltk.word_tokenize(query_action)
    action_tokens = set([stemmer.stem(token) for token in action_tokens])
    action_tokens = set([token for token in action_tokens if token not in stop])

    # Iterate over steps, find relevant steps, add with a score
    # What are the steps in the recipe?
    recipe_info_str = json.loads(get_recipe_info(recipe_id))
    recipe_info = recipe_info_str['response']
    raw_instructions = recipe_info["Instructions"].replace('\r', '').replace('\n', '')
    instructions = raw_instructions.split('.')
    num_instructions = len(instructions)

    # Compare each instruction with a 'duration' keyword
    dur_kw = set(['minutes', 'minut', 'minute', 'mins', 'min',
    'seconds', 'second', 'secs', 'sec'])

    candidates = []

    for idx, instruc in enumerate(instructions):
        instruc_tokens = nltk.word_tokenize(instruc)
        instruc_tokens = [stemmer.stem(token) for token in instruc_tokens]
        instruc_tokens = set([token for token in instruc_tokens if token not in stop])

        is_duration_instruc = len(instruc_tokens & dur_kw) > 0

        if is_duration_instruc:
            # Calculate score
            num_matches = len(instruc_tokens & action_tokens)
            candidates += [(instruc, num_matches), ]

    candidates = sorted(candidates, key=lambda x: -x[1])

    if len(candidates) == 0:
        response = 'error'
    else:
        most_relev_instruc = candidates[0][0]
        response = most_relev_instruc

    return json.dumps({'response' : response})


def respond_to_step_use(text, recipe_id):
    """Respond to
    where do i use <X>?
    """
    # What is the ingredient?
    # Detect by simple pattern matching
    match = re.search('where do i use (?P<ing>[\w -]+)', text)
    query_ingredient = match.group('ing')

    # Clean up recipe tokens
    # a. tokenize the ingredients
    recipe_tokens = nltk.word_tokenize(query_ingredient)
    # b. stem the tokens
    recipe_tokens = set([stemmer.stem(token) for token in recipe_tokens])
    # c. remove stop words
    recipe_tokens = set([token for token in recipe_tokens if token not in stop])

    # Iterate over steps, find relevant steps, add with a score
    # What are the steps in the recipe?
    recipe_info_str = json.loads(get_recipe_info(recipe_id))
    recipe_info = recipe_info_str['response']
    raw_instructions = recipe_info["Instructions"].replace('\r', '').replace('\n', '')
    instructions = raw_instructions.split('. ')
    num_instructions = len(instructions)

    candidates = []

    for idx, instruc in enumerate(instructions):
        instruc_tokens = nltk.word_tokenize(instruc)
        instruc_tokens = [stemmer.stem(token) for token in instruc_tokens]
        instruc_tokens = set([token for token in instruc_tokens if token not in stop])

        num_matches = len(instruc_tokens & recipe_tokens)
        step_num = idx + 1

        if num_matches > 0:
            candidates += [(instruc, step_num, num_matches), ]

    candidates = sorted(candidates, key=lambda x:x[1])

    if len(candidates) == 0:
        response = '%s not used in any step.' % query_ingredient
    elif len(candidates) == 1:
        instruc, step_num, num_matches = candidates[0]
        response = 'In step %d. %s' % (step_num, instruc)
    else:
        # Get list of steps where its used
        steps_used = [str(cand[1]) for cand in candidates]
        response = 'In steps ' + ', '.join(steps_used) + '. '
        for instruc, step_num, num_matches in candidates:
            response += 'In step %d. %s' % (step_num, instruc)

    return json.dumps({'response' : response})


def respond_to_cal(text, recipe_id):
    """Respond to
    how many calories does this contain
    """
    # Get Recipe
    recipe_info = json.loads(get_recipe_info(recipe_id))['response']
    calories = recipe_info.get("Calories", None)

    if calories is None:
        response = "Nutritional value unavailable."
    else:
        response = "This dish contains %s kilocalories" % calories

    return json.dumps({'response' : response})


def respond_to_temp(text):
    # What is the temperature?

    # Construct response
    pass


def respond_to_ready(text):
    # What is the state?

    # Construct response
    pass


def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def main():
    recipe_id = 608382
    # text = "what is step two"
    # print respond_to_ing_qty(text, recipe_id)
    # text = "what is step three"
    text = "how long do i parboil the red potatoes"
    print route_command(text, recipe_id)

if __name__ == '__main__':
    main()
