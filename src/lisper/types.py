# from typing import Protocol, TypeVar, Hashable, Callable, Any, Awaitable, Union, Iterable, AsyncIterable
from typing import *

# TypeVars for argument/return type
T = TypeVar("T")
S = TypeVar("S")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
R = TypeVar("R", covariant=True)
C = TypeVar("C", bound=Callable[..., Any])
CLS = TypeVar("CLS", bound=Type)
AC = TypeVar("AC", bound=Callable[..., Awaitable[Any]])


#: Hashable Key
HK = TypeVar("HK", bound=Hashable)

# LT < LT
LT = TypeVar("LT", bound="SupportsLT")

class SupportsLT(Protocol):
    def __lt__(self: LT, other: LT) -> bool:
        raise NotImplementedError


# ADD + ADD
ADD = TypeVar("ADD", bound="SupportsAdd")


class SupportsAdd(Protocol):
    def __add__(self: ADD, other: ADD) -> ADD:
        raise NotImplementedError

#: (async) iter T
AnyIterable = Union[Iterable[T], AsyncIterable[T]]
