#!flask/bin/python

def route_command(recipe_id, text):
    """Decide if command is:
    a. Generic:
        - What's step <X>?
        - How much of <X> is required?
    b. Hardware related
        - What's the temperature of the oven?
        - Is the oven ready?
    Route command accordingly

    @type recipe_id: number
    @type text: Request as String
    @return: Respose as String
    """
    return None


def exec_generic_command(text):
    """Execute generic command

    @type text: Request as String
    @return: Respose as String
    """
    return None


def exec_hardware_command(text):
    """Execute hardware-related command

    @type text: Request as String
    @return: Respose as String
    """
    return None
