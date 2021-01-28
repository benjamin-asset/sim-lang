def import_class(*args):
    module = __import__(args[0])
    for arg in args[1: -1]:
        module = getattr(module, arg)
    return getattr(module, args[-1])
