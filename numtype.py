# returns the type of the input item

def numtype(item):
    # add binary?
    try:
        int(item)
        return 'int'
    except ValueError:
        pass
    try:
        float(item)
        return 'float'
    except ValueError:
        pass
    try:
        complex(item)
        return 'complex'
    except ValueError:
        pass
    return 'str'
        