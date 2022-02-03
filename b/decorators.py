# ======================================================================================================================
#        File:  decorators.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Function decorators used to connect b with Mercurial."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
from b import exceptions




# ======================================================================================================================
# Helpers
# ----------------------------------------------------------------------------------------------------------------------
def simple_decorator(decorator):
    """[Decorator-decorator pattern](https://wiki.python.org/moin/PythonDecoratorLibrary)."""

    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g

    return new_decorator




# ======================================================================================================================
# Decorator Classes
# ----------------------------------------------------------------------------------------------------------------------
class ValidOpts:
    """A decorator class that allow the valid options for a decorator to be provided."""

    def __init__(self, *valid_opts):
        self.valid_opts = set(valid_opts)

    def __call__(self, f):
        def non_default(key, value):
            if key == 'owner':
                return value != '*'
            return value

        def d(that, args, opts):
            invalid_opts = [o for o in opts
                            if non_default(o, opts[o])
                            and o not in self.valid_opts]
            if invalid_opts:
                raise exceptions.InvalidCommand("--%s is not a supported flag for this command" % invalid_opts[0])
            return f(that, args, opts)

        # TODO have @simple_decorator support decorator classes
        d.__name__ = f.__name__
        d.__doc__ = f.__doc__
        d.__dict__.update(f.__dict__)
        return d




# ======================================================================================================================
# Decorator Functions
# ----------------------------------------------------------------------------------------------------------------------
@simple_decorator
def zero_args(f):
    def d(self, args, opts):
        if args:
            raise exceptions.InvalidCommand("Expected zero arguments, got '%s'" % ' '.join(args))
        return f(self, opts)

    return d


# ----------------------------------------------------------------------------------------------------------------------
@simple_decorator
def prefix_arg(f):
    def d(self, args, opts):
        if len(args) < 1:
            raise exceptions.RequiresPrefix()
        elif len(args) > 1:
            raise exceptions.InvalidCommand("Unexpected arguments: %s" % ' '.join(args[1:]))
        else:
            return f(self, args[0], opts)

    return d


# ----------------------------------------------------------------------------------------------------------------------
@simple_decorator
def prefix_plus_args(f):
    def d(self, args, opts):
        if len(args) < 1:
            raise exceptions.RequiresPrefix()
        return f(self, args[0], args[1:], opts)

    return d




# End of File
