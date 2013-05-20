


def niceCurrencyString(f):
    def wrapper(*args, **kwargs):
        return number.comma3(f(*args, **kwargs))
    return wrapper