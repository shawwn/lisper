from __future__ import annotations

from abc import abstractmethod
# read version from installed package
from importlib.metadata import version
__version__ = version(__name__)

del version

from typing import *

import collections.abc as std
import builtins as py
import functools
import abc

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
    return globe.setdefault(name, value)

def defclass(name, globe=nil):
    def inner(cls):
        return defvar(name, cls, globe=globe)
    return inner

@defclass("Unset")
class Unset:
    pass

class UnsetType(Unset):
    def __repr__(self):
        return "#<unset>"

unset = defvar("unset", UnsetType())

def unbound(x: Unset):
    if x is unset:
        return t
    if isinstance(x, Unset):
        return t

StringT = TypeVar("TextLike", bound=Union[str, bytes])

# yy: TextLike
# xx: TextLike[str]

class StringType(std.Sequence[StringT]):
    pass
    @classmethod
    def __subclasshook__(cls, C, *, seen=()):
        print("StringType.__subclasshook__", cls, C)
        if cls in seen:
            return NotImplemented
        if issubclass(C, (TextType, MemoryType)):
            return t
        return NotImplemented

class TextType(py.str, std.Sequence[str]):
    @classmethod
    def __subclasshook__(cls, C, *, seen=()):
        print("TextType.__subclasshook__", cls, C)
        if issubclass(C, py.str):
            return True
        if issubclass(C, (py.bytes, py.bytearray, py.memoryview)):
            return False
        if cls in seen:
            return NotImplemented
        if MemoryType.__subclasshook__(C, seen=(*seen, cls)) is True:
            print("TextType.__subclasshook__", cls, C, f"=> #f (MemoryType)")
            return False
        return NotImplemented

class MemoryType(py.bytearray, std.Sequence[bytes]):
    @classmethod
    def __subclasshook__(cls, C, *, seen=()):
        print("MemoryType.__subclasshook__", cls, C)
        if issubclass(C, py.str):
            return False
        if issubclass(C, (py.bytes, py.bytearray, py.memoryview)):
            return True
        if cls in seen:
            return NotImplemented
        if TextType.__subclasshook__(C, seen=(*seen, cls)) is True:
            print("MemoryType.__subclasshook__", cls, C, f"=> #f (TextType)")
            return False
        return NotImplemented

# StringType.register(py.str)
# StringType.register(py.bytes)
# StringType.register(py.bytearray)
# StringType.register(py.memoryview)
StringType.register(TextType)
StringType.register(MemoryType)

# TextType.register(py.str)

MemoryType.register(py.bytes)
# MemoryType.register(py.bytearray)
MemoryType.register(py.memoryview)

class Seq(py.tuple, std.Sequence[T], metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, C, *, seen={}):
        print("Seq.__subclasshook__", cls, C)
        if cls is not Seq:
            print("Seq.__subclasshook__", cls, C, f"=> NotImplemented (not Seq)")
            return NotImplemented
        if C in seen:
            print("Seq.__subclasshook__", cls, C, f"=> {seen[C]=} (seen)")
            return seen[C]
        seen[C] = NotImplemented
        if issubclass(C, std.Sequence):
            if issubclass(C, StringType):
                print("Seq.__subclasshook__", cls, C, "=> #f (StringType)")
                seen[C] = False
                return False
            print("Seq.__subclasshook__", cls, C, "=> #t")
            seen[C] = True
            return True
        print("Seq.__subclasshook__", cls, C, "=> NotImplemented")
        return NotImplemented

if TYPE_CHECKING:
    Seq = Union[Seq[T_co], Optional[Sequence[T_co]]]

import subprocess
subprocess.run("echo 1", stdout=1)

class ImmutableSeq(py.tuple, std.Sequence[T], metaclass=abc.ABCMeta):
    # @overload
    # @abstractmethod
    # def __getitem__(self, index: int) -> T_co: ...
    #
    # @overload
    # @abstractmethod
    # def __getitem__(self, index: slice) -> Sequence[T_co]: ...
    #
    # @abstractmethod
    # def __getitem__(self, index: int) -> T_co:
    #     raise KeyError
    #
    # @abstractmethod
    # def __len__(self) -> int:
    #     return 0

    @classmethod
    def __subclasshook__(cls, C):
        print("ImmutableSeq.__subclasshook__", cls, C)
        if cls is ImmutableSeq:
            if issubclass(C, std.MutableSequence):
                print("ImmutableSeq.__subclasshook__", cls, C, "=> #f (std.MutableSequence)")
                return False
        # else:
        #     if issubclass(C, std.Sequence):
        #         print("ImmutableSeq.__subclasshook__", cls, C, "=> #t (std.Sequence)")
        #         return True
        # result = super().__subclasshook__(C)
        # result = Seq.__subclasshook__(C)
        result = NotImplemented
        print("ImmutableSeq.__subclasshook__", cls, C, f"=> {result=}")
        return result

if TYPE_CHECKING:
    ImmutableSeq = Optional[Tuple[T_co, ...]]

if TYPE_CHECKING:
    MutableSeq: TypeAlias = Optional[MutableSequence[T_co]]
else:
    class MutableSeq(py.list, std.MutableSequence[T_co], metaclass=abc.ABCMeta):
        if TYPE_CHECKING:
            @overload
            def __init__(self): ...
            @overload
            def __init__(self, x: Iterable[T_co]): ...
                # super().__init__(x)
            def __init__(self, *args):
                super().__init__(*args)
        def __class_getitem__(cls: Type[MutableSeq[T_co]], item: T_co) -> Type[MutableSeq[T_co]]:
            return cls
        @classmethod
        def __subclasshook__(cls, C, *, _recurse=[]):
            print("MutableSeq.__subclasshook__", cls, C)
            _recurse.append(True)
            breakpoint()
            try:
                if issubclass(C, Seq):
                    if issubclass(C, std.MutableSequence):
                        return True
                    return False
                return NotImplemented
            finally:
                _recurse.pop()
            if len(_recurse) > 0:
                if issubclass(C, std.MutableSequence):
                    return True
                return std.MutableSequence.__subclasshook__(C)
            _recurse.append(True)
            try:
                if issubclass(C, std.Sequence):
                    if not issubclass(C, std.MutableSequence):
                        print("MutableSeq.__subclasshook__", cls, C, "=> #f (not std.MutableSequence)")
                        return False
                    return True
                # result = super().__subclasshook__(C)
                # result = Seq.__subclasshook__(C)
                result = NotImplemented
                print("MutableSeq.__subclasshook__", cls, C, f"=> {result=}")
                return result
            finally:
                _recurse.pop()

# if TYPE_CHECKING:
#     # MutableSeq: TypeAlias = Optional[MutableSequence[T_co]]
#     MutableSeq[int]
# if TYPE_CHECKING:
#     MutableSeq: TypeAlias = Optional[Union[MutableSequence[T_co]]]

if (lambda: False)():
    MutableIntSeq: TypeAlias = MutableSeq[int]
    xx0: MutableSeq[int] =["asdf"]
    xx0: MutableSeq[int] =[0]
    MutableIntSeq()
    xx0b: MutableSeq[int] = MutableSeq(["hi"])
    xx1: MutableSeq[int] =[0]
    xx2: MutableSeq[int] =[0.5]
    class Integer(int):
        pass
    xx3: MutableSeq[int] =[Integer(0)]
    def foo(l: MutableSeq[int]):
        pass
    foo(xx0)
    foo(["hi"])
    foo((0, 1))
    foo([0, 1, 2])
    foo(bytearray(b'hi'))
    class MySeq(MutableSeq[T_co]):
        @classmethod
        def new(cls: Type[MySeq[T_co]], x: MutableSeq[T_co]) -> MySeq[T_co]:
            return cls(x)

    # MyIntSeq: TypeAlias = MySeq[int]
    if TYPE_CHECKING:
        class MyIntSeq(MySeq[int]):
            pass
    else:
        MyIntSeq = MySeq
    l: MySeq[int] = ["hi"]
    l: MySeq[int] = [0]
    l: MySeq[int] = MyIntSeq.new([0])
    l: MySeq[int] = MyIntSeq.new(["omg"])
    l: MySeq[int] = MyIntSeq.new([0.5])

# if TYPE_CHECKING:
#     class MutableSeq(MutableSequence[T_co]):
#         pass


# if TYPE_CHECKING:
#     class ImmutableSeq(Tuple[T_co]):
#         pass
#     # ImmutableSeq: TypeAlias = Tuple
#     class MutableSeq(List[T_co]):
#         pass
#     # MutableSeq: TypeAlias = List

# _MutableIntSeq = TypeVar("_MutableIntSeq", bound=MutableSeq[int])
if TYPE_CHECKING:
    # class _MutableIntSeq(MutableSeq[int]):
    #     pass
    _MutableIntSeq = Union[MutableSeq[int], List[int]]
l: _MutableIntSeq = ["asdf"]
l: _MutableIntSeq = [0]

def _test():
    def foo(x: _MutableIntSeq):
        return x
    # if (lambda: False)(): l = ([],)
    l2: MutableSeq[int]
    l2 = ["hi"]
    foo("hi")
    foo(b"hi")
    foo(bytearray(b"hi"))
    l2[0]
    l: ImmutableSeq[MutableSeq[int]]
    l[0][0] = 42
    l[0][0] = None
    l[0][0] = "hi"
    l = []
    l = ()
    l = nil

def car(l: Sequence[T]) -> Optional[T]:
    if l:
        return l[0]

SeqType = TypeVar("SeqType", bound=Sequence)

def cdr(l: SeqType) -> Optional[SeqType]:
    if l:
        return l[1:]

def string(x):
    if isinstance(x, StringType):
        return t

assert string("abc")
assert string(b"abc")
assert string(py.bytearray(b"abc"))

def text(x):
    if isinstance(x, TextType):
        return t

assert text("abc")
assert not text(b"abc")
assert not text(py.bytearray(b"abc"))

def memory(x):
    if isinstance(x, MemoryType):
        return t

def pair(x):
    if isinstance(x, Seq):
        return t

assert not pair(t)
assert not pair(nil)
assert not pair("abc")
assert pair(())
assert pair([])

def mutable(x):
    if isinstance(x, MutableSeq):
        return t

assert mutable([])
assert not mutable(t)
assert not mutable(nil)
assert not mutable(())
assert not mutable("abc")
assert not mutable(b"abc")
assert mutable(py.bytearray(b'abc'))

def atom(x):
    if not pair(x):
        return t
assert not pair("abc")

def null(x):
    if x is nil:
        return t
    if pair(x) and not x:
        return t

def ok(x):
    if not null(x):
        return t


ParameterT = TypeVar("ParameterT", bound="Parameter")

class Parameter(Generic[T]):
    def __init__(self, fget: Callable[[], T], fset: Callable[[T], None]):
        self.fget = fget
        self.fset = fset

    @overload
    def __call__(self) -> T: ...

    @overload
    def __call__(self, value: T) -> None: ...

    def __call__(self, *args, **kwargs):
        if len(args) <= 0:
            return self.fget()
        else:
            assert len(args) == 1
            return self.fset(args[0])

    def __class_getitem__(cls: Type[Parameter[T]], item: T) -> Type[Parameter[T]]:
        return cls

class Value(Parameter[T]):
    def __init__(self, value: T):
        self.value = value
        super().__init__(self.get, self.foo)

    def foo(self):
        pass

    def get(self) -> T:
        return self.value

    def set(self, value: T):
        self.value = value

    def __class_getitem__(cls: Type[Parameter[T]], item: T) -> Type[Parameter[T]]:
        return cls

IntValue: TypeAlias = Value[int]
if TYPE_CHECKING:
    class IntValue(Value[int]):
        pass


class Integer(int):
    pass

class Float(float):
    pass

Value[int]("hi")

v = IntValue(0.5)
v2 = IntValue(Integer(2))
v3 = IntValue(Float(2))
zz = v()
zz


