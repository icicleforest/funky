# Python imports
import operator
from functools import wraps


# Constants
LIST_TYPES = (list, tuple, set)


def first(iterable, default=None):
    if not iterable:
        # Empty iterator (list)
        return default
    return iterable[0]


def rest(iterable):
    return iterable[1:]


def last(iterable):
    return iterable[-1]


def get(iterable, index, default=None):
    try:
        return iterable[index]
    except (IndexError, KeyError):
        return default


def next(iterable, value, n=1, default=None):
    if value in iterable:
        index = iterable.index(value)
        return get(iterable, index + n, default=default)
    return default


def prev(*args, **kwargs):
    kwargs['n'] = kwargs.get('n', 1) * -1
    return next(*args, **kwargs)


def chainable(method):
    @wraps(method)
    def f(self, *args, **kwargs):
        f(self, *args, **kwargs)
        return self
    f.is_chainable = True
    return f


def list_from_args(args):
    """
    Flatten list of args
    So as to accept either an array
    Or as many arguments
    For example:
    func(['x', 'y'])
    func('x', 'y')
    """
    # Empty args
    if not args:
        return []

    # Get argument type
    arg_type = type(args[0])
    is_list = arg_type in LIST_TYPES

    # Check that the arguments are uniforn (of same type)
    same_type = all([
        isinstance(arg, arg_type)
        for arg in args
    ])

    if not same_type:
        raise Exception('Expected uniform arguments of same type !')

    # Flatten iterables
    # ['x', 'y'], ...
    if is_list:
        args_lists = map(list, args)
        flattened_args = sum(args_lists, [])
        return flattened_args
    # Flatten set
    # 'x', 'y'
    return list(args)


# Decorator for list_from_args
def arglist(func):
    @wraps(func)
    def f(*args, **kwargs):
        args_list = list_from_args(args)
        return func(args_list, **kwargs)
    return f


# Decorator for methods
def arglist_method(func):
    @wraps(func)
    def f(self, *args, **kwargs):
        args_list = list_from_args(args)
        return func(self, args_list, **kwargs)
    return f


class Memoizer(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def cache_key(self, args, kwargs):
        sorted_kwargs = kwargs.items()
        sorted_kwargs.sort()
        cache_key = hash(args + tuple(sorted_kwargs))
        return cache_key

    def has_cache(self, cache_key):
        return cache_key in self.cache

    def get_cache(self, cache_key):
        return self.cache[cache_key]

    def set_cache(self, cache_key, value):
        self.cache[cache_key] = value

    def clear(self):
        self.cache = {}

    def __call__(self, *args, **kwargs):
        cache_key = self.cache_key(args, kwargs)
        if not self.has_cache(cache_key):
            value = self.func(*args, **kwargs)
            self.set_cache(cache_key, value)
        return self.get_cache(cache_key)


# Cache calls
def memoize(func):
    """Cache a functions output for a given set of arguments"""
    return wraps(func)(Memoizer(func))


def transform(transform_func):
    """Apply a transformation to a functions return value"""
    def decorator(func):
        @wraps(func)
        def f(*args, **kwargs):
            return transform_func(
                func(*args, **kwargs)
            )
        return f
    return decorator


# Useful functions
negate = transform(operator.not_)


def true_only(iterable):
    return filter(bool, iterable)


def first_true(iterable):
    true_values = true_only(iterable)
    if true_values:
        return true_values[0]
    return None