from __future__ import annotations

import functools
import sys
import types

from typeguard import typeguard_ignore

try:
    from types import (  # type: ignore[attr-defined, unused-ignore]
        UnionType as _Union,
    )
except ImportError:
    from typing import (  # type: ignore[assignment, unused-ignore]
        Union as _Union,
    )
from typing import Any, Mapping, Union, get_args, get_origin


def type_matches(expected: Any, actual: type) -> bool:
    """Checks if a class matches an expected result.

    This includes checking if the actual class is in a Union with other classes.

    Example:
        >>> expected_class = Union[str, int]
        >>> actual_class = str
        >>> type_matches(expected_class, actual_class)
        True
    """
    if expected == actual:
        return True

    if get_origin(expected) is Union or get_origin(expected) is _Union:
        for sub_type in get_args(expected):
            if sub_type == actual:
                return True

    return False


@typeguard_ignore
def get_annotations(
    obj: object | type | types.ModuleType,
    *,
    globals: dict[str, Any] | None = None,  # noqa A002
    locals: Mapping[str, Any] | None = None,  # noqa A002
    eval_str: bool = True,
) -> dict[str, Any]:
    """Compute the annotations dict for an object.

    Tries to use the standard inspect package if available (>Python 3.10)
    Otherwise, uses the back-ported function in this module.
    """
    try:
        from inspect import (  # type: ignore[attr-defined, unused-ignore]
            get_annotations,
        )

        return get_annotations(  # type: ignore[no-any-return, unused-ignore]
            obj,  # type: ignore[arg-type, unused-ignore]
            globals=globals,
            locals=locals,
            eval_str=eval_str,
        )
    except ImportError:
        return _get_annotations(
            obj, _globals=globals, _locals=locals, eval_str=eval_str
        )


@typeguard_ignore
def _eval_annotations(
    value: Any, _globals: dict[str, Any] | None, _locals: Mapping[str, object] | None
) -> Any:
    def _eval(_value: Any) -> Any:
        try:
            return eval(_value, _globals, _locals)  # noqa S307
        except:  # noqa E722
            return _value

    values = value.split(" | ")
    evals = [_eval(value) for value in values]

    if len(evals) == 1:
        return evals[0]

    return Union[tuple(evals)]  # type: ignore[misc, unused-ignore]


@typeguard_ignore
def _get_annotations(  # noqa C901
    obj: object | type | types.ModuleType,
    *,
    _globals: dict[str, Any] | None = None,
    _locals: Mapping[str, Any] | None = None,
    eval_str: bool,
) -> dict[str, Any]:
    """Compute the annotations dict for an object.

    This function is back-ported from Python 3.10.
    See https://docs.python.org/3/howto/annotations.html
    and https://docs.python.org/3/library/inspect.html#inspect.get_annotations

    """
    if isinstance(obj, type):
        # class
        obj_dict = getattr(obj, "__dict__", None)
        if obj_dict and hasattr(obj_dict, "get"):
            ann = obj_dict.get("__annotations__", None)
            if isinstance(ann, types.GetSetDescriptorType):
                ann = None
        else:
            ann = None

        obj_globals = None
        module_name = getattr(obj, "__module__", None)
        if module_name:
            module = sys.modules.get(module_name, None)
            if module:
                obj_globals = getattr(module, "__dict__", None)
        obj_locals = dict(vars(obj))
        unwrap: object = obj
    elif isinstance(obj, types.ModuleType):
        # module
        ann = getattr(obj, "__annotations__", None)
        obj_globals = getattr(obj, "__dict__", None)
        obj_locals = None
        unwrap = None
    elif callable(obj):
        # this includes types.Function, types.BuiltinFunctionType,
        # types.BuiltinMethodType, functools.partial, functools.singledispatch,
        # etc etc etc...
        ann = getattr(obj, "__annotations__", None)
        obj_globals = getattr(obj, "__globals__", None)
        obj_locals = None
        unwrap = obj
    else:
        raise TypeError(f"{obj!r} is not a module, class, or callable.")

    if ann is None:
        return {}

    if not isinstance(ann, dict):
        raise ValueError(f"{obj!r}.__annotations__ is neither a dict nor None")

    if not ann or not eval_str:
        return ann

    if unwrap is not None:
        while True:
            if hasattr(unwrap, "__wrapped__"):
                unwrap = unwrap.__wrapped__
                continue
            if isinstance(unwrap, functools.partial):
                unwrap = unwrap.func
                continue
            break
        if hasattr(unwrap, "__globals__"):
            obj_globals = unwrap.__globals__

    eval_globals: dict[str, Any] | None = obj_globals if _globals is None else _globals

    if _locals is None:
        _locals = obj_locals

    return {
        key: value
        if not isinstance(value, str)
        else _eval_annotations(value, eval_globals, _locals)
        for key, value in ann.items()
    }
