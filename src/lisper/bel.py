from .runtime import *

def no(x):
    if not x:
        return t

def all(f, xs):
    if no(xs):
        return t
    if f(car(xs)):
        return all(f, cdr(xs))

def some(f, xs):
    if no(xs):
        return nil
    if f(car(xs)):
        return xs
    return some(f, cdr(xs))

def reduce(f, xs):
    if no(cdr(xs)):
        return car(xs)
    return f(car(xs), reduce(f, cdr(xs)))

def cons(*args):
    return reduce(join, args)

def append(*ls):
    r = []
    for l in ls:
        if l:
            r.extend(l)
    return new(ls[0] if ls else nil, r)

def snoc(*args):
    return append(car(args), cdr(args))

def list(*args):
    return append(args, nil)

def map(f, *args):
    return list(*py.map(f, *args))

def char(x):
    if isinstance(x, py.str):
        return t

def symbol(x):
    return char(x)

def pair(x):
    if sequence(x):
        return t

def atom(x):
    if not sequence(x):
        return t

def and_(x=t, *args):
    if x:
        return x
    return and_(*args)

def equal(*args):
    if no(cdr(args)):
        return t
    if some(atom, args):
        return all(lambda y: id(y, car(args)), cdr(args))
    if equal(*map(car, args)):
        if equal(*map(cdr, args)):
            return t

def mem(x, ys, f=equal):
    return some(lambda y: f(y, x), ys)

def in_(x, *ys):
    return mem(x, ys)

def cadr(x):
    return car(cdr(x))

def cddr(x):
    return cdr(cdr(x))

def caddr(x):
    return car(cdr(cdr(x)))

def find(f, xs):
    if it := some(f, xs):
        return car(it)

def begins(xs, pat, f=equal):
    if no(pat):
        return t
    if atom(xs):
        return nil
    if f(car(xs), car(pat)):
        return begins(cdr(xs), cdr(pat), f)

def caris(x, y, f=equal):
    return begins(x, list(y), f)

def literal(e):
    if in_(e, t, nil, False):
        return t
    if number(e):
        return t
    if caris(e, "lit"):
        return t

vmark = globals().setdefault("vmark", join("%vmark"))

def variable(e):
    if atom(e):
        return no(literal(e))
    if id(car(e), vmark):
        return t

globe = list(globals(), py.__dict__)

def bel(e, g=globe):
    return ev(list(list(e, nil)),
              nil,
              list(nil, g))

def mev(s, r, m):
    p, g = car(m), cadr(m)
    if no(s):
        if p:
            return sched(p, g)
        else:
            return car(r)
    return sched(snoc(p, list(s, r)),
                 g)

def sched(p, g):
    (s, r), p = car(p), cdr(p)
    return ev(s, r, list(p, g))

def ev(s, r, m):
    (e, a), s = car(s), cdr(s)
    if literal(e):
        return evlit(e, a, s, r, m)
    if variable(e):
        return vref(e, a, s, r, m)
    if it := get(car(e), forms, id):
        return cadr(it)(cdr(e), a, s, r, m)
    return evcall(e, a, s, r, m)

def evlit(e, a, s, r, m):
    return mev(s, cons(e, r), m)

def vref(v, a, s, r, m):
    g = cadr(m)
    if it := lookup(v, a, s, g):
        return mev(s, cons(cadr(it), r), m)
    raise NameError(f"Unbound {v}")

def lookup(e, a, s, g):
    if it := get(e, a, id):
        return it
    if it := get(e, g, id):
        return it
    if id(e, "scope"):
        return list(e, a)
    if id(e, "globe"):
        return list(e, g)

def get(k, kvs, f=equal):
    if table(kvs):
        kvs: dict
        if in_(f, equal, id) and isinstance(k, std.Hashable):
            if k in kvs:
                return list(kvs, kvs[k])
        else:
            for key, v in kvs.items():
                if f(key, k):
                    return list(kvs, v)
    elif isinstance(kvs, (py.tuple, py.list)):
        for l in kvs:
            if it := get(k, l, f):
                return it
    else:
        return find(lambda l: f(car(l), k), kvs)

def rev(xs):
    if xs:
        return xs[::-1]

def snap(xs, ys, acc=nil):
    if no(xs):
        return list(acc, ys)
    else:
        return snap(cdr(xs), cdr(ys), snoc(acc, car(ys)))

smark = globals().setdefault("smark", join("%smark"))

def fu(f):
    return list(list(smark, "fut", f), nil)

def evmark(e, a, s, r, m):
    k = car(e)
    if k == "fut":
        return cadr(e)(s, r, m)
    raise NotImplementedError("Unknown mark")

forms = {smark: evmark}

def form(*names):
    def inner(f):
        for name in names:
            forms[name] = f
        return f
    return inner

@form("quote")
def quote_form(es, a, s, r, m):
    e = car(es)
    return mev(s, cons(e, r), m)

@form("if")
def if_form(es, a, s, r, m):
    if no(es):
        return mev(s, cons(nil, r), m)
    args = list(car(es), a)
    if cdr(es):
        @fu
        def if2_fut(s, r, m):
            return if2(cdr(es), a, s, r, m)
        return mev(cons(args, if2_fut, s), r, m)
    else:
        return mev(cons(args, s), r, m)

def if2(es, a, s, r, m):
    e = car(es) if car(r) else cons("if", cdr(es))
    return mev(cons(list(e, a), s), cdr(r), m)

def evcall(e, a, s, r, m):
    return mev(cons(list(car(e), a),
                    fu(lambda s, r, m: evcall2(cdr(e), a, s, r, m)),
                    s),
               r,
               m)

def evcall2(es, a, s, r, m):
    op, r = car(r), cdr(r)
    @fu
    def evcall3(s, r, m):
        args, r2 = snap(es, r)
        return applyf(op, rev(args), a, s, r2, m)
    return mev(append(map(lambda _: list(_, a), es),
                      cons(evcall3, s)),
               r,
               m)

def applyf(f, args, a, s, r, m):
    if callable(f):
        return mev(s, cons(f(*args), r), m)
    raise NotImplementedError

import operator

globals()["+"] = operator.add
globals()["-"] = operator.sub
globals()["*"] = operator.mul
globals()["/"] = operator.truediv
globals()["//"] = operator.floordiv

# >>> bel(["len", ["quote", [1, 2, 3]]])
# 3
# >>> bel(["*", 2, ["+", 1, 3]])
# 8