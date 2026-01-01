# python
import importlib
import inspect
import json
import pkgutil

from hikerservespacecraft.hull import Hull

from hikerservespacecraft.spacecraft import Spacecraft
from hikerservespacecraft.spacecraft_bus import SpacecraftBus, PowerBus
from hikerservespacecraft.spacecraft_constructor import get_initial_spacecraft


class SerializationError(Exception):
    """Custom exception for serialization errors."""
    pass


class DeserializationError(Exception):
    """Custom exception for deserialization errors."""
    pass



def serializesimon(obj, _seen=None, _depth=0, _max_depth=50):
    try:

        print(f"Serializing object of type {type(obj).__name__} at depth {_depth}")


        if _seen is None:
            _seen = set()

        # guard against too deep recursion
        if _depth > _max_depth:
            return {"__recursion__": True, "__repr__": repr(obj)}

        # primitives
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj

        oid = id(obj)
        if oid in _seen:
            return {"__recursion__": True, "__type__": type(obj).__name__, "__repr__": repr(obj)}

        # mark current object as seen
        _seen.add(oid)
        try:
            # containers
            if isinstance(obj, tuple):
                print("Serializing tuple")
                return {"__type__": "tuple", "items": [serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
            if isinstance(obj, list):
                print("Serializing list")
                return [serialize(i, _seen, _depth + 1, _max_depth) for i in obj]
            if isinstance(obj, set):
                print("Serializing set")
                return {"__type__": "set", "items": [serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
            if isinstance(obj, frozenset):
                print("Serializing frozenset")
                return {"__type__": "frozenset", "items": [serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
            if isinstance(obj, dict):
                print("Serializing dict")
                return {str(k): serialize(v, _seen, _depth + 1, _max_depth) for k, v in obj.items()}

            # custom objects: prefer instance attributes, handle __slots__
            if hasattr(obj, "__dict__") or hasattr(type(obj), "__slots__"):
                obj_type = type(obj)
                result = {"__type__": obj_type.__name__}

                # instance attributes
                try:
                    for k, v in vars(obj).items():
                        try:
                            result[k] = serialize(v, _seen, _depth + 1, _max_depth)
                        except SerializationError:
                            result[k] = repr(v)
                except TypeError as te:
                    print("TypeError during vars():", te)

                # __slots__ attributes
                slots = getattr(obj_type, "__slots__", ())
                if isinstance(slots, str):
                    slots = (slots,)
                for slot in slots:
                    if hasattr(obj, slot):
                        try:
                            result[slot] = serialize(getattr(obj, slot), _seen, _depth + 1, _max_depth)
                        except SerializationError:
                            print("SerializationError during __slots__ handling for slot:", slot)
                            result[slot] = repr(getattr(obj, slot))

                return result

            # fallback for non-serializable builtins / descriptors
            return repr(obj)
        finally:
            # unmark to allow other branches to serialize same object independently
            _seen.discard(oid)
    except Exception as e:
        print("Exception during serialization:", e)
        raise SerializationError(f"Error during serialization: {e}")

# cache payload classes so the dynamic scan runs only once per process
_PAYLOAD_CLASSES_CACHE = None

classes = {cls.__name__: cls for cls in [Spacecraft, Hull,
                                         SpacecraftBus, PowerBus]}

def _load_payload_classes():
    global _PAYLOAD_CLASSES_CACHE
    if _PAYLOAD_CLASSES_CACHE is not None:
        return _PAYLOAD_CLASSES_CACHE

    payload_classes = {}
    try:
        pkg_name = "hikerservespacecraft.payloads"
        pkg = importlib.import_module(pkg_name)
        for finder, modname, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            try:
                mod = importlib.import_module(modname)
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if getattr(obj, "__module__", "").startswith(pkg_name):
                        payload_classes.setdefault(name, obj)
            except Exception:
                continue
    except Exception:
        payload_classes = {}

    _PAYLOAD_CLASSES_CACHE = payload_classes
    return payload_classes



def deserialize2simon(data, format: str = "json"):

    if format == "json":
        data = json.loads(data)

    classes = {cls.__name__: cls for cls in [Spacecraft, Hull,
                                             SpacecraftBus, PowerBus]}

    # dynamically scan `hikerservespacecraft.payloads` for additional classes
    payload_classes = _load_payload_classes()

    d = 3
    classes = {**classes, **payload_classes}

    try:
        def handle_primitive(value, _):
            return value

        def handle_list(value, classes):
            return [deserialize2(item, classes) for item in value]

        def handle_set(value, classes):
            return set(deserialize2(item, classes) for item in value["items"])

        def handle_frozenset(value, classes):
            return frozenset(deserialize2(item, classes) for item in value["items"])

        def handle_tuple(value, classes):
            return tuple(deserialize2(item, classes) for item in value["items"])

        def handle_custom_class(value, classes):
            class_name = value.pop("__type__")
            cls = classes.get(class_name)
            if cls is None:
                raise DeserializationError(f"Unknown class type: {class_name}")
            obj = cls.__new__(cls)
            for key, val in value.items():
                setattr(obj, key, deserialize2(val, classes))
            return obj

        type_dispatch = {
            "set": handle_set,
            "frozenset": handle_frozenset,
            "tuple": handle_tuple,
        }

        if isinstance(data, (int, float, str, bool, type(None))):
            return handle_primitive(data, classes)
        elif isinstance(data, list):
            return handle_list(data, classes)
        elif isinstance(data, dict):
            if "__type__" in data:
                obj_type = data["__type__"]
                if obj_type in type_dispatch:
                    return type_dispatch[obj_type](data, classes)
                return handle_custom_class(data, classes)
            else:
                return {key: deserialize2(value, classes) for key, value in data.items()}
        else:
            raise DeserializationError(f"Type {type(data)} not deserializable")
    except Exception as e:
        raise DeserializationError(f"Error during deserialization: {e}")


if __name__ == '__main__':
    # Example usage
    default_initial_spacecraft_dict = serialize(get_initial_spacecraft())
    default_initial_spacecraft_json = json.dumps(default_initial_spacecraft_dict)

    reconstructed_sc = deserialize2(default_initial_spacecraft_json)
