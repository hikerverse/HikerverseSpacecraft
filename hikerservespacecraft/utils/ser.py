# python
import importlib
import inspect
import json
import pkgutil
import dataclasses
from typing import Any, Dict, Iterable, Set

from hikerservespacecraft.hull import Hull
from hikerservespacecraft.spacecraft import Spacecraft
from hikerservespacecraft.spacecraft_bus import SpacecraftBus, PowerBus
from hikerservespacecraft.spacecraft_constructor import get_initial_spacecraft


class SerializationError(Exception):
    pass


class DeserializationError(Exception):
    pass



"""
Serializer that converts Python objects to JSON-serializable Python structures
and reconstructs objects back. Honors opt-out exclusion via `__serialize_exclude__`,
dataclass field metadata `metadata={'serialize': False}`, and `__serialize__` / `__getstate__`.
"""


extra_classes={}
core = {cls.__name__: cls for cls in [Spacecraft, Hull, SpacecraftBus, PowerBus]}
_classes = {**core, **(extra_classes or {})}
# payloads are discovered lazily during deserialize


def _load_payload_classes() -> Dict[str, type]:

    payload_classes: Dict[str, type] = {}
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





_PAYLOAD_CLASSES_CACHE: Dict[str, type] = _load_payload_classes()


def _collect_exclude_names(obj: Any) -> Set[str]:
    excluded: Set[str] = set()
    cls = type(obj)
    for source in (getattr(obj, "__serialize_exclude__", None), getattr(cls, "__serialize_exclude__", None)):
        if source is None:
            continue
        if isinstance(source, str):
            excluded.add(source)
        elif isinstance(source, Iterable):
            excluded.update(str(x) for x in source)
        else:
            excluded.add(str(source))
    return excluded

def _should_serialize_attr(obj: Any, name: str) -> bool:
    # dataclass field metadata override
    if dataclasses.is_dataclass(obj):
        for f in dataclasses.fields(obj):
            if f.name == name and f.metadata.get("serialize") is False:
                return False
    if name in _collect_exclude_names(obj):
        return False
    return True

def serialize(obj: Any, _max_depth: int = 50) -> Any:
    try:
        return _serialize(obj, set(), 0, _max_depth)
    except Exception as e:
        raise SerializationError(f"Error during serialization: {e}")

def _serialize(obj: Any, _seen: Set[int], _depth: int, _max_depth: int) -> Any:
    if _seen is None:
        _seen = set()

    if _depth > _max_depth:
        return {"__recursion__": True, "__repr__": repr(obj)}

    # primitives
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    oid = id(obj)
    if oid in _seen:
        return {"__recursion__": True, "__type__": type(obj).__name__, "__repr__": repr(obj)}

    _seen.add(oid)
    try:
        # containers
        if isinstance(obj, tuple):
            return {"__type__": "tuple", "items": [_serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
        if isinstance(obj, list):
            return [_serialize(i, _seen, _depth + 1, _max_depth) for i in obj]
        if isinstance(obj, set):
            return {"__type__": "set", "items": [_serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
        if isinstance(obj, frozenset):
            return {"__type__": "frozenset", "items": [_serialize(i, _seen, _depth + 1, _max_depth) for i in obj]}
        if isinstance(obj, dict):
            return {str(k): _serialize(v, _seen, _depth + 1, _max_depth) for k, v in obj.items()}

        # full custom serialization hook
        if hasattr(obj, "__serialize__"):
            try:
                custom = obj.__serialize__()
                return _serialize(custom, _seen, _depth + 1, _max_depth)
            except Exception:
                # fall back to other mechanisms
                pass

        # prefer __getstate__ if present
        state = None
        if hasattr(obj, "__getstate__"):
            try:
                state = obj.__getstate__() or {}
            except Exception:
                state = None

        # custom object handling: use state or vars/slots
        if state is None:
            try:
                state = dict(vars(obj))
            except TypeError:
                state = {}

        result = {"__type__": type(obj).__name__}
        for k, v in state.items():
            if not _should_serialize_attr(obj, k):
                continue
            try:
                result[k] = _serialize(v, _seen, _depth + 1, _max_depth)
            except SerializationError:
                result[k] = repr(v)
            except Exception:
                result[k] = repr(v)

        # __slots__
        slots = getattr(type(obj), "__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            if hasattr(obj, slot) and _should_serialize_attr(obj, slot):
                try:
                    result[slot] = _serialize(getattr(obj, slot), _seen, _depth + 1, _max_depth)
                except Exception:
                    result[slot] = repr(getattr(obj, slot))

        return result
    finally:
        _seen.discard(oid)

def deserialize(data: Any, fmt: str = "json") -> Any:
    try:
        if fmt == "json" and isinstance(data, str):
            data = json.loads(data)
        return _deserialize_recursive(data)
    except DeserializationError:
        raise
    except Exception as e:
        raise DeserializationError(f"Error during deserialization: {e}")

def _deserialize_recursive(data: Any) -> Any:
    # build classes mapping with discovered payload classes
    classes = {**_classes, **_load_payload_classes()}

    def handle_primitive(value):
        return value

    def handle_list(value):
        return [_deserialize_recursive(item) for item in value]

    def handle_set(value):
        return set(_deserialize_recursive(item) for item in value["items"])

    def handle_frozenset(value):
        return frozenset(_deserialize_recursive(item) for item in value["items"])

    def handle_tuple(value):
        return tuple(_deserialize_recursive(item) for item in value["items"])

    def handle_custom_class(value):
        class_name = value.pop("__type__")
        cls = classes.get(class_name)
        if cls is None:
            raise DeserializationError(f"Unknown class type: {class_name}")
        obj = cls.__new__(cls)
        for key, val in value.items():
            setattr(obj, key, _deserialize_recursive(val))
        return obj

    type_dispatch = {
        "set": handle_set,
        "frozenset": handle_frozenset,
        "tuple": handle_tuple,
    }

    if isinstance(data, (int, float, str, bool, type(None))):
        return handle_primitive(data)
    if isinstance(data, list):
        return handle_list(data)
    if isinstance(data, dict):
        if "__type__" in data:
            t = data["__type__"]
            if t in type_dispatch:
                return type_dispatch[t](data)
            return handle_custom_class(dict(data))  # copy to avoid mutating input
        return {k: _deserialize_recursive(v) for k, v in data.items()}

    raise DeserializationError(f"Type {type(data)} not deserializable")


if __name__ == '__main__':
    # Example usage
    default_initial_spacecraft_dict = serialize(get_initial_spacecraft())
    default_initial_spacecraft_json = json.dumps(default_initial_spacecraft_dict)

    reconstructed_sc = deserialize(default_initial_spacecraft_json)

    d = 3
