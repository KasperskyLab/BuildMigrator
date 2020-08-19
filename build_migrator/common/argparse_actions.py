import argparse


# Custom argparse Action.
# Allows setting one 'dest' from multiple arguments
class SetDestOnce(argparse.Action):
    def __init__(self, *args, **kwargs):
        super(SetDestOnce, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        found = getattr(namespace, self.dest, None)
        if found is None:
            setattr(namespace, self.dest, values)


# Custom argparse Action
# TODO: use for all arguments with nargs
class Extend(argparse.Action):
    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        attr_value = getattr(namespace, self.dest, None) or []
        attr_value.extend(values)
        setattr(namespace, self.dest, attr_value)
