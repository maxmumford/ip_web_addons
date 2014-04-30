def isnumeric(val):
    """ Tests if a value is numeric and returns True or False accordingly """
    if isinstance(val, (int, float)):
        return True
    elif isinstance(val, (str, unicode)):
        try:
            float(val)
            return True
        except ValueError:
            return False
