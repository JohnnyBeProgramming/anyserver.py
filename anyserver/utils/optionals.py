
from importlib import import_module


class OptionalModule:
    _mod = None
    _name = None

    def __init__(self, name, imports=[]):
        try:
            # Try and load the module and the imports
            self._name = name
            self._mod = self.module()
            for ident in imports:
                setattr(self, ident, self.imports(ident))
        except Exception:
            pass  # Failed to load the module and/or some props

    def imports(self, class_name): return getattr(self.module(), class_name)

    def found(self): return not self._mod == None

    def module(self):
        try:
            name = self._name
            self._mod = self._mod if self._mod else import_module(name)
            return self._mod
        except ImportError:
            raise Exception(f"""
# You are trying to use the '{name}' python package dependency. 
# This dependency was not found, and is not currently installed.
# To install `{name}`, run the following command:

> pip3 install -r requirements.txt {name}

WARNING: Flask python package not found. Aborting!
""")

    def hasBase(self, obj, class_name):
        def all_base_classes(type):
            res = [type.__name__]
            for cls in (cls for cls in type.__bases__ if not cls.__name__ == "object"):
                res = res + all_base_classes(cls)
            return res

        return class_name in all_base_classes(obj.__class__)
