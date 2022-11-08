from __future__ import annotations

# read version from installed package
from abc import abstractmethod
from importlib.metadata import version
__version__ = version(__name__)

del version

from typing import *

import collections.abc as std
import builtins as py
import functools

T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=True)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.
T_contra = TypeVar('T_contra', contravariant=True)  # Ditto contravariant.
KT_contra = TypeVar('KT_contra', contravariant=True)  # Ditto contravariant.

t = True
nil = None
inf = float("inf")
nan = float("nan")

def defvar(name, value: T, globe=nil) -> T:
    globe = globe or globals()
    globe.setdefault(name, value)
    return value

unset = defvar("unset", object())

def car(l):
    if l:
        return l[0]

def cdr(l):
    if l:
        return l[1:]

def pair(l):
    if isinstance(l, std.Sequence):
        return t

def unslice(x: Union[slice, range]):
    return x.start, x.stop, x.step

Rangelike = TypeVar("Rangelike", slice, range)

def normslice(x: Union[slice, range], cls: Type[Rangelike] = slice) -> Rangelike:
    lo, hi, by = unslice(x)
    if lo == inf:
        lo = hi
    elif lo == -inf:
        lo = None
    if hi == inf:
        hi = None
    elif hi == -inf:
        hi = lo
    if by is None:
        by = 1
    if by > 0 and lo == 0:
        lo = None
    elif by < 0 and hi == -1:
        hi = None
    return cls(lo, hi, by)



# if TYPE_CHECKING:
#     class SupportsGetItem(Container[KT_contra], Protocol[KT_contra, VT_co]):
#         def __getitem__(self, __k: KT_contra) -> VT_co: ...
#
#     class SupportsItemAccess(SupportsGetItem[KT_contra, VT], Protocol[KT_contra, VT]):
#         def __setitem__(self, __k: KT_contra, __v: VT) -> None: ...
#         def __delitem__(self, __v: KT_contra) -> None: ...


SelfT = TypeVar("SelfT", bound="SupportsGetItemAndLength")

@runtime_checkable
class SupportsGetItemAndLength(Container[KT_contra], Sized, Protocol[KT_contra, VT_co]):
    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> T: ...

    @overload
    @abstractmethod
    def __getitem__(self: SelfT, index: slice) -> SelfT[T]: ...
    def __getitem__(self, __k: KT_contra) -> VT_co: ...
    # def __getitem__(self, __k: KT_contra) -> VT_co: ...

SeqType: TypeAlias = TypeVar("SeqType", bound="Seq")

@functools.total_ordering
class Seq(std.Sequence, Sequence[T_co], Sized):
    ref: Sequence[T_co]
    # pos: range
    pos: slice

    # def __init__(self, ref: Sequence[T_co], pos: range = nil):
    def __init__(self, ref: Sequence[T_co], pos: slice = nil):
        if pos is nil:
            # pos = range(len(ref))
            pos = slice(None, None, 1)
        self.ref = ref
        self.pos = normslice(pos)

    if TYPE_CHECKING:
        def __new__(cls: Type[SeqType[T_co]], ref: Sequence[T_co], pos: range = nil) -> SeqType[T_co]: ...

    @property
    def key(self) -> slice:
        # return normslice(self.pos)
        return self.pos

    @property
    def range(self) -> Optional[range]:
        return range(*self.pos.indices(len(self.ref)))
        # if self.pos.start is not None or self.pos.stop is not None:
        #     return normslice(self.pos, range)

    @overload
    def offset(self, index: int) -> int: ...
    @overload
    def offset(self, index: slice) -> slice: ...
    def offset(self, index: Union[int, slice]) -> Union[int, slice]:
        if self.range is None:
            where = index
        else:
            where = self.range[index]
        if isinstance(where, int):
            return where
        else:
            out: slice = normslice(where)
            lo, hi, by = unslice(out)
            if by > 0:
                if hi >= len(self.ref):
                    hi = None
            # else:
            #     if hi >= len(self.ref):
            #         hi = None
            return slice(lo, hi, by)

    @property
    def value(self) -> Sequence[T_co]:
        return self.ref[self.key]

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> T_co: ...

    @overload
    @abstractmethod
    def __getitem__(self: SeqType[T_co], index: slice) -> SeqType[T_co]: ...

    def __getitem__(self, index: Union[int, slice]):
        if isinstance(index, int):
            where = self.offset(index)
            # where = self.pos[index]
            return self.ref[where]
        else:
            # where = self.pos[index]
            where = self.offset(index)
            return type(self)(self.ref, where)

    def __len__(self) -> int:
        return len(self.value)

    def __hash__(self):
        rid = py.id(self.ref)
        # return py.hash((rid, self.pos.start, self.pos.step))
        lo, hi, by = unslice(self.pos)
        return py.hash((rid, lo, hi, by))

    def __eq__(self, other):
        return self.value == other

    def __repr__(self):
        return repr(self.value)

    def __bool__(self):
        return bool(self.value)

    def __lt__(self, other):
        return self.value < other

    def __add__(self, other):
        return self.value + other



MutType: TypeAlias = TypeVar("MutType", bound="MutableSeq")

class MutableSeq(Seq[T_co], std.MutableSequence, MutableSequence[T_co]):
    ref: MutableSequence[T_co]
    value: MutableSequence[T_co]

    @property
    def value(self) -> MutableSequence[T_co]:
        return self.ref[self.key]

    @value.setter
    def value(self, v: T_co):
        self.ref[self.key] = v

    # def __init__(self, ref: MutableSequence[T_co], pos: range = nil):
    def __init__(self, ref: MutableSequence[T_co], pos: slice = nil):
        super().__init__(ref, pos)

    if TYPE_CHECKING:
        # def __new__(cls: Type[MutType[T_co]], ref: Sequence[T_co], pos: range = nil) -> MutType[T_co]: ...
        def __new__(cls: Type[MutType[T_co]], ref: Sequence[T_co], pos: slice = nil) -> MutType[T_co]: ...

    def insert(self, index: int, value: T_co) -> None:
        where = self.range[index:].start
        return self.ref.insert(where, value)

    @overload
    @abstractmethod
    def __setitem__(self, index: int, value: T_co) -> None: ...

    @overload
    @abstractmethod
    def __setitem__(self, index: slice, value: Iterable[T_co]) -> None: ...

    def __setitem__(self, index: int, value: T_co) -> None:
        where = self.pos[index]
        self.ref[where] = value

    @overload
    @abstractmethod
    def __delitem__(self, index: int) -> None: ...

    @overload
    @abstractmethod
    def __delitem__(self, index: slice) -> None: ...

    def __delitem__(self, index: int) -> None:
        where = self.pos[index]
        del self.ref[where]


# zz = MutableSeq([4, 5, 6])
# zz.value[0] = 42

def mutable(cls):
    if cls is list or issubclass(cls, std.MutableSequence):
        return t

SequenceType = TypeVar("SequenceType", bound=Sequence[T_co])

# # @overload
# # def join(a: T_co = nil, b: MutableSequence[T_co] = nil) -> MutableSeq[T_co]: ...
# # @overload
# # def join(a: T_co = nil, b: MutableSequence[T_co] = nil, cls: Type[MutableSequence] = nil) -> MutableSeq[T_co]: ...
# # @overload
# # def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[Sequence] = nil) -> Seq[T_co]: ...
# # @overload
# # def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[Sequence] = nil) -> Seq[T_co]: ...
# # @overload
# # def join(a: T_co = nil, b: None = nil, cls: Type[MutableSequence] = nil) -> MutableSeq[T_co]: ...
# # def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[Sequence] = nil) -> Seq[T_co]:
# @overload
# def join(a: T_co, b: Sequence[T_co]) -> Seq[T_co]: ...
# @overload
# def join(a: T_co, b: Optional[Sequence[T_co]], cls: Type[Sequence[T_co]]) -> Seq[T_co]: ...
# @overload
# def join(a: T_co, b: MutableSequence[T_co]) -> MutableSeq[T_co]: ...
# @overload
# def join(a: T_co, b: Optional[Sequence[T_co]], cls: Type[MutableSequence[T_co]]) -> MutableSeq[T_co]: ...
# @overload
# def join(a: T_co, b: Optional[Sequence[T_co]], cls: Type[Sequence[T_co]]) -> MutableSeq[T_co]: ...
# @overload
# def join(a: T_co, b: Optional[Sequence[T_co]], cls: Type[Tuple]) -> Seq[T_co]: ...
# @overload
# def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[MutableSequence[T_co]] = nil) -> MutableSeq[T_co]: ...
# @overload
# def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[Sequence[T_co]] = nil) -> Seq[T_co]: ...
# def join(a: T_co = nil, b: Sequence[T_co] = nil, cls: Type[Sequence[T_co]] = nil) -> Seq[T_co]:
def join(a: T_co = nil, b: Sequence[T_co] = nil) -> Seq[T_co]:
    if b:
        return Seq((a, *b))
    else:
        return Seq((a,))

# join(1, (2,))
# zz = join(1, [2])

def slot(a: T_co = nil, b: Sequence[T_co] = nil, cls=py.list) -> MutableSeq[T_co]:
    if b:
        return MutableSeq(cls((a, *b)))
    else:
        return MutableSeq(cls((a,)))

# zz = slot(1, (2,))
# zz[0] = 42
# zz
