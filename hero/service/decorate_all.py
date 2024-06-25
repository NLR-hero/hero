def decorate_all(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)) and not attr.startswith('__'):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate