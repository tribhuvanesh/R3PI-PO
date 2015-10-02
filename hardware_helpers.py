#!flask/bin/python
import json

def get_oven_temperature():
    """Get oven temperature (celsius) through hardware magic

    @return: float
    """
    return 0.0

def get_oven_state():
    """Get state of oven

    @return: One of ["on", "off", "error"]
    """
    return "error"
