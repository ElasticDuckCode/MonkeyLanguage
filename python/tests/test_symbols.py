from unittest import TestCase

from src.monkey import symbols


class TestSymbols(TestCase):
    def test_define_global(self):
        expected = {
            "a": symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            "b": symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
        }

        g = symbols.Table()

        a = g.define("a")
        self.assertEqual(a, expected["a"])

        b = g.define("b")
        self.assertEqual(b, expected["b"])

    def test_define_local(self):
        expected = {
            "a": symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            "b": symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
            "c": symbols.Symbol("c", symbols.LOCAL_SCOPE, 0),
            "d": symbols.Symbol("d", symbols.LOCAL_SCOPE, 1),
            "e": symbols.Symbol("e", symbols.LOCAL_SCOPE, 0),
            "f": symbols.Symbol("f", symbols.LOCAL_SCOPE, 1),
        }

        g = symbols.Table()
        a = g.define("a")
        self.assertEqual(a, expected["a"])
        b = g.define("b")
        self.assertEqual(b, expected["b"])

        l1 = symbols.Table(g)
        c = l1.define("c")
        self.assertEqual(c, expected["c"])
        d = l1.define("d")
        self.assertEqual(d, expected["d"])

        l2 = symbols.Table(l1)
        e = l2.define("e")
        self.assertEqual(e, expected["e"])
        f = l2.define("f")
        self.assertEqual(f, expected["f"])

    def test_resolve_global(self):
        expected = [
            symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
        ]

        g = symbols.Table()
        g.define("a")
        g.define("b")

        for sym in expected:
            result = g.resolve(sym.name)
            self.assertIsNotNone(result)
            self.assertEqual(result, sym)

    def test_resolve_local(self):
        expected1 = [
            symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
            symbols.Symbol("c", symbols.LOCAL_SCOPE, 0),
            symbols.Symbol("d", symbols.LOCAL_SCOPE, 1),
        ]
        expected2 = [
            symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
            symbols.Symbol("e", symbols.LOCAL_SCOPE, 0),
            symbols.Symbol("f", symbols.LOCAL_SCOPE, 1),
        ]
        gt = symbols.Table()
        gt.define("a")
        gt.define("b")

        lt1 = symbols.Table(gt)
        lt1.define("c")
        lt1.define("d")

        lt2 = symbols.Table(lt1)
        lt2.define("e")
        lt2.define("f")

        for sym in expected1:
            result = lt1.resolve(sym.name)
            self.assertIsNotNone(result)
            self.assertEqual(result, sym)

        for sym in expected2:
            result = lt2.resolve(sym.name)
            self.assertIsNotNone(result)
            self.assertEqual(result, sym)
