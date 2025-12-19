import inspect
import json
from typing import get_type_hints

def find_methods_with_wrapper(cls, wrapper_name):
    wrapped_method_names = []

    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if getattr(method, wrapper_name, False):
            wrapped_method_names.append(name)

    return wrapped_method_names



def analyze_command_methods_in_class(cls, wrapper_name):
    methods_info = {}

    def _type_to_str(tp):
        try:
            if tp is inspect._empty:
                return "unknown"
            if hasattr(tp, "__name__"):
                return tp.__name__
            return str(tp)
        except Exception:
            return repr(tp)

    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if getattr(method, wrapper_name, False):
            signature = inspect.signature(method)
            try:
                type_hints = get_type_hints(method, globalns=getattr(method, "__globals__", {}), localns=vars(cls))
            except Exception:
                type_hints = getattr(method, "__annotations__", {}).copy()

            params = {}
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue
                ann = type_hints.get(param_name, param.annotation)
                ann_str = _type_to_str(ann)
                default = None
                if param.default is not inspect._empty:
                    default = repr(param.default)
                params[param_name] = {
                    "type": ann_str,
                    "default": default,
                }

            return_ann = type_hints.get("return", signature.return_annotation)
            return_type = _type_to_str(return_ann)

            methods_info[name] = {
                "parameters": params,
                "return_type": return_type
            }

    return json.dumps(methods_info, indent=4)



