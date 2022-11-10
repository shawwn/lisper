from __future__ import annotations

import collections.abc as std
import builtins as py
import dataclasses
from abc import abstractmethod
from typing import *
from functools import singledispatch as dispatch
import numbers

t = True
nil = None

T = TypeVar("T")
ConsType = TypeVar("ConsType", bound="Cons")

@dataclasses.dataclass
class Cons(std.MutableSequence[T]):
    car: Optional[T] = nil
    cdr: Optional[Cons[T]] = nil

    if TYPE_CHECKING:
        def __new__(cls: Type[ConsType[T]], car: Optional[T] = nil, cdr: Optional[Cons[T]] = nil) -> ConsType[T]: ...

    def __hash__(self):
        return py.hash(py.id(self))

    def insert(self, index: int, value: T) -> None:
        raise NotImplementedError

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> T: ...

    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> MutableSequence[T]: ...

    def __getitem__(self, index: int) -> T:
        if isinstance(index, py.slice):
            start, stop, stride = index.indices(len(self))
            r = []
            for i in range(start, stop, stride):
                r.append(self[i])
            return new(self, r)
        if index == 0:
            return self.car
        elif index > 0:
            if self.cdr:
                return self.cdr[index - 1]
            raise IndexError("index out of range")
        elif index < 0:
            index = len(self) + index
            if index < 0:
                raise IndexError("index out of range")
            return self[index]

    @overload
    @abstractmethod
    def __setitem__(self, index: int, value: T) -> None: ...

    @overload
    @abstractmethod
    def __setitem__(self, index: slice, value: Iterable[T]) -> None: ...

    def __setitem__(self, index: int, value: T) -> None:
        raise NotImplementedError

    @overload
    @abstractmethod
    def __delitem__(self, index: int) -> None: ...

    @overload
    @abstractmethod
    def __delitem__(self, index: slice) -> None: ...

    def __delitem__(self, index: int) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        n = 1
        tail = self.cdr
        while tail:
            n += 1
            tail = tail.cdr
        return n

@dispatch
def new(l, lst):
    cls = type(l)
    return cls(lst)

@new.register(type(nil))
def new_None(l: None, x):
    return new_Cons(Cons(), x)

@new.register(Cons)
def new_Cons(l: Cons[T], lst: Optional[Sequence[T]]) -> Optional[Cons[T]]:
    cls: Type[Cons[T]] = type(l)
    if not isinstance(lst, std.Reversible):
        lst = py.tuple(lst or [])
    r: Optional[Cons[T]] = nil
    for l in reversed(lst):
        r = cls(l, r)
    return r

@new.register(py.str)
def new_str(l: str, lst: Optional[Sequence[str]]) -> str:
    return type(l)(''.join(lst))

@new.register(py.bytes)
def new_bytes(l: bytes, lst: Optional[Sequence[bytes]]) -> bytes:
    return type(l)(b''.join(lst))

@dispatch
def conj(l, x):
    return new(l, (x, *l))

@conj.register(type(nil))
def conj_None(l: None, x):
    return Cons(x)

@conj.register(Cons)
def conj_Cons(l: Cons[T], x: Optional[T]):
    # return type(l)(x, l)
    return Cons(x, l)

@conj.register(py.str)
def conj_str(l: str, x: str) -> str:
    return x + l

@conj.register(py.bytes)
def conj_bytes(l: bytes, x: bytes) -> bytes:
    if isinstance(x, py.int):
        x = x.to_bytes(1, "little")
    return x + l

def join(x=nil, l=nil):
    return conj(l, x)

def car(x):
    if x:
        return x[0]

@dispatch
def cdr(x):
    if x:
        return x[1:]

@cdr.register(Cons)
def cdr_Cons(x: Cons):
    return x.cdr

def sequence(x):
    if isinstance(x, (Cons, py.list, py.tuple)):
        return t

def boolean(x):
    if isinstance(x, py.bool):
        return t

def string(x):
    if isinstance(x, (py.str, py.bytes)):
        return t

def number(x):
    if isinstance(x, numbers.Number):
        if not boolean(x):
            return t

def table(x):
    if isinstance(x, std.Mapping):
        return t

def id(x, y):
    if number(y) and number(x):
        return eq(x, y)
    if string(y):
        return eq(x, y)
    if x is y:
        return t

def eq(x, y):
    if x == y:
        return t
