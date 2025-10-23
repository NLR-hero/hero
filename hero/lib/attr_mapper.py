from collections.abc import MutableMapping


def _to_attr(value):
    if isinstance(value, dict):
        return HeroObject(value)
    if isinstance(value, list):
        return [_to_attr(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_to_attr(v) for v in value)
    return value


class HeroObject(MutableMapping):
    """
    Mapping that supports attribute-style access and recursive wrapping.
    Example:
        run = HeroObject({"info": {"run_id": "123"}, "data": {"tags": [{"key": "k","value": "v"}]}})
        run.info.run_id -> "123"
        run["info"]["run_id"] -> "123"
    """

    __slots__ = ("_store",)

    def __init__(self, data=None, **kwargs):
        object.__setattr__(self, "_store", {})
        if data:
            for k, v in data.items():
                self._store[k] = _to_attr(v)
        for k, v in kwargs.items():
            self._store[k] = _to_attr(v)

    # Mapping protocol
    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = _to_attr(value)

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    # Attribute access
    def __getattr__(self, name):
        try:
            return self._store[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, name, value):
        # keep internal slot private; everything else goes in the mapping
        if name == "_store":
            object.__setattr__(self, name, value)
        else:
            self._store[name] = _to_attr(value)

    def __delattr__(self, name):
        try:
            del self._store[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def to_dict(self):
        def _to_plain(v):
            if isinstance(v, HeroObject):
                return {k: _to_plain(v[k]) for k in v}
            if isinstance(v, list):
                return [_to_plain(i) for i in v]
            if isinstance(v, tuple):
                return tuple(_to_plain(i) for i in v)
            return v

        return {k: _to_plain(v) for k, v in self._store.items()}

    def __repr__(self):
        return f"HeroObject({self.to_dict()!r})"
