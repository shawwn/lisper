from __future__ import annotations

import inspect
# read version from installed package
from importlib.metadata import version
__version__ = version(__name__)
del version

from typing import *
from functools import singledispatch as dispatch
import functools
import builtins as py
import numbers
import contextvars as CV

T = TypeVar("T")
T0 = TypeVar("T0")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")

t = True
nil = None
globe = globals()
inf = py.float("inf")
nan = py.float("nan")

if "unset" in globe:
    unset = globe["unset"]
else:
    class Unset:
        def __repr__(self):
            return "unset"
        def __bool__(self):
            return False
    unset = Unset()

def unbound(x):
    if x is unset:
        return t

def ok(x):
    if x is not nil:
        return t

def null(x):
    if x is nil:
        return t

# noinspection PyDefaultArgument
def defvar(name, value: T, globe=globe) -> T:
    return globe.setdefault(name, value)

# noinspection PyDefaultArgument
def defconst(name, value: T, globe=globe) -> T:
    globe[name] = value
    return value

def fuse(f, *args):
    # return apply(append, apply(map, f, args))
    return append(*map(f, *args))

@overload
def list() -> Tuple[None, ...]: ...
@overload
def list(t0: T0) -> Tuple[T0]: ...
@overload
def list(t0: T0, t1: T1) -> Tuple[T0, T1]: ...
@overload
def list(t0: T0, t1: T1, t2: T2) -> Tuple[T0, T1, T2]: ...
@overload
def list(t0: T0, t1: T1, t2: T2, t3: T3) -> Tuple[T0, T1, T2, T3]: ...
@overload
def list(*args: T, **kwargs) -> Tuple[T, ...]: ...
def list(*args, **kwargs):
    if kwargs:
        xs, ks = unlist(args)
        ks.update(kwargs)
        for k, v in ks.items():
            xs.extend((":" + k, v))
        # return append(*((":" + k, v) for k, v in {**ks, **kwargs}.items()), xs)
        return xs
    return args

# @dispatch
def keynom(x) -> Optional[py.str]:
    # if isinstance(x, py.str) and x.startswith(":") and (k := x[1:]): #.isidentifier():
    #     return k
    if isinstance(x, py.str) and x.startswith(":"):
        return x[1:]

# @dispatch
def askey(x):
    if isinstance(x, py.str):
        if x.startswith(":"):
            return x
        return ":" + x

def attrnom(x) -> Optional[py.str]:
    if isinstance(x, py.str) and x.startswith(".") and (k := x[1:]).isidentifier():
        return k

def asattr(x):
    if isinstance(x, py.str):
        if x.startswith("."):
            return x
        return "." + x

def defaults(default=unset):
    return default

@dispatch
def at(l, k, *default):
    try:
        if ok(a := attrnom(k)):
            return getattr(l, a, *default)
        else:
            return l[k]
    except (LookupError, TypeError, AttributeError):
        return defaults(*default)

@dispatch
def get(l, k):
    if integer(k):
        for pos, k2, i, v in iterate(l):
            if null(k2):
                if i >= k:
                    if i == k:
                        return l, pos
                    break
    elif index(k) and not integer(k):
        raise NotImplementedError
        # xs, ks = unlist(l)
        # return xs[k]
    else:
        for pos, k2, i, v in iterate(l):
            if k2 == k:
                return l, pos


class Foo:
    __slots__ = "a", "b"

class Bar:
    pass

@dispatch
def iterate(l, upto=nil) -> Generator[Tuple[py.int, Optional[py.str], py.int, T]]:
    inspect.getmembers_static


@iterate.register(py.list)
@iterate.register(py.tuple)
def iterate_seq(l: Iterable[T], upto=nil) -> Generator[Tuple[py.int, Optional[py.str], py.int, T]]:
    pos = -1
    i = -1
    if l:
        it = iter(l)
        try:
            while True:
                x = next(it)
                pos += 1
                if k := keynom(x):
                    x = next(it)
                    pos += 1
                else:
                    i += 1
                    if ok(upto) and i >= upto:
                        yield pos, k, i, x
                        break
                yield pos, k, i, x
        except StopIteration:
            return

@iterate.register(py.dict)
def iterate_dict(l: Dict, upto=nil):
    n = -1
    for k, x in l.items():
        if py.type(k) is py.int:
            n = py.max(k, n)
            if ok(upto) and n >= upto:
                break
        else:
            yield k, k, n, x
    n += 1
    for i in py.range(n):
        x = l[i] if i in l else unset
        yield i, nil, i, x

def unlist(l: Iterable[T]) -> Tuple[List[T], Dict[py.str, T]]:
    xs: List[T] = []
    ks: List[Tuple[py.str, T]] = []
    for pos, k, i, v in iterate(l):
        if k:
            ks.append(list(k, v))
        else:
            xs.append(v)
    return py.list(xs), py.dict(ks)

def relist(l):
    xs, ks = unlist(l)
    return list(*xs, **py.dict(ks))

def map(f, *args, keep=ok):
    xs = []
    ks: List[Dict[py.str, T]] = []
    for l in args:
        xs2, ks2 = unlist(l)
        xs.append(xs2)
        ks.append(ks2)
    kws = {}
    if ks:
        ks0 = ks[0]
        ks1 = ks[1:]
        for k in ks0.keys():
            if py.all(k in k1 for k1 in ks1):
                y = f(*([ks0[k]] + [k1[k] for k1 in ks1]))
                # if y is not nil:
                if keep is t or keep(y):
                    kws[k] = y
    vs = []
    for v in py.map(f, *xs):
        # if y is not nil:
        if keep is t or keep(v):
            vs.append(v)
    return list(*vs, **kws)

def append(*ls):
    r = []
    kws = {}
    for l in ls:
        if l:
            xs, ks = unlist(l)
            r.extend(xs)
            kws.update(ks)
    return list(*r, **kws)

def applyargs(*args):
    return append(args[0:-1], args[-1])

def apply(f, *args, **kws):
    args = applyargs(*args)
    return call(f, *args, **kws)

def call(f, *args, **kws):
    return f(*args, **kws)

def sequence(x):
    if isinstance(x, (py.tuple, py.list)):
        return t

# def atom(x):
#     if x and sequence(x):
#         return nil
#     return t

def atom(x):
    if sequence(x):
        return nil
    return t

def some(f, l):
    if l:
        if py.any(f(x) for x in l):
            return t
        # for x in l:
        #     if f(x):
        #         return t

def all(f, l):
    if l:
        if py.all(f(x) for x in l):
            return t
        # for x in l:
        #     if not f(x):
        #         return nil
        # return t

def number(x):
    if py.type(x) in (py.int, py.float):
        return t
    if isinstance(x, numbers.Number):
        return t

def car(x: Optional[Sequence[T]]) -> Optional[T]:
    if x:
        return x[0]

def cdr(x: T) -> T:
    if x:
        return x[1:]
    else:
        return x

def integer(k):
    if py.type(k) is py.int:
        return t

def index(k):
    if py.type(k) in (py.int, py.slice):
        return t

@dispatch
def update(l, k, v):
    l[k] = v
    return l

@update.register(py.tuple)
def update_tuple(l, k, v):
    cls = py.type(l)
    l = py.list(l)
    l = update(l, k, v)
    return cls(l)

@update.register(py.list)
def update_list(l: py.list, k, v):
    xs, ks = unlist(l)
    if index(k):
        xs[k] = v
    else:
        ks[k] = v
    l.clear()
    l.extend(list(*xs, **ks))
    return l


def length(l, upto=nil):
    if ok(upto):
        n = -1
        for pos, k, i, x in iterate(l):
            if i >= upto:
                break


def join(x=nil, y=nil):
    if y:
        return x, *y
    else:
        return x,

@dispatch
def composite(_x):
    return nil

@composite.register(numbers.Number)
@composite.register(py.str)
@composite.register(py.bytes)
@composite.register(py.bytearray)
@composite.register(py.memoryview)
def always(_x):
    return t

@composite.register(py.bool)
@composite.register(py.type(nil))
def never(_x):
    return nil

def id(a=nil, b=nil):
    if a is b:
        return t
    if composite(a) and composite(b):
        if a == b:
            return t

def eq(a=nil, b=nil):
    if composite(a) and composite(b):
        if a == b:
            return t
    else:
        if a is b:
            return t

def eqv(a=nil, *bs):
    if py.all(id(a, b) for b in bs):
        return t

def equal(*args):
    # print("equal", *args)
    if not cdr(args):
        return t
    elif some(atom, args):
        # x = car(args)
        # return all(lambda y: eqv(y, x), cdr(args))
        return eqv(*args)
    else:
        if equal(*map(len, args)):
            # if all(lambda x: equal(*x), zip(*args)):
            if py.all(equal(*x) for x in zip(*args)):
                return t
            # for x in zip(*args):
            #     if not equal(*x):
            #         return nil
            # return t
            # # if equal(*map(car, args)):
            # #     if equal(*map(cdr, args)):
            # #         return t

# def begins(xs, pat, test=nil):
#     test = test or id
#     if not pat:
#         return t
#     if atom(xs):
#         return nil
#     if not test(car(xs), car(pat)):
#         return nil
#     return begins(cdr(xs), cdr(pat), test=test)

def begins(xs, pat, test=nil):
    test = test or id
    while True:
        if not pat:
            return t
        if atom(xs):
            return nil
        if not test(car(xs), car(pat)):
            return nil
        xs = cdr(xs)
        pat = cdr(pat)


def caris(l, x, test=nil):
    return begins(l, list(x), test=test)

def compose2(f, g):
    @functools.wraps(g)
    def f_of_g(*args, **kws):
        return f(g(*args, **kws))
    f_of_g.__name__ = f.__name__ + ":" + g.__name__
    f_of_g.__qualname__ = f.__qualname__ + ":" + g.__qualname__
    return f_of_g

def compose(f, *gs):
    if not gs:
        return f
    else:
        return compose2(f, compose(*gs))

forms = defvar("forms", {})

def form(*names):
    def inner(f):
        for name in names:
            forms[name] = f
        return f
    return inner

@form("%do", "do")
def do_form():
    pass

# noinspection PyDefaultArgument
def bel(e, g=globe):
    return ev(list(list(e, list())),
              list(),
              list(list(), g))

def ev(s, r, m):
    (e, a), s = car(s), cdr(s)




