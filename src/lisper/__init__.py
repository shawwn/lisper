# read version from installed package
from importlib.metadata import version
__version__ = version(__name__)

del version

from typing import *
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_VT_co = TypeVar("_VT_co", covariant=True)
_T_co = TypeVar("_T_co", covariant=True)


import numbers
import builtins as py
import collections.abc as std
from functools import singledispatch as dispatch

t = True
nil = None
inf = float("inf")
nan = float("nan")

class Unset:
    def __bool__(self):
        return False
    def __repr__(self):
        return "unset"

unset = Unset()

@dispatch
def car(x):
    if x:
        return x[0]

@dispatch
def cdr(x):
    if x:
        return x[1:]

@dispatch
def cut(l, lo=nil, hi=nil):
    if l:
        return l[lo:hi]

def bound_narrow(lo, start):
    if lo is nil:
        return start
    if start is nil:
        return lo
    if lo >= 0 and start >= 0:
        return max(lo, start)
    if lo < 0 and start < 0:
        return min(lo, start)
    if lo < 0:
        return lo
    if start < 0:
        return start
    assert False

def minmax(x, *ys):
    if not ys:
        return x, x
    if x is nil:
        return minmax(*ys)
    lo, hi = x, x
    for y in ys:
        if y is nil:
            continue
        lo = min(lo, y)
        hi = max(hi, y)
    return lo, hi

def amin(*xs):
    lo, hi = minmax(*xs)
    return lo

def amax(*xs):
    lo, hi = minmax(*xs)
    return hi

def aabs(n):
    if n is not None:
        return abs(n)

def aadd(x, n):
    if x is nil:
        return n
    elif n is nil:
        return x
    else:
        return x + n

def aneg(x):
    if x is not nil:
        return -x

def possible(lo, hi):
    return minmax(
        aadd(lo, hi),
        aadd(lo, aneg(hi)),
        aadd(aneg(lo), hi),
        aadd(aneg(lo), aneg(hi)))

def normrange(l: range):
    lo, hi, by = unrange(l)
    assert lo >= 0
    assert hi >= 0
    assert by == 1
    if lo > hi:
        lo = hi
    return range(lo, hi, by)

def slice2range(l: slice, n: int, start=nil, stop=nil):
    # return range(*l.indices(n))[:][start:stop][:]
    return normrange(normrange(range(*l.indices(n)))[start:stop])

def slice2range(l: slice, n: int = nil):
    if n is not nil:
        l = normslice(l)
        return normrange(range(*l.indices(n)))
    lo, hi, by = unslice(l)
    return rerange(lo, hi, by)
    # if n is nil:
    #     n = l.stop - (l.start or 0)
    # return normrange(range(*l.indices(n)))

def range2slice(l: range):
    lo, hi, by = unrange(normrange(l))
    assert by == 1
    assert lo >= 0
    assert hi >= 0
    if lo > hi:
        lo = hi
    return slice(lo, hi, by)

def unrange(l: range):
    return l.start, l.stop, l.step

def rangeslice(l: range):
    return normslice(slice(*unrange(l)))

def slicerange(l: slice):
    return range(*unslice(normslice(l)))

def rerange(lo, hi, by):
    return normrange(range(lo, hi, by))

def slice_narrow(x: slice, start=nil, stop=nil, n=nil):
    lo, hi, by = unslice(x)
    assert by == 1
    lo = lo or 0
    start = start or 0
    assert ok(lo) and ok(hi)
    assert lo >= 0
    assert hi >= 0
    if lo > hi:
        lo = hi
    # assert hi >= lo
    if start == inf:
        return reslice(hi, hi, by)
    elif start == -inf:
        start = None
    if stop == inf:
        stop = None
    elif stop == -inf:
        return reslice(lo, lo, by)
    # r = slice2range(reslice(lo, hi, by), lo + hi, start, stop)
    r = slice2range(reslice(lo, hi, by), lo + hi)
    r = r[start:stop]
    r = normrange(r)
    bot, top, by = unrange(r)
    # bot, top, by = unrange(range(lo, hi)[start:stop])
    return slice(bot, top, by)

@cut.register(slice)
def cut_slice(x: slice, lo=nil, hi=nil):
    return slice_narrow(x, lo, hi)

@car.register(slice)
def car_slice(x: slice):
    lo, hi, by = unslice(slice_narrow(x))
    assert by == 1
    return lo or 0

@cdr.register(slice)
def cdr_slice(x: slice):
    return cut(x, 1)

def almost(x):
    return cut(x, nil, -1)

def inner(x):
    return cut(x, 1, -1)

def last(x):
    return car(cut(x, -1))

def join(a=nil, b=nil):
    if b:
        return a, *b
    else:
        return a,

def reduce1(f, x, ys):
    if ys:
        for y in ys:
            x = f(x, y)
    return x

def reduce(f, xs):
    if it := cdr(xs):
        return f(car(xs), reduce(f, it))
    else:
        return car(xs)

def list(*args, **kws):
    if kws:
        k, v = kws.popitem()
        return list(*args, ":" + k, v, **kws)
    return args

def at(l, k, *default):
    if isinstance(k, range):
        k = rangeslice(k)
        # k = slice(k.start, k.stop, k.step)
    if default:
        try:
            return l[k]
        except (LookupError, TypeError):
            return default[0]
    else:
        return l[k]

def locate(l, k):
    if table(l):
        l: dict
        if k in l:
            return l, k
    elif pair(l):
        l: tuple
        key = ":" + k
        if key in l:
            pos = l.index(key) + 1
            if pos < len(l):
                return l, pos

def ref(slot, *default):
    l, k = slot
    return at(l, k, *default)

def get(l, k, *default):
    if slot := locate(l, k):
        return at(*slot, *default)
    if default:
        return default[0]
    raise KeyError(k)

def snoc(*args):
    return append(car(args), cdr(args))

def append(*ls):
    out = []
    for l in ls:
        if l:
            out.extend(l)
    return list(*out)

def cons(*args):
    return reduce(join, args)

def mev(s, r, m):
    print(r)
    p, g = m
    if s:
        return sched(snoc(p, list(s, r)), g)
    elif p:
        return sched(p, g)
    else:
        return car(r)

def sched(p, g):
    (s, r), *p = p
    return ev(s, r, list(p, g))

def null(x):
    if x is nil:
        return t

def no(x):
    if x:
        return nil
    if x is False:
        return t
    return t

def ok(x):
    if null(x):
        return nil
    return t

def boolean(x):
    if isinstance(x, bool):
        return t

def pair(x):
    if isinstance(x, (tuple, py.list)):
        return t

def alit(x, *kind):
    if caris(x, "lit"):
        if kind:
            return mem(car(cdr(x)), kind)
        return t

def atom(x):
    if pair(x):
        return nil
    return t

def string(x):
    if isinstance(x, str):
        return t

def table(x):
    if isinstance(x, dict):
        return t

def number(x):
    if isinstance(x, numbers.Number):
        if boolean(x):
            return nil
        return t

def id(a, b):
    if string(a) or number(a):
        return equal(a, b)
    if a is b:
        return t

def equal(a, b):
    if a == b:
        return t

def caris(x, y, test=id):
    if pair(x):
        return test(car(x), y)

def pattern(x):
    if caris(x, "lit") and x[1] == "pat":
        return x[2]
    if identifier(x):
        x: str
        if len(x) > 1 and x[0] == "%":
            return x

def begins(xs, pat, test=id, captures=nil):
    if pat:
        if table(captures):
            if pattern(pat):
                pat: str
                captures[pat] = xs
            elif pair(pat) and (k := pattern(car(pat))):
                if car(cdr(pat)) == "...":
                    captures[car(pat)] = cdr(xs)
                    return t
                else:
                    captures[car(pat)] = car(xs)
                    return begins(cdr(xs), cdr(pat), test, captures)
        if atom(xs):
            return nil
        if test(car(xs), car(pat)):
            return begins(cdr(xs), cdr(pat), test, captures)
    else:
        return t

def begins(xs, pat, test=id):
    if not pat:
        return t
    if atom(xs):
        return nil
    if test(car(xs), car(pat)):
        return begins(cdr(xs), cdr(pat), test)

def begins2(xs, pat, test=id, pos=nil):
    if pos is nil:
        pos = range(max(len(xs), len(pat)))
    if not at(pat, pos):
        return t
    if not at(xs, pos):
        return nil
    if not ok(i := car(pos)):
        return nil
    if test(at(xs, i), at(pat, i)):
        return begins2(xs, pat, test, cdr(pos))

def inner(x):
    if x:
        return x[1:-1]

@dispatch
def iterate(x):
    if x:
        return iter(x)

@dispatch
def length(x, upto=-1):
    try:
        return len(x)
    except TypeError:
        try:
            i = -1
            if upto >= 0:
                for i, v in enumerate(x):
                    if i > upto:
                        break
            else:
                for i, v in enumerate(x):
                    pass
            return i + 1
        except TypeError:
            return -1

def stringlit(x):
    if string(x):
        if len(x) >= 2:
            if x[0] == '"' and x[-1] == '"':
                return "string"
            if x[0] == '|' and x[-1] == '|':
                return "code"
            if x[0] == "." and x[1] != ".":
                return "accessor"
            if x[0] == ":" and x[1] != ":":
                return "key"
        return "id"

def codelit(x):
    return in_(stringlit(x), "code")

def stringkind(x):
    if string(x):
        if stringlit(x):
            return "string"
        elif codelit(x):
            return "code"
        else:
            return "symbol"

def identifier(x):
    if id(stringlit(x), "id"):
        return t
    if begins(x, smark):
        return t

def literal(x):
    if identifier(x):
        return "sym"
    if caris(x, "lit"):
        return x[1]
    if pair(x):
        return nil
    return t

def variable(x):
    if identifier(x):
        return t

def ev(s, r, m):
    (e, a), *s = s
    if literal(e):
        return evlit(e, a, s, r, m)
    elif variable(e):
        return vref(e, a, s, r, m)
    else:
        return evcall(e, a, s, r, m)

def evlit(e, a, s, r, m):
    if begins(e, list("lit", "alias")):
        return mev(s, cons(last(e), r), m)
    if codelit(e):
        source = inner(e)
        try:
            code = compile(source, "<bel>", "eval")
            func = py.eval
        except SyntaxError:
            code = compile(source, "<bel>", "exec")
            func = py.exec
        global_ = Bindings(a, s, r, m)
        local = dict(__builtins__={})
        e = func(code, local, global_)
    return mev(s, cons(e, r), m)

def vref(e, a, s, r, m):
    if it := inwhere(s):
        new = car(it)
        if it := lookup(e, a, s, r, m, new):
            return mev(cdr(s), cons(it, r), m)
    else:
        # p, g = m
        # v = vget(g, e)
        # return mev(s, cons(v, r), m)
        if it := lookup(e, a, s, r, m):
            return mev(s, cons(ref(it), r), m)
    raise NameError(f"name {e!r} not defined")

# (set smark (join))
smark = globals().setdefault("smark", join("%smark"))

# (def inwhere (s)
#   (let e (car (car s))
#     (and (begins e (list smark 'loc))
#          (cddr e))))
def inwhere(s):
    e = car(car(s))
    if begins(e, list(smark, "loc")):
        return cdr(cdr(e))

def or_(x, *ys):
    if x is nil:
        return or_(*ys)

def in_(x, *ys, test=id):
    if ys:
        return mem(x, ys, test)

def bindings(s):
    if s:
        pat = list(smark, "bind")
        for (e, a) in s:
            if begins(e, pat, id):
                _, _, slot = pat
                yield slot

class Bindings(std.MutableMapping):
    def __init__(self, a, s, r, m):
        self.args = (a, s, r, m)
        # self.binds = py.list(bindings(s))
        # self.scope = a
        # self.globe = g

    def __setitem__(self, k: _KT, v: _VT) -> None:
        slot, k = lookup(k, *self.args, t)
        slot[k] = v

    def __delitem__(self, k: _KT) -> None:
        if it := lookup(k, *self.args, "del"):
            slot, k = it
            del slot[k]
        else:
            raise KeyError(k)

    def __getitem__(self, k: _KT) -> _VT_co:
        if it := lookup(k, *self.args):
            slot, k = it
            return slot[k]
        raise KeyError(k)

    def __len__(self) -> int:
        n = 0
        for slot in self:
            n += len(slot)
        return n

    def __iter__(self) -> Iterator[_T_co]:
        return binds(*self.args)

def binds(a, s, r, m, new=nil):
    for slot in bindings(s):
        yield slot
    if a:
        for slot in a:
            yield slot
    p, g = m
    yield g
    if not new:
        scope = a
        globe = g
        if g := get(g, "__bel__", globals()):
            if g is not globe:
                yield g
        if it := get(g, "__builtins__", py.__dict__):
            yield it
        meta = {"scope": scope,
                "globe": globe,
                "%other": p,
                "%stack": s,
                "%outer": r,
                "%cont": (s, r, m),
                }
        yield meta

def lookup(e, a, s, r, m, new=nil):
    for slot in binds(a, s, r, m, new):
        if it := locate(slot, e):
            return it
    if new:
        p, g = m
        if not id(new, "del"):
            if a:
                slot = last(a)
            else:
                slot = g
            slot[e] = nil
            return slot, e
    else:
        if id(e, "%env"):
            return {"%env": Bindings(a, s, r, m)}, e



# def lookup(e, a, s, r, m, new=nil):
#     if a:
#         for frame in a:
#             if it := locate(frame, e):
#                 return it
#     p, g = m
#     if new:
#         if not id(new, "del"):
#             frame = last(a) if a else g
#             frame[e] = nil
#             return frame, e
#     else:
#         if it := locate(g, e):
#             return it
#         if g := get(g, "__builtins__", nil):
#             if it := locate(g, e):
#                 return it
#         meta = {"%scope": a,
#                 "%globe": g,
#                 "%other": p,
#                 "%stack": s,
#                 "%outer": r,
#                 "%cont": (s, r, m),
#                 }
#         return locate(meta, e)

def vget(l, k):
    l: dict
    if k in l:
        return l[k]
    if g := l.get("__builtins__"):
        return vget(g, k)
    raise NameError(f"name {k!r} not defined")

# def evcall(e, a, s, r, m):
#     f, *args = e
#     # if identifier(f):
#     #     if it := get(forms, f, nil):
#     #         return it(args, a, s, r, m)
#     # if begins(f, list("lit", "form")):
#     #     return last(f)(args, a, s, r, m)
#     # if f == "do":
#     #     return do(args, a, s, r, m)
#     breakpoint()
#     raise NotImplementedError


def bel(e, g=nil, a=nil, tid=nil):
    g = g or globals()
    if a and not pair(a):
        a = list(a)
    return ev(list(list(e, a)),
              list(tid),
              list(list(), g))

def fu(*args):
    def inner(f):
        return list(smark, "fut", f, *args)
    return inner

def fut(f, env):
    def inner(*args):
        return list(fu(*args)(f), env)
        # return list(list(smark, "fut", f, *args), env)
    return inner

def future(env, *args):
    def inner(then):
        def f(es, a, s, r, m):
            return then(cons(car(r), es), a, s, cdr(r), m)
        # return fu(*args)(f)
        return fut(f, env)(*args)
    return inner


forms = globals().setdefault("forms", {})


# class Prim(py.tuple):
#     def __new__(cls, f):
#         return super().__new__(cls, list("lit", "prim", f))
#     def __call__(self, *args, **kwargs):
#         return self[2](*args, **kwargs)

def form(name):
    def inner(f):
        forms[name] = f
        # out = list("lit", "form", f)
        # globals()[name] = list("lit", "alias", out)
        # globals()[name] = out
        return f
    return inner

# (def evmark (e a s r m)
#   (case (car e)
#     fut  ((cadr e) s r m)
#     bind (mev s r m)
#     loc  (sigerr 'unfindable s r m)
#     prot (mev (cons (list (cadr e) a)
#                     (fu (s r m) (mev s (cdr r) m))
#                     s)
#               r
#               m)
#          (sigerr 'unknown-mark s r m)))
@form(smark)
def evmark(e, a, s, r, m):
    it = car(e)
    if id(it, "fut"):
        _, f, *args = e
        return f(args, a, s, r, m)
    if id(it, "bind"):
        return mev(s, r, m)
    raise ValueError(list("Unknown mark", e))

# (form quote ((e) a s r m)
#   (mev s (cons e r) m))
@form("quote")
def quote_form(es, a, s, r, m):
    return mev(s, cons(car(es), r), m)

@form("void")
def void(es, a, s, r, m):
    return mev(s, cdr(r), m)

# (form thread ((e) a s r (p g))
#   (mev s
#        (cons nil r)
#        (list (cons (list (list (list e a))
#                          nil)
#                    p)
#              g)))
@form("thread")
def thread(es, a, s, r, m):
    p, g = m
    name, *body = es
    parent = last(r)
    tid = snoc(parent, name)
    return mev(s,
               cons(tid, r),
               list(cons(list(list(list(cons("do", body), a)),
                              list(tid)),
                         p),
                    g))

@form("tid")
def thread(es, a, s, r, m):
    return mev(s, cons(last(r), r), m)

def mem(x, l, test=id):
    if l:
        for v in l:
            if test(v, x):
                return t

def map(f, *args):
    return py.tuple(py.map(f, *args))

def living(tids, s, r, m):
    if mem(last(r), tids):
        return t
    p, g = m
    for (s1, r1) in p:
        if mem(last(r1), tids):
            return t

@form("apply")
def apply_form(es, a, s, r, m):
    f, *args = es
    args = append(almost(args), last(args))
    return ev(cons(list(list("call", "list", *args), a),
                   list(fu(f, *args)(apply2), a),
                   s),
              r,
              m)

def apply2(es, a, s, r, m):
    f, args = car(es), car(r)
    breakpoint()
    return ev(cons(list(list("call", f, *args), a),
                   s),
              cdr(r),
              m)

@form("call")
def evcall(es, a, s, r, m):
    f, *args = es
    if identifier(f):
        if it := get(forms, f, nil):
            return it(args, a, s, r, m)
    # if caris(f, "lit") and id(car(cdr(f)), "fut"):
    #     _, _, f, *more = f
    #     if not callable(f):
    #         breakpoint()
    #     return f(append(args, more), a, s, r, m)
    return mev(cons(list(f, a),
                    list(fu(f, *args)(call2), a),
                    s),
               r,
               m)

def call2(es, a, s, r, m):
    f, args = car(r), cdr(es)
    breakpoint()
    if begins(f, list("lit", "form")):
        return last(f)(args, a, s, r, m)
    if begins(f, list(smark, "fut")):
        _, _, f, *more = f
        if callable(f):
            return f(append(args, more), a, s, r, m)
        breakpoint()
        return call2(append(list(f), args, more), a, s, r, m)
    #map(lambda e: list(e, a), args),
    return mev(cons(list(cons("list", args), a),
                    list(fu(f, *args)(call3), a),
                    s),
               cdr(r),
               m)

def call3(es, a, s, r, m):
    f, args = car(es), car(r)
    v = f(*args)
    return mev(s, cons(v, cdr(r)), m)

@form("list")
def list_form(es, a, s, r, m):
    return mev(append(map(lambda e: list(e, a), es),
                      list(list(fu(*es)(list2), a)),
                      s),
               r,
               m)

@dispatch
def rev(l):
    if l:
        return l[::-1]
    return l

def normslice(x: slice):
    lo, hi, by = x.start, x.stop, x.step
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
    return slice(lo, hi, by)

def unslice(x: slice):
    # x = normslice(x)
    return x.start, x.stop, x.step

def reslice(lo, hi, by):
    return normslice(slice(lo, hi, by))

def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0

def revslice(x: slice):
    lo, hi, by = unslice(normslice(x))
    assert by in [1, -1]
    if hi is not None:
        hi -= by
    if lo is not None:
        lo -= by
    return reslice(hi, lo, -by)

def checkslice(s, x: slice):
    return s[x][::-1], s[revslice(x)], revslice(x)

def testslice(s, x: slice):
    a, b, xr = checkslice(s, x)
    assert a == b, f"{a=}, {b=}. {x=}, {xr=}"
    return a, xr

def testslices(s):
    for lo in [None, 7, -7]:
        for hi in [None, 7, -7]:
            for by in [None, 1, -1]:
                testslice(s, slice(lo, hi, by))

testslices("abcdefghijklmnop")

def prn(*args, **kws):
    print(*args, **kws)
    return last(args)


# def slice2interval(x: slice):
#     # x = normslice(x)
#     lo, hi, by = x.start, x.stop, x.step
#     if by > 0:
#         return lo, hi, by
#     else:
#         if by == -1:
#             if lo == 0:
#                 lo = None
#             if hi == by:
#                 hi = None
#             lo, hi = hi, lo
#                 lo += 1
#                 if lo == 0:
#                     lo = None
#             if hi is not None:
#                 hi += 1
#                 if hi == 0:
#                     hi = None
#             lo, hi = hi, lo
#             if hi is not None:
#                 hi = -hi
#                 if hi < 0:
#
#             if lo is not None:
#                 lo -= 1
#             if hi is not None:
#                 hi -= 1
#             return lo, hi, -by
#         raise NotImplementedError



@rev.register(py.slice)
def rev_slice(x: slice):
    x = normslice(x)
    lo, hi, by = x.start, x.stop, x.step
    by = -by
    if by < 0 and lo == 0:
        lo, hi = hi, None
    elif by > 0 and hi == -1:
        lo, hi = None, lo
    else:
        lo, hi = hi, lo
    delta = 1 if by > 0 else -1
    if lo is not None:
        if lo < 0:
            lo += delta
        else:
            lo -= delta
    if hi is not None:
        if hi < 0:
            hi += delta
        else:
            hi -= delta
    return slice(lo, hi, by)

def snap(xs, ys, acc=nil):
    if not xs:
        return rev(acc), ys
    else:
        return snap(cdr(xs), cdr(ys), snoc(acc, car(ys)))

def list2(es, a, s, r, m):
    vs, r2 = snap(es, r)
    return mev(s, cons(vs, r2), m)

@form("idfn")
def tuple_form(es, a, s, r, m):
    e = car(es)
    return mev(cons(list(e, a),
                    s),
               r,
               m)



# @form("call")
# def call(es, a, s, r, m):
#     f, *args = es
#     @fu(f, *args)
#     def call2(es, a, s, r, m):
#         f, *args = es
#
#     name = last(r)
#     print(map(lambda e: bel(e, g, a, name), es)
#     return mev(s, cons(living(tids, s, r, m), r), m)
#
# @form("pr")
# def pr(es, a, s, r, m):
#     name = last(r)
#     print(map(lambda e: bel(e, g, a, name), es)
#     return mev(s, cons(living(tids, s, r, m), r), m)

@form("alive")
def alive(tids, a, s, r, m):
    return mev(s, cons(living(tids, s, r, m), r), m)

@form("wait")
def wait(tids, a, s, r, m):
    tid = last(r)
    return mev(s, cons(last(r), r), m)

@form("atomic")
def atomic(es, a, s, r, m):
    p, g = m
    e = cons("do", es)
    return mev(s,
               cons(bel(e, g, a, last(r)),
                    r),
               m)

@form("do")
def do(es, a, s, r, m):
    e, *es = es or (nil,)
    if es:
        return mev(append(list(list(e, a),
                               list(list("void"), a),
                               # # list(fu(es)(void), a),
                               list(cons("do", es), a),
                               # # list(fu(*es)(do), a),
                               # fut(void, a)(),
                               # fut(do, a)(*es),
                               ),
                          s), r, m)
    else:
        return mev(cons(list(e, a), s), r, m)

@form("if")
def if_form(es, a, s, r, m):
    """
    (form if (es a s r m)
      (if (no es)
          (mev s (cons nil r) m)
          (mev (cons (list (car es) a)
                     (if (cdr es)
                         (cons (fu (s r m)
                                 (if2 (cdr es) a s r m))
                               s)
                         s))
               r
               m)))"""
    if not es:
        return mev(s, cons(nil, r), m)
    else:
        return mev(cons(list(car(es), a),
                        if_(it := cdr(es),
                            lambda: cons(list(fu(*it)(if2), a), s),
                            lambda: s)()),
                   r,
                   m)

def if2(es, a, s, r, m):
    """
    (mev (cons (list (if (car r)
                       (car es)
                       (cons 'if (cdr es)))
                   a)
             s)
       (cdr r)
       m))"""
    return mev(cons(list(if_(car(r),
                             lambda: car(es),
                             lambda: cons("if", cdr(es)))(),
                         a),
                    s),
               cdr(r),
               m)

# (form where ((e (o new)) a s r m)
#   (mev (cons (list e a)
#              (list (list smark 'loc new) nil)
#              s)
#        r
#        m))
@form("where")
def where_form(es, a, s, r, m):
    e, new = car(es), car(cdr(es))
    return mev(cons(list(e, a),
                    list(list(smark, "loc", new), a),
                    s),
               r,
               m)

def if_(cond=nil, *args):
    if args:
        then, *args = args
        if cond:
            return then
        else:
            return if_(*args)
    else:
        return cond

# @form("or")
# def or_(es, a, s, r, m):
#     cond, es = car(es), cdr(es)
#     if es:
#         return mev(cons(list(cond, a),
#                         list(fu(*es)(or2), a),
#                         s),
#                    r,
#                    m)
#     else:
#         return mev(cons(list(cond, a),
#                         s),
#                    r,
#                    m)
#
# def or2(es, a, s, r, m):
#     cond, r = car(r), cdr(r)
#     if cond:
#         return mev(s, cons(cond, r), m)
#     else:
#         return mev(cons(list(cons("or", es), a),
#                         s),
#                    r,
#                    m)

@form("and")
def and_(es, a, s, r, m):
    cond, es = car(es), cdr(es)
    return mev(cons(list(cond, a),
                    list(fu(*es)(and2), a),
                    s),
               r,
               m)

def and2(es, a, s, r, m):
    cond, r = car(r), cdr(r)
    if not es or not cond:
        return mev(s, cons(cond, r), m)
    else:
        return mev(cons(list(cons("and", es), a),
                        s),
                   r,
                   m)
@form("or")
def or_(es, a, s, r, m):
    cond, es = car(es), cdr(es)
    return mev(cons(list(cond, a),
                    list(fu(*es)(or2), a),
                    s),
               r,
               m)

def or2(es, a, s, r, m):
    cond, r = car(r), cdr(r)
    if not es or cond:
        return mev(s, cons(cond, r), m)
    else:
        return mev(cons(list(cons("or", es), a),
                        s),
                   r,
                   m)
