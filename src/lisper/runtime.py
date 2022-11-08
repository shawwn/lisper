from __future__ import annotations

import inspect
from typing import *
import builtins as py
import numbers
import collections.abc as std
from functools import singledispatch as dispatch
import types

#
# constants
#

nil = None
t = True

class Unset:
    def __bool__(self):
        return False

    def __repr__(self):
        return "unset"

    def __eq__(self, other):
        return other is unset
    #
    # def __call__(self, *x):
    #     return x[0] is unset if x else unset

unset = Unset()

def unbound(*x):
    return x[0] is unset if x else unset

#
# equality
#
def id(x=nil, y=nil):
    """Return t if x is identical to y, else nil."""
    if x is y:
        return t

def null(x=nil):
    """Return t if x is nil, else nil."""
    if id(x, nil):
        return t
#
# truthiness
#

def ok(x=nil):
    """Return t if x isn't nil, else nil."""
    if not null(x):
        return t

def no(x=nil):
    """Return t if x is false, else nil."""
    if not x:
        return t
#
# if
#
def if_(cond, a, b):
    return b if no(cond) else a

def either(a, *bs):
    if not bs or ok(a):
        return a
    return either(*bs)

#
# accessors
#

@dispatch
def at(x, k, *default):
    if default:
        try:
            return x[k]
        except LookupError:
            return default[0]
    else:
        return x[k]

@dispatch
def get(x, k, *default):
    return py.getattr(x, k, *default)

#
# object naming
#
@dispatch
def nom(x):
    return py.getattr(x, "__qualname__", py.getattr(x, "__name__", x))

@nom.register(py.type(nil))
def nom_nil(_x):
    return "nil"

@nom.register(py.type(py.bool))
def nom_bool(x):
    return "t" if x else "false"

@nom.register(py.type(py.bool))
def nom_bool(x):
    return "t" if x else "false"


#
# type predicates
#
T = TypeVar("T")
R = TypeVar("R")

def function(x):
    return inspect.isfunction(x)

def type(x):
    return inspect.isclass(x)

@overload
def define(name: str, constructor: Callable[[], T], globals=globals) -> T: ...
@overload
def define(name: str, constructor: Type[T], globals=globals) -> T: ...
def define(name: str, constructor, globals=globals) -> T:
    return globals().setdefault(name, constructor())

RegistryK: TypeAlias = Union[Type, str, Callable[[T], bool]]
RegistryV: TypeAlias = Union[str, Callable[[T], R], None, bool]
class Registry:
    registry: Dict[RegistryK, RegistryV]
    def __init__(self):
        self.registry = {}
    def set(self, key: RegistryK, value: RegistryV):
        self.registry[key] = value
    @overload
    def get(self, key: RegistryK) -> RegistryV: ...
    @overload
    def get(self, key: RegistryK, default: T) -> Union[RegistryV, T]: ...
    def get(self, key: RegistryK, *default):
        if not default:
            return self.registry[key]
        else:
            try:
                return self.registry[key]
            except KeyError:
                return default[0]
    def __setitem__(self, key: RegistryK, value: RegistryV):
        self.set(key, value)
    def __getitem__(self, key: RegistryK):
        return self.get(key)
    def items(self):
        return self.registry.items()

@overload
def deref(x: Callable[..., T], *args, **kws) -> T: ...
@overload
def deref(_x: T, *args, **kws) -> T: ...
def deref(x, *args, **kws):
    if null(x):
        return deref(*args, **kws)
    elif function(x):
        return x(*args, **kws)
    else:
        return x

class Namespace:
    def __init__(self, *registries: Callable[[], Registry]):
        self.registries = py.list(registries)
    def find(self, x, *default):
        for func in self.registries:
            registry = deref(func)
            for k, v in registry.items():
                print(k, v, x)
                # breakpoint()
                if inspect.isclass(k):
                    if not py.isinstance(x, k):
                        continue
                elif callable(k):
                    if no(k(x)):
                        continue
                elif not id(k, x):
                    continue
                if null(v):
                    break
                elif v is t:
                    return x
                else:
                    return deref(v, x)
        if default:
            return deref(default[0])
        raise KeyError(x)

sequence_types = define("sequence_types", Registry)
number_types = define("number_types", Registry)
table_types = define("table_types", Registry)

lobby = Namespace(lambda: sequence_types,
                  lambda: number_types,
                  lambda: table_types,
                  )

sequence_types[py.list] = t
sequence_types[py.tuple] = t
number_types[py.bool] = nil
number_types[py.int] = t
number_types[py.float] = t
number_types[numbers.Number] = t
table_types[py.dict] = t
table_types[std.Mapping] = t

def pairs(l):
    if isinstance(l, std.Collection):
        for x in l:
            if ok(x):
                if isinstance(x, std.Collection) and py.len(x) == 2 and not string(x):
                    return t

def sequence(x):
    return isinstance(x, (py.list, py.tuple))

def number(x):
    if py.type(x) in [py.int, py.float]:
        return t
    elif isinstance(x, numbers.Number):
        if not isinstance(x, bool):
            return t

def table(x):
    return isinstance(x, (py.dict, std.Mapping))

def string(x):
    return isinstance(x, py.str)

def binary(x):
    return isinstance(x, (py.bytes, py.bytearray, py.memoryview))

#
# car, cdr, join
#
def car(l=nil):
    if l:
        return l[0]

assert car(nil) == nil
assert car([]) == nil
assert car([1]) == 1
assert car([[1]]) == [1]
assert car(car([[1]])) == 1
assert car(car([(1, 2)])) == 1

def cdr(l=nil):
    if l and (x := l[1:]):
        if x[0] == "." and py.len(x) == 2 and not string(l):
            return x[1]
        return x

assert cdr(nil) == nil
assert cdr([]) == nil
assert cdr([1]) == nil
assert cdr([1, ".", 2]) == 2
assert cdr((1, 2, 3)) == (2, 3)
assert cdr("foo") == "oo"
assert cdr("a.b") == ".b"

class Seq(py.tuple):
    def __hash__(self):
        return py.hash(py.id(self))

def join(x=nil, y=nil, type=Seq):
    if sequence(y):
        return type([x, *y])
    elif null(y):
        return type([x])
    else:
        return type([x, ".", y])

assert join(nil, nil) == (nil,)
assert join(1, 2) == (1, ".", 2)
assert join(1, "foo") == (1, ".", "foo")