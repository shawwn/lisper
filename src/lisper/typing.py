"""
Helper module to simplify version specific typing imports

This module is for internal use only. Do *not* put any new
"async typing" definitions here.
"""
import sys
from typing import (
    TypeVar,
    Hashable,
    Union,
    AsyncIterable,
    Iterable,
    Callable,
    Any,
    Awaitable,
    Generic,
    Callable,
    Mapping,
    overload,
    TYPE_CHECKING,
)

if sys.version_info >= (3, 8):
    from typing import Protocol, AsyncContextManager, ContextManager, TypedDict
else:
    from typing_extensions import (
        Protocol,
        AsyncContextManager,
        ContextManager,
        TypedDict,
    )

from .types import *

# __all__ = [
#     "TYPE_CHECKING",
#     "overload",
#     "Generic",
#     "Any",
#     "Callable",
#     "Mapping",
#     "Protocol",
#     "AsyncContextManager",
#     "ContextManager",
#     "TypedDict",
#     "T",
#     "T1",
#     "T2",
#     "T3",
#     "T4",
#     "T5",
#     "R",
#     "AC",
#     "HK",
#     "LT",
#     "ADD",
#     "AnyIterable",
# ]

if sys.version_info >= (3, 10):
    from typing import (ParamSpec, ParamSpecKwargs, ParamSpecArgs)
else:
    from typing_extensions import (ParamSpec, ParamSpecKwargs, ParamSpecArgs)

P = ParamSpec("P")

# __all__ += [
#     "ParamSpec",
#     "ParamSpecKwargs",
#     "ParamSpecArgs",
# ]

del sys
