from __future__ import annotations

# read version from installed package
from abc import abstractmethod
from importlib.metadata import version
__version__ = version(__name__)

from typing import *

del version

import builtins as py
import collections
import collections.abc as std

_R = TypeVar("_R")

_VT = TypeVar("_VT")
_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_KT = TypeVar("_KT")
_VT_co = TypeVar("_VT_co", covariant=True)

t = True
nil = None

class Unset:
    def __bool__(self):
        return False
    def __repr__(self):
        return "unset"

unset = Unset()


def no(x) -> bool:
    return x is nil or x is False

def yes(x) -> bool:
    return not no(x)


class Seq(std.MutableSequence):
    def __init__(self, *args):
        self.tag = "array"
        self.rep = py.list(*args)


    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> _T: ...

    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> MutableSequence[_T]: ...

    def __getitem__(self, index: int) -> _T:
        pass

    @overload
    @abstractmethod
    def __setitem__(self, index: int, value: _T) -> None: ...

    @overload
    @abstractmethod
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None: ...

    def __setitem__(self, index: int, value: _T) -> None:
        pass

    @overload
    @abstractmethod
    def __delitem__(self, index: int) -> None: ...

    @overload
    @abstractmethod
    def __delitem__(self, index: slice) -> None: ...

    def __delitem__(self, index: int) -> None:
        pass

    def __len__(self) -> int:
        pass

    def insert(self, index: int, value: _T) -> None:
        pass

WaitT = TypeVar("WaitT", bound="IWait")

class IWait(Protocol[_T_co]):
    result: Union[_T_co, Unset]
    @abstractmethod
    def ready(self: WaitT) -> Optional[WaitT]: ...

EventT = TypeVar("EventT", bound="Event")

class Event(IWait[_T]):
    def __init__(self, result: _T = unset):
        self.result = result

    def check(self):
        return unset

    def ready(self):
        if self.result is unset:
            self.result = self.check()
        if self.result is not unset:
            return self

class Wait(Event[_T]):
    def __init__(self, check: Callable[[], _T]):
        super().__init__()
        self.check = check

    def ready(self) -> Optional[EventT]:
        if self.result is unset:
            self.result = self.check()
        return super().ready()

# ArgsT = TypeVar("ArgsT", bound=Sequence)
ArgsT: TypeAlias = Sequence

@runtime_checkable
class IApplyable(Protocol[_R]):
    def call(self, *args, **kwargs) -> _R: ...
    def apply(self, args: Optional[ArgsT] = nil) -> _R: ...
    def apply_k(self, args: Optional[ArgsT], then: Continuation) -> Continuation: ...
    def __call__(self, args: Optional[ArgsT], then: Continuation) -> Continuation: ...

class Applyable(Generic[_R]):
    @abstractmethod
    def call(self, *args, **kwargs) -> _R: ...

    def apply(self, args: Optional[ArgsT] = nil, **kws) -> _R:
        return self.call(*(args or ()), **kws)

    def apply_k(self, args: Optional[ArgsT], then: Continuation) -> Continuation:
        result = self.apply(args)
        then.push(result)
        return then

    # def __call__(self, args: Optional[ArgsT], then: Continuation) -> Continuation:
    #     return self.apply_k(args, then)
    def __call__(self, *args, **kws) -> _R:
        return self.apply(args, **kws)

class Function(Applyable[_R]):
    def __init__(self, callable: Optional[Callable[..., _R]] = nil):
        self.callable = callable

    def __new__(cls, callable: Optional[Callable[..., _R]] = nil):
        if isinstance(callable, Function):
            return callable
        return cls()

    def call(self, *args, **kwargs) -> _R:
        return self.callable(*args, **kwargs)

class Thunk(Function[_R], Callable[[], Optional[_R]]):
    def __init__(self, callable: Callable[[], Optional[_R]]):
        super().__init__(callable)

# foo: Thunk[int] = Thunk(lambda: 42)
# foo: Thunk[int] = Thunk(lambda: "hi")

# class Condition(IWait):
#     def __init__(self, *checks: Thunk):
#         self.checks = checks
#
#     def ready(self) -> bool:
#         for check in self.checks:
#             if no(check()):
#                 return False
#         return t


class ITagged(Generic[_T_co]):
    @property
    @abstractmethod
    def tag(self) -> str: ...

    @property
    @abstractmethod
    def rep(self) -> _T_co: ...

# class IWatch(ICallable[_T_co]):
#     def __call__(self, result: _T_co):
#         pass

LiteralT = TypeVar("LiteralT", bound="Literal")

class Literal(ITagged[_T_co]):
    _tag: Optional[str]
    _rep: Optional[_T_co]
    _watchers: List[Callable]

    def __init__(self):
        self._tag = nil
        self._rep = nil
        self._watchers = []

    def init(self: LiteralT, tag: str, rep: Optional[_T_co] = nil):
        self._tag = tag
        self._rep = rep

    @classmethod
    def new(cls, tag: str, rep: _T_co, *, self: Optional):
        if self is None:
            self = cls()
        self.init(tag, rep)
        self._tag = tag
        self._rep = rep

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def rep(self) -> _T_co:
        return self._rep

    @rep.setter
    def rep(self, value: _T_co):
        self._rep = value

    @property
    def watchers(self) -> Sequence[Callable]:
        return py.tuple(self._watchers)

class IQueue(Protocol[_T_co], Collection[_T_co]):
    @abstractmethod
    def append(self, result: _T_co): ...

    @abstractmethod
    def pop(self) -> _T_co: ...

    def pop_k(self, *, then: Continuation) -> Continuation:
        then.push(self.pop())
        return then

class Results(IQueue[_T_co]):
    rep: List[_T_co]

    def __init__(self):
        self.tag = "stream"
        self.rep = []

    def append(self, result: _T_co):
        self.rep.append(result)

    def pop(self) -> _T_co:
        return self.rep.pop()

    def __len__(self) -> int:
        return len(self.rep)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self.rep)

    def __contains__(self, __x: object) -> bool:
        return __x in self.rep

EnvironmentT = TypeVar("EnvironmentT", bound="Environment")

class Environment(std.MutableMapping):

    def __init__(self, *scopes: MutableMapping, protected: Sequence[MutableMapping]):
        self.tag = "tab"
        self.rep = collections.ChainMap(*scopes)
        self.protected = py.list(protected)

    @overload
    def maps(self) -> Tuple[Mapping, ...]: ...
    @overload
    def maps(self, new: bool) -> Tuple[MutableMapping, ...]: ...
    def maps(self, new: bool = False):
        if new:
            return py.tuple(map for map in self.rep.maps if map not in self.protected)
        else:
            return py.tuple(self.rep.maps)

    @overload
    def where(self, k: _KT) -> Optional[Mapping]: ...
    @overload
    def where(self, k: _KT, new: bool) -> Optional[MutableMapping]: ...
    def where(self, k: _KT, new: bool = False):
        maps = self.maps(new)
        for map in maps:
            if k in map:
                return map
        if new and maps:
            return maps[-1]

    def __setitem__(self, k: _KT, v: _VT) -> None:
        if map := self.where(k, True):
            map[k] = v
        else:
            raise KeyError(k)

    def __delitem__(self, k: _KT) -> None:
        if map := self.where(k, True):
            del map[k]
        raise KeyError(k)

    def __getitem__(self, k: _KT) -> _VT_co:
        return self.rep[k]

    def __len__(self) -> int:
        return py.len(self.rep)

    def __iter__(self) -> Iterator[_T_co]:
        return py.iter(self.rep)

    def join(self: EnvironmentT, map: MutableMapping, protected: bool = False) -> EnvironmentT:
        cls: Type[EnvironmentT] = self.__class__
        maps = [*self.rep.maps]
        protect = [*self.protected]
        maps.insert(0, map)
        if protected:
            protect.insert(0, map)
        return cls(*maps, protected=protect)

ExprT: TypeAlias = Tuple[Any, Environment]
ExprsT: TypeAlias = List[ExprT]
ReturnsT: TypeAlias = IQueue
ThreadT: TypeAlias = Tuple[IWait, ExprsT, ReturnsT]
ThreadsT: TypeAlias = List[ThreadT]
ProcessT: TypeAlias = Tuple[ThreadsT, MutableMapping]

class Process:
    globe: MutableMapping
    threads: ThreadsT

    def __init__(self, globe: Optional[Callable[[], MutableMapping]] = nil):
        self.globe = globe or globals()
        self.threads = []

    def sched(self) -> Optional[List[Tuple[Environment, Any]]]:
        for wait, stack in self.threads:
            if wait.ready():
                return stack





class Continuation:
    s: ExprsT
    r: ReturnsT
    m: ProcessT
    def __init__(self, s: ExprsT = unset, r: ReturnsT = unset, m: ProcessT = unset):
        if s is unset:
            s = []
        if r is unset:
            r = []
        if m is unset:
            m = [], globals()
        self.s = s
        self.r = r
        self.m = m

    def __repr__(self):
        return f"Continuation(stack={self.s!r}, results={self.r!r})"

    def push(self, result):
        self.r.append(result)

    def pop(self):
        return self.r.pop() if len(self.r) > 0 else unset

    def env(self, a: Optional[Environment] = nil):
        return a or Environment(self.m[1], globals(), py.__dict__, protected=[globals(), py.__dict__])

    def then(self, e, a: Optional[Environment] = nil) -> Continuation:
        print("then", e)
        a = self.env(a)
        self.s.append((e, a))
        return self

    def sync(self, wait: IWait = Event(True)) -> Tuple[ThreadsT, MutableMapping]:
        p, g = self.m
        p.append((wait, self.s, self.r))
        return p, g
        # return [*p, (wait, self.s, self.r)], g

    def eval(self, e, a: Optional[Environment] = nil, then: Continuation = unset) -> Continuation:
        if then is unset:
            then = self
        a = then.env(a)
        print('eval', e, a)
        if isinstance(e, py.str):
            v = a[e]
            then.push(v)
        elif isinstance(e, std.Sequence):
            # return call(*e, env=a, then=then)
            [f, *args] = e
            if f == "do":
                return do(*args, env=a, then=then)
            if f == "call2":
                return call2(*args, env=a, then=then)
            # then.then(f, a)
            # then.then(["call2", *args], a)
            # if callable(f):
            #     return f(*args, env=a, then=then)
            return call(f, *args, env=a, then=then)
        else:
            then.push(e)
        return then

    def run(self):
        more, then = self.do()
        while more:
            more, then = then.do()
        return then


    def do(self):
        if self.s:
            e, a = self.s.pop(0)
            return True, self.eval(e, a)
        else:
            p, g = self.m
            if cont := sched(p, g):
                return True, cont
        v = self.r.pop() if self.r else nil
        return False, v


def call(f, *args, env: Optional[Environment] = nil, then: Continuation = unset) -> Continuation:
    print("CALL", f, *args, then.r)
    then.then(f)
    # then.then([call2, *args], env)
    def calling(env: Environment, then: Continuation):
        f = then.pop()
        return then.then([call2, f, *args], env)
        # return call2(f, *args, env=env, then=then)
    then.then([calling])
    return then

import inspect

def call2(f, *args, env: Optional[Environment] = nil, then: Continuation = unset) -> Continuation:
    kws = {}
    try:
        sig = inspect.signature(f)
        params = sig.parameters
    except ValueError:
        params = {}
    if 'env' in params:
        kws['env'] = env
    if 'then' in params:
        kws['then'] = then
    v = f(*args, **kws)
    if isinstance(v, Continuation):
        return v
    then.push(v)
    return then


def do(*args, env: Optional[Environment] = nil, then: Continuation = unset) -> Continuation:
    print("DO", *args)
    if then is unset:
        then = Continuation()
    [*statements, tail] = args or [nil]
    for stmt in statements:
        then.then(stmt, env)
        then.then([discard], env)
    then.then(tail)
    return then

def discard(env: Environment, then: Continuation) -> Continuation:
    then.r.pop()
    return then


def now():
    import time
    return time.time()

class Timer(Event):
    def __init__(self, duration: float, value: Callable = lambda: True):
        super().__init__()
        self.when = now() + duration
        self.value = value

    def check(self):
        if now() >= self.when:
            return self.value()
        return super().check()

def timer(delay, value):
    # strike = time.time() + delay
    # return Wait(lambda: (value() if (now() >= strike) else lisper.unset))
    return Timer(delay, value)

def sched(p: ThreadsT, g: MutableMapping) -> Optional[Continuation]:
    if p:
        for i, (wait, s, r) in enumerate(p):
            if wait.ready():
                p = py.list(p)
                p.pop(i)
                return Continuation(s, r, (p, g))


def bel(e, globe: Dict = unset, scope: MutableMapping = unset):
    if globe is unset:
        globe = globals()
    if scope is unset:
        scope = Environment(globe, py.__dict__, protected=[globe, py.__dict__])
    k = Continuation([(e, scope)], [], ([], globe))
    return k.run()


