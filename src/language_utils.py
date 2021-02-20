def import_class(*args):
    if len(args) == 1:
        return __import__(args[0])
    module = __import__('.'.join(args[:-1]))
    for arg in args[1: -1]:
        module = getattr(module, arg)
    return getattr(module, args[-1])
