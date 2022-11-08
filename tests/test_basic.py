import unittest

from lisper.types import *
import lisper


if TYPE_CHECKING:
    from lisper.dispatch import *

    # @singledispatch
    def foo(x: int) -> str:
        return x
    foo = SingleDispatch(foo)
    foo
    foo("omg")

    class Foo:
        def foo(self, x: int) -> str:
            return x

        def bar(self, x: int) -> str:
            return x

    Foo.foo = singledispatchmethod(Foo.foo)

    f = Foo()
    f.bar("ok")

    zz = Foo().foo("hi")
    zz
    zza = Foo().foo(1)
    zza
    zzb = Foo().foo(1, "ok")
    zzb
    zz3 = foo("hi")
    zz3
    zz4 = foo(1)
    zz4

class TestCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
