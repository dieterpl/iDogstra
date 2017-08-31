import time
import warnings
import functools


def current_time_millis():
    """ Returns the current system time in milliseconds """
    return int(round(time.time() * 1000))


def current_time_micros():
    """ Returns the current system time in microseconds """
    return int(round(time.time() * 1E6))


def overrides(interface_class):
    """ This method can be used as an @override annotation.
    Inspired by http://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method

    Example usage:

    @override(superclass)
    def somemethod():
    """

    def overrider(method):
        assert (method.__name__ in dir(interface_class))
        return method

    return overrider


def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)

    return new_func


def get_class_name(obj):
    """
    Returns the name of the class of the given object
    :param obj: the object whose class is to be determined
    :return: the name of the class as a string
    """
    return obj.__class__.__name__

