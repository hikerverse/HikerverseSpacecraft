import abc
import inspect
from functools import wraps
from typing import Optional


def command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func.command = True
        return func(*args, **kwargs)
    wrapper.command = True
    return wrapper

class Commandable(abc.ABC):

    def execute(self, **args):
        try:
            cmd = args['cmd']
            bar = getattr(self, cmd)
        except AttributeError:
            return None
        args = args['args']
        if len(args) > 0:
            if isinstance(args, list):
                return bar(*args)
            else:
                return bar(**args)
        else:
            return bar()


    def get_method(self, method_name: str) -> Optional[callable]:
        try:
            bar = getattr(self, method_name)
            return bar
        except AttributeError:
            return None

    def get_docstring(self, obj) -> Optional[str]:
        """
        Return the normalized docstring for a function/method/class or None.
        Uses inspect.getdoc which also honors inheritance and cleans indentation.
        """
        method_ = self.get_method(obj)
        return inspect.getdoc(method_)

    def get_class_docstring(self, class_name: str) -> Optional[str]:
        """
        Return the normalized docstring for a class attribute on this object or None.
        If the attribute is an instance, its class's docstring is returned.
        """
        try:
            attr = getattr(self, class_name)
        except AttributeError:
            return None
        target = attr if inspect.isclass(attr) else (getattr(attr, "__class__", None))
        if target is None:
            return None
        return inspect.getdoc(target)
