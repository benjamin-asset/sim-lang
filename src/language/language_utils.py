import importlib


def import_module(*args):
    if len(args) == 1:
        return importlib.import_module(args[0])
    return importlib.import_module(".".join(args))
    # return getattr(module, args[-1])
