from copy import deepcopy
import os
import re
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
from build_migrator.common.argument_parser_ex import ArgumentParserEx  # noqa: E402


class TestArgumentParserEx(base.TestBase):
    def test_compatiblity_arguments(self):
        # test ArgumentParser interface compatibility
        # these arguments are simply ignored
        parser = ArgumentParserEx(
            prog="test",
            usage="usage",
            description="description",
            epilog="epilog",
            parents=[],
            formatter_class=object,
            fromfile_prefix_chars="fromfile_prefix_chars",
            argument_default=None,
            conflict_handler="error",
            add_help=True,
        )
        parser.add_argument("-a", help="help", metavar="metavar")
        ns = parser.parse_args(["-a1"])
        self.assertEqual("1", ns.a)

    def test_action_default(self):
        parser = ArgumentParserEx()
        parser.add_argument("attr1")
        parser.add_argument("--attr2")

        ns, remaining = parser.parse_known_args(["--attr2", "val1", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual("val2", ns.attr1)
        self.assertEqual("val1", ns.attr2)

    def test_action_store_optional(self):
        parser = ArgumentParserEx()
        parser.add_argument("--attr", "-a", action="store")

        ns, remaining = parser.parse_known_args(["-aval"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr)

        ns, remaining = parser.parse_known_args(["-a", "val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr)

        ns, remaining = parser.parse_known_args(["-a-val"])
        self.assertListEqual([], remaining)
        self.assertEqual("-val", ns.attr)

        ns, remaining = parser.parse_known_args(["-a", "-val"])
        self.assertListEqual([], remaining)
        self.assertEqual("-val", ns.attr)

        ns, remaining = parser.parse_known_args(["--attr=val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr)

        ns, remaining = parser.parse_known_args(["--attr", "val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr)

        ns, remaining = parser.parse_known_args(["--attr=-val"])
        self.assertListEqual([], remaining)
        self.assertEqual("-val", ns.attr)

        ns, remaining = parser.parse_known_args(["--attr", "-val"])
        self.assertListEqual([], remaining)
        self.assertEqual("-val", ns.attr)

        ns, remaining = parser.parse_known_args(["--attrval"])
        self.assertListEqual(["--attrval"], remaining)
        self.assertIsNone(vars(ns).get("attr"))

    def test_action_store_positional(self):
        parser = ArgumentParserEx()
        parser.add_argument("attr", action="store")

        ns, remaining = parser.parse_known_args(["-val"])
        self.assertListEqual(["-val"], remaining)
        self.assertIsNone(vars(ns).get("attr"))

        ns, remaining = parser.parse_known_args(["val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr)

    def test_action_store_override(self):
        parser = ArgumentParserEx()
        parser.add_argument("attr1", action="store")
        parser.add_argument("--attr2", action="store")

        ns, remaining = parser.parse_known_args(["val1", "--attr2", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual("val1", ns.attr1)
        self.assertEqual("val2", ns.attr2)

        ns, remaining = parser.parse_known_args(["--attr2", "val2", "val1"])
        self.assertListEqual([], remaining)
        self.assertEqual("val1", ns.attr1)
        self.assertEqual("val2", ns.attr2)

        ns, remaining = parser.parse_known_args(
            ["--attr2", "val1", "val2", "--attr2", "val3"]
        )
        self.assertListEqual([], remaining)
        self.assertEqual("val2", ns.attr1)
        self.assertEqual("val3", ns.attr2)

    def test_nargs(self):
        parser = ArgumentParserEx()
        parser.add_argument("--attr2", action="store", nargs="1")
        parser.add_argument("attr1", action="store", nargs="1")

        ns, remaining = parser.parse_known_args(
            ["--attr2", "val1", "val2", "--attr2", "val3"]
        )
        self.assertListEqual([], remaining)
        self.assertEqual(["val2"], ns.attr1)
        self.assertEqual(["val3"], ns.attr2)

        parser = ArgumentParserEx()
        parser.add_argument("--attr2", action="store", nargs="2")
        parser.add_argument("attr1", action="store", nargs="2")

        ns, remaining = parser.parse_known_args(
            ["--attr2", "val1", "val2", "val3", "val4"]
        )
        self.assertListEqual([], remaining)
        self.assertEqual(["val3", "val4"], ns.attr1)
        self.assertEqual(["val1", "val2"], ns.attr2)

        ns, remaining = parser.parse_known_args(
            ["val1", "val2", "--attr2", "val3", "val4", "val5"]
        )
        self.assertListEqual(["val5"], remaining)
        self.assertEqual(["val1", "val2"], ns.attr1)
        self.assertEqual(["val3", "val4"], ns.attr2)

        ns, remaining = parser.parse_known_args(["val1", "--attr2", "val2"])
        self.assertListEqual(["--attr2"], remaining)
        self.assertEqual(["val1", "val2"], ns.attr1)
        self.assertIsNone(vars(ns).get("attr2"))

        ns, remaining = parser.parse_known_args(
            ["val1", "--attr2", "val2", "val3", "val4"]
        )
        self.assertListEqual([], remaining)
        self.assertEqual(["val1", "val4"], ns.attr1)
        self.assertEqual(["val2", "val3"], ns.attr2)

        ns, remaining = parser.parse_known_args(["val1", "--attr2", "val2", "val3"])
        self.assertListEqual([], remaining)
        self.assertEqual(["val1"], ns.attr1)
        self.assertEqual(["val2", "val3"], ns.attr2)

        parser = ArgumentParserEx()
        parser.add_argument("attr1", action="store", nargs="?")
        parser.add_argument("--attr2", action="store", nargs="?")

        ns, remaining = parser.parse_known_args(["val1", "--attr2"])
        self.assertListEqual([], remaining)
        self.assertEqual(["val1"], ns.attr1)
        self.assertEqual([], ns.attr2)

        ns, remaining = parser.parse_known_args(["--attr2", "val1"])
        self.assertListEqual([], remaining)
        self.assertEqual(None, ns.attr1)
        self.assertEqual(["val1"], ns.attr2)

        parser = ArgumentParserEx()
        parser.add_argument("--attr2", action="store", nargs="+")
        parser.add_argument("attr1", action="store", nargs="+")

        ns, remaining = parser.parse_known_args(["val1", "val2", "--attr2"])
        self.assertListEqual(["--attr2"], remaining)
        self.assertEqual(["val1", "val2"], ns.attr1)
        self.assertIsNone(vars(ns).get("attr2"))

        ns, remaining = parser.parse_known_args(["--attr2", "val1", "val2"])
        self.assertListEqual([], remaining)
        self.assertIsNone(vars(ns).get("attr1"))
        self.assertEqual(["val1", "val2"], ns.attr2)

        ns, remaining = parser.parse_known_args(["val1", "val2", "--attr2", "val3"])
        self.assertListEqual([], remaining)
        self.assertEqual(["val1", "val2"], ns.attr1)
        self.assertEqual(["val3"], ns.attr2)

        parser = ArgumentParserEx()
        parser.add_argument("attr1", action="store", nargs="*")
        parser.add_argument("--attr2", action="store", nargs="*")

        ns, remaining = parser.parse_known_args(["val1", "val2", "--attr2"])
        self.assertListEqual([], remaining)
        self.assertEqual(["val1", "val2"], ns.attr1)
        self.assertEqual([], ns.attr2)

        ns, remaining = parser.parse_known_args(["--attr2", "val1", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual([], ns.attr1)
        self.assertEqual(["val1", "val2"], ns.attr2)

        ns, remaining = parser.parse_known_args(["val1", "--attr2", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual(["val1"], ns.attr1)
        self.assertEqual(["val2"], ns.attr2)

        parser = ArgumentParserEx()
        parser.add_argument("-C", action="append", nargs="?")
        ns = parser.parse_args(["-C", "a1", "-C"])
        self.assertListEqual([["a1"], []], ns.C)

        parser = ArgumentParserEx()
        parser.add_argument("-C", action="append", nargs="*")
        ns = parser.parse_args(["-C", "a1", "-C", "b1", "b2", "-C"])
        self.assertListEqual([["a1"], ["b1", "b2"], []], ns.C)

        parser = ArgumentParserEx()
        parser.add_argument("-C", action="append", nargs="+")
        ns = parser.parse_args(["-C", "a1", "-C", "b1", "b2"])
        self.assertListEqual([["a1"], ["b1", "b2"]], ns.C)

        parser = ArgumentParserEx()
        parser.add_argument("C", action="append", nargs="?")
        ns = parser.parse_args(["1"])
        self.assertListEqual([["1"]], ns.C)
        ns, remaining = parser.parse_known_args(["1", "2"])
        self.assertListEqual(["2"], remaining)
        self.assertListEqual([["1"]], ns.C)
        ns = parser.parse_args([])
        self.assertIsNone(ns.C)

        parser = ArgumentParserEx()
        parser.add_argument("C", action="append", nargs="*")
        ns = parser.parse_args(["1"])
        self.assertListEqual([["1"]], ns.C)
        ns = parser.parse_args(["1", "2"])
        self.assertListEqual([["1", "2"]], ns.C)
        ns, _remaining = parser.parse_known_args(["1", "2", "-a", "3"])
        self.assertListEqual([["1", "2"], ["3"]], ns.C)
        ns, _remaining = parser.parse_known_args(["1", "2", "-a"])
        self.assertListEqual([["1", "2"]], ns.C)
        # Check that empty list does not raise an Exception
        parser.parse_args([])

        parser = ArgumentParserEx()
        parser.add_argument("C", action="append", nargs="+")
        ns = parser.parse_args(["1"])
        self.assertListEqual([["1"]], ns.C)
        ns = parser.parse_args(["1", "2"])
        self.assertListEqual([["1", "2"]], ns.C)
        ns, _remaining = parser.parse_known_args(["1", "2", "-a", "3"])
        self.assertListEqual([["1", "2"], ["3"]], ns.C)
        ns, _remaining = parser.parse_known_args(["1", "2", "-a"])
        self.assertListEqual([["1", "2"]], ns.C)
        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )

    def test_prefix_chars(self):
        parser = ArgumentParserEx(prefix_chars="/-")
        parser.add_argument("-attr1", action="store")

        ns, remaining = parser.parse_known_args(["/attr1", "val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr1)

        ns, remaining = parser.parse_known_args(["-attr1", "val"])
        self.assertListEqual([], remaining)
        self.assertEqual("val", ns.attr1)

        parser.set(prefix_chars="+")
        parser.add_argument("+attr2", action="store")

        ns, remaining = parser.parse_known_args(["-attr1", "val1", "+attr2", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual("val1", ns.attr1)
        self.assertEqual("val2", ns.attr2)

        ns, remaining = parser.parse_known_args(["/attr1", "val1", "+attr2", "val2"])
        self.assertListEqual([], remaining)
        self.assertEqual("val1", ns.attr1)
        self.assertEqual("val2", ns.attr2)

        ns, remaining = parser.parse_known_args(["+attr1", "val1", "-attr2", "val2"])
        self.assertListEqual(["+attr1", "val1", "-attr2", "val2"], remaining)
        self.assertIsNone(vars(ns).get("attr1"))
        self.assertIsNone(vars(ns).get("attr2"))

    def test_action_store_const(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="store_const", const="a")

        ns, remaining = parser.parse_known_args([])
        self.assertListEqual([], remaining)
        self.assertIsNone(vars(ns).get("a"))

        ns, remaining = parser.parse_known_args(["-a"])
        self.assertListEqual([], remaining)
        self.assertEqual("a", ns.a)

        parser = ArgumentParserEx()
        parser.add_argument("-a", action="store_const", const="a", default="b")

        ns, remaining = parser.parse_known_args([])
        self.assertListEqual([], remaining)
        self.assertEqual("b", ns.a)

    def test_action_store_true(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="store_true")

        ns, remaining = parser.parse_known_args([])
        self.assertListEqual([], remaining)
        self.assertFalse(ns.a)

        ns, remaining = parser.parse_known_args(["-a"])
        self.assertListEqual([], remaining)
        self.assertTrue(ns.a)

    def test_action_store_false(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="store_false")

        ns, remaining = parser.parse_known_args([])
        self.assertListEqual([], remaining)
        self.assertTrue(ns.a)

        ns, remaining = parser.parse_known_args(["-a"])
        self.assertListEqual([], remaining)
        self.assertFalse(ns.a)

    def test_action_append(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="append")

        ns, remaining = parser.parse_known_args(["-a1", "-a2"])
        self.assertListEqual([], remaining)
        self.assertEqual(["1", "2"], ns.a)

        ns, remaining = parser.parse_known_args(["-a", "2", "-a", "1"])
        self.assertListEqual([], remaining)
        self.assertEqual(["2", "1"], ns.a)

        parser.add_argument("b", action="append")

        ns, remaining = parser.parse_known_args(["-a", "1", "2", "-a", "3"])
        self.assertListEqual([], remaining)
        self.assertEqual(["1", "3"], ns.a)
        self.assertEqual(["2"], ns.b)

    def test_action_append_const(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="append_const", const="v")

        ns, remaining = parser.parse_known_args(["-a", "1", "-a2", "-a"])
        self.assertListEqual(["1", "-a2"], remaining)
        self.assertEqual(["v", "v"], ns.a)

    def test_type_conversion(self):
        parser = ArgumentParserEx()
        parser.add_argument("--a1", type=int)
        # disable prefix chars to allow negative numbers as positional arguments
        parser.set(prefix_chars="")
        parser.add_argument("a2", type=float)

        ns, remaining = parser.parse_known_args(["--a1", "h", "0.1"])
        self.assertListEqual(["--a1", "h"], remaining)
        self.assertIsNone(vars(ns).get("a1"))
        self.assertEqual(0.1, ns.a2)

        ns, remaining = parser.parse_known_args(["-1", "--a1=123"])
        self.assertListEqual([], remaining)
        self.assertEqual(123, ns.a1)
        self.assertEqual(-1, ns.a2)

        ns, remaining = parser.parse_known_args(["--a1", "-5", "-1"])
        self.assertListEqual([], remaining)
        self.assertEqual(-5, ns.a1)
        self.assertEqual(-1, ns.a2)

    def test_choices(self):
        parser = ArgumentParserEx()
        parser.add_argument("--a1", choices=["abc", "ab", "a"])
        parser.add_argument("a2", choices=["def", "ef"])

        ns, remaining = parser.parse_known_args(["--a1=abc", "de"])
        self.assertListEqual(["de"], remaining)
        self.assertEqual("abc", ns.a1)
        self.assertIsNone(vars(ns).get("a2"))

        ns, remaining = parser.parse_known_args(["--a1", "abc", "de"])
        self.assertListEqual(["de"], remaining)
        self.assertEqual("abc", ns.a1)
        self.assertIsNone(vars(ns).get("a2"))

        ns, remaining = parser.parse_known_args(["--a1", "b", "def"])
        self.assertListEqual(["--a1", "b"], remaining)
        self.assertIsNone(vars(ns).get("a1"))
        self.assertEqual("def", ns.a2)

    def test_strict_parsing(self):
        parser = ArgumentParserEx()
        parser.add_argument("arg1")

        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["--option"]
        )
        ns = parser.parse_args(["val"])
        self.assertEqual("val", ns.arg1)

        parser = ArgumentParserEx()
        parser.add_argument("--arg1", "-a", required=True)

        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["--arg1="]
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["-a"]
        )
        ns = parser.parse_args(["-aval"])
        self.assertEqual("val", ns.arg1)

        parser = ArgumentParserEx()
        parser.add_argument("arg1", nargs=2)

        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        self.assertRaisesRegexp(
            ValueError, "Not enough values", parser.parse_args, ["a"]
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["a", "b", "c"]
        )
        ns = parser.parse_args(["a", "b"])
        self.assertEqual(["a", "b"], ns.arg1)

        parser = ArgumentParserEx()
        parser.add_argument("--arg1", "-a", required=True, nargs=2)

        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["--arg1", "val"]
        )
        self.assertRaisesRegexp(
            ValueError, "Unparsed tokens", parser.parse_args, ["-a", "val"]
        )
        ns = parser.parse_args(["--arg1", "a", "b"])
        self.assertEqual(["a", "b"], ns.arg1)

    def test_default_values(self):
        parser = ArgumentParserEx()
        parser.add_argument("arg1", default="default")

        ns = parser.parse_args([])
        self.assertEqual("default", ns.arg1)

        ns = parser.parse_args(["value"])
        self.assertEqual("value", ns.arg1)

        parser = ArgumentParserEx()
        parser.add_argument("-a", default=[], action="append")

        ns = parser.parse_args([])
        self.assertEqual([], ns.a)

        ns.a.append("value")

        ns = parser.parse_args([])
        self.assertEqual([], ns.a)

        ns = parser.parse_args(["-aval"])
        self.assertEqual(["val"], ns.a)

    def test_intermixed_args(self):
        parser = ArgumentParserEx()
        parser.add_argument("files", action="append")
        parser.add_argument("-D", action="append", dest="definitions")
        ns = parser.parse_args(["-DA=1", "a.cpp", "-DB=2", "b.cpp"])
        # standard ArgumentParser won't append 'b.cpp' here
        self.assertListEqual(["a.cpp", "b.cpp"], ns.files)
        self.assertListEqual(["A=1", "B=2"], ns.definitions)

    def test_shortening(self):
        parser = ArgumentParserEx()
        parser.add_argument("--abc")
        parser.add_argument("--a")
        # standard ArgumentParser will parse --ab as --abc
        ns, remaining = parser.parse_known_args(["--abc", "1", "--ab", "2", "--a", "3"])
        self.assertListEqual(["--ab", "2"], remaining)
        self.assertEqual("1", ns.abc)
        self.assertEqual("3", ns.a)

    def test_dest_is_none(self):
        parser = ArgumentParserEx()
        parser.add_argument("-opt", dest=None, required=True)
        parser.add_argument("pos", dest=None)

        ns = parser.parse_args(["-opt", "1", "2"])
        self.assertIsNone(vars(ns).get("opt"))
        self.assertIsNone(vars(ns).get("pos"))

        ns, remaining = parser.parse_known_args(["-opt"])
        self.assertListEqual(["-opt"], remaining)

        ns, remaining = parser.parse_known_args(["1"])
        self.assertListEqual([], remaining)
        self.assertIsNone(vars(ns).get("opt"))
        self.assertIsNone(vars(ns).get("pos"))

        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, ["1"]
        )

    def test_values_starting_with_prefix(self):
        # standard ArgumentParser does not accept values starting with prefix_chars

        parser = ArgumentParserEx()
        parser.add_argument("-Xclang")
        ns = parser.parse_args(["-Xclang", "-no-color-output"])
        self.assertEqual("-no-color-output", ns.Xclang)

        parser = ArgumentParserEx()
        parser.add_argument("-f", nargs="2")
        ns = parser.parse_args(["-f", "-1", "-2"])
        self.assertListEqual(["-1", "-2"], ns.f)

        parser = ArgumentParserEx()
        parser.add_argument("-f", nargs="2", action="append")
        parser.add_argument("--enable", action="store_true")
        ns = parser.parse_args(["-f", "-1", "-2"])
        self.assertListEqual([["-1", "-2"]], ns.f)
        parser.add_argument("-f", nargs="2", action="append")
        ns = parser.parse_args(["-f", "-1", "-2", "-f", "-3", "-4"])
        self.assertListEqual([["-1", "-2"], ["-3", "-4"]], ns.f)
        ns, remaining = parser.parse_known_args(["-f", "-1", "-2", "-f", "-3"])
        self.assertListEqual(["-f", "-3"], remaining)
        self.assertListEqual([["-1", "-2"]], ns.f)
        ns, remaining = parser.parse_known_args(
            ["-f", "-1", "-2", "-f", "-3", "--enable", "-4"]
        )
        self.assertListEqual(["-4"], remaining)
        self.assertListEqual([["-1", "-2"], ["-3", "--enable"]], ns.f)
        self.assertFalse(ns.enable)
        self.assertRaisesRegexp(
            ValueError,
            "Unparsed tokens",
            parser.parse_args,
            ["-f", "-1", "-2", "-f", "-3"],
        )

        parser = ArgumentParserEx()
        parser.add_argument("f", nargs="*")
        ns, remaining = parser.parse_known_args(["-1"])
        self.assertListEqual(["-1"], remaining)
        ns, remaining = parser.parse_known_args(["1", "2", "-3"])
        self.assertListEqual(["-3"], remaining)
        self.assertListEqual(["1", "2"], ns.f)
        ns, remaining = parser.parse_known_args(["1", "-2", "3"])
        self.assertListEqual(["-2"], remaining)
        self.assertListEqual(["1", "3"], ns.f)

        parser = ArgumentParserEx()
        parser.add_argument("f", nargs="+")
        ns, remaining = parser.parse_known_args(["-1", "-2"])
        self.assertListEqual(["-1", "-2"], remaining)

        parser = ArgumentParserEx()
        parser.add_argument("-f", nargs="+")
        ns, remaining = parser.parse_known_args(["-f", "-1", "-2"])
        self.assertListEqual(["-2"], remaining)
        self.assertListEqual(["-1"], ns.f)

    def test_multicharacter_short_flag_disables_suffix_value(self):
        parser = ArgumentParserEx()
        parser.add_argument("-Xclang")
        ns, remaining = parser.parse_known_args(["-Xclangvalue"])
        self.assertListEqual(["-Xclangvalue"], remaining)
        self.assertIsNone(vars(ns).get("Xclang"))

    def test_force_suffix_value(self):
        parser = ArgumentParserEx()
        parser.add_argument(prefixes=["-Xclang"])
        ns = parser.parse_args(["-Xclangvalue"])
        self.assertEqual("value", ns.Xclang)

        parser = ArgumentParserEx()
        parser.add_argument("-Xclang", prefix=True)
        ns = parser.parse_args(["-Xclangvalue"])
        self.assertEqual("value", ns.Xclang)

    def test_correct_list_order(self):
        parser = ArgumentParserEx(prefix_chars="-/")
        parser.set_defaults(definitions=[])
        parser.add_argument("/c", action="store_true", dest="compile_only")
        parser.add_argument("-D", action="append", dest="definitions")
        parser.add_argument("-I", action="append", dest="include_dirs")
        parser.add_argument("-U", action="append", dest="definitions")
        parser.add_argument("files", nargs="*")
        ns = parser.parse_args(["/c", "-D1", "/U", "2", "/D3", "-I.", "-U4", "a.cpp"])
        self.assertListEqual(["1", "2", "3", "4"], ns.definitions)

    def test_no_prefix_chars(self):
        parser = ArgumentParserEx()
        parser.add_argument("-D", action="append", dest="definitions")
        parser.add_argument(
            flags=["cmd"],
            action="append",
            nargs="+",
            dest="commands",
            args_regexp=re.compile(r"^(?!cmd)"),
        )
        ns = parser.parse_args(["-DA=1", "cmd", "cl.exe", "cmd", "gcc", "/c", "a.cpp"])
        self.assertListEqual(["A=1"], ns.definitions)
        self.assertListEqual([["cl.exe"], ["gcc", "/c", "a.cpp"]], ns.commands)

    def test_case_insensitive_windows_style(self):
        parser = ArgumentParserEx(prefix_chars="/")
        parser.add_argument("/nologo", action="store_true", ignore_case=True)
        ns = parser.parse_args(["/NOLOGO"])
        self.assertTrue(ns.nologo)
        ns = parser.parse_args(["/nologo"])
        self.assertTrue(ns.nologo)

    def test_msvc_flag(self):
        parser = ArgumentParserEx(prefix_chars="/")
        parser.add_argument("/GR", action="msvc_flag", dest="rtti")
        parser.add_argument(
            "/INCREMENTAL",
            action="msvc_flag",
            msvc_false_suffix=":NO",
            dest="incremental",
        )
        parser.add_argument(
            "/flag",
            action="msvc_flag",
            msvc_true_suffix=":on",
            msvc_false_suffix=":off",
            ignore_case=True,
        )

        ns = parser.parse_args(["/GR-"])
        self.assertFalse(ns.rtti)
        ns = parser.parse_args(["/GR"])
        self.assertTrue(ns.rtti)
        ns = parser.parse_args(["/INCREMENTAL"])
        self.assertTrue(ns.incremental)
        ns = parser.parse_args(["/INCREMENTAL:NO"])
        self.assertFalse(ns.incremental)
        ns = parser.parse_args(["/FLAG:ON"])
        self.assertTrue(ns.flag)
        ns = parser.parse_args(["/flag:off"])
        self.assertFalse(ns.flag)

        ns = parser.parse_args([])
        self.assertIsNone(vars(ns).get("flag"))
        self.assertIsNone(vars(ns).get("rtti"))
        self.assertIsNone(vars(ns).get("incremental"))

        ns, remaining = parser.parse_known_args(["/flag:unknown"])
        self.assertListEqual(["/flag:unknown"], remaining)
        self.assertIsNone(vars(ns).get("flag"))

        parser.set_defaults(flag=False)
        ns = parser.parse_args([])
        self.assertFalse(ns.flag)

    def test_msvc_flag_with_value(self):
        parser = ArgumentParserEx(prefix_chars="/-")
        parser.set(ignore_case=True)
        parser.add_argument("/flag", action="msvc_flag_with_value")
        parser.add_argument(
            "/ENABLE", action="msvc_flag_with_value", append=True, dest="list"
        )

        ns, remaining = parser.parse_known_args(["/FLAG"])
        self.assertListEqual(["/FLAG"], remaining)
        self.assertIsNone(vars(ns).get("flag"))

        ns, remaining = parser.parse_known_args(["/flag"])
        self.assertListEqual(["/flag"], remaining)
        self.assertIsNone(vars(ns).get("flag"))

        ns, remaining = parser.parse_known_args(["/flag:"])
        self.assertListEqual(["/flag:"], remaining)
        self.assertIsNone(vars(ns).get("flag"))

        ns = parser.parse_args(["/flag:value"])
        self.assertEqual("value", ns.flag)

        ns = parser.parse_args(["-FLAG:1,2,3"])
        self.assertEqual("1,2,3", ns.flag)

        ns = parser.parse_args(["/ENABLE:1", "-FlAg:2", "-enable:3"])
        self.assertEqual("2", ns.flag)
        self.assertEqual(["1", "3"], ns.list)

    def test_msvc_flag_with_value_with_append(self):
        parser = ArgumentParserEx(prefix_chars="/-")
        parser.set(ignore_case=True)
        parser.add_argument(
            "/flag", action="msvc_flag_with_value", dest="flags", append=True
        )

        ns = parser.parse_args(["/flag:a", "/flag:b"])
        self.assertListEqual(["a", "b"], ns.flags)

    def test_single_hyphen_multichar_flag(self):
        parser = ArgumentParserEx()
        parser.add_argument("-flag")

        ns = parser.parse_args(["-flag", "value"])
        self.assertEqual("value", ns.flag)

        ns = parser.parse_args(["-flag=value"])
        self.assertEqual("value", ns.flag)

    def test_dest_naming(self):
        parser = ArgumentParserEx(prefix_chars="/-")
        parser.add_argument("-a-b", action="store_true")
        parser.add_argument("-++", action="store_true")
        parser.add_argument("/b:c", dest="_f", action="store_true")
        parser.add_argument("--c~d", action="store_true")
        parser.add_argument("-UPPER", action="store_true")
        self.assertRaisesRegexp(
            ValueError,
            "Invalid dest: '@flag'",
            parser.add_argument,
            "-flag",
            dest="@flag",
            action="store_true",
        )
        ns = parser.parse_args(["-a-b", "-++", "/b:c", "--c~d", "-UPPER"])
        self.assertTrue(ns.a_b)
        self.assertTrue(ns.__)
        self.assertTrue(ns._f)
        self.assertTrue(ns.c_d)
        self.assertTrue(ns.UPPER)

    def test_raw_dest(self):
        parser = ArgumentParserEx()
        parser.add_argument("-arg1", action="store_true", raw_dest="args")
        parser.add_argument("--arg2", "-f", dest=None, raw_dest="args")
        parser.add_argument("file", raw_dest="args")
        parser.add_argument("files", nargs="*", dest=None, raw_dest="args")
        parser.add_argument("-D", dest=None, raw_dest="args", raw_format="".join)

        ns = parser.parse_args(["--arg2", "1", "2"])
        self.assertListEqual([["--arg2", "1"], "2"], ns.args)

        ns = parser.parse_args(["--arg2=1", "1", "-arg1", "2", "3"])
        self.assertListEqual(["--arg2=1", "1", "-arg1", "2", "3"], ns.args)

        ns, remaining = parser.parse_known_args(["1", "-fvalue", "2", "-unknown"])
        self.assertListEqual(["-unknown"], remaining)
        self.assertListEqual(["1", "-fvalue", "2"], ns.args)

        ns, remaining = parser.parse_known_args(["1", "-unknown", "-fvalue", "2"])
        self.assertListEqual(["-unknown"], remaining)
        self.assertListEqual(["1", "-fvalue", "2"], ns.args)

        ns = parser.parse_args(["1", "-D", "2", "3", "-D4"])
        self.assertListEqual(["1", "-D2", "3", "-D4"], ns.args)

    def test_unknown_args_dest(self):
        parser = ArgumentParserEx()
        parser.add_argument("--flag", action="store_true", raw_dest="args")
        parser.add_argument("--key", raw_dest="args")
        parser.add_argument("infile", raw_dest="args")

        ns, unknown = parser.parse_known_args(["--flag"], unknown_dest="args")
        self.assertListEqual(["--flag"], ns.args)
        self.assertListEqual([], unknown)

        ns, unknown = parser.parse_known_args(
            ["--flag", "--unknownflag", "--key=value"], unknown_dest="args"
        )
        self.assertListEqual(["--flag", "--unknownflag", "--key=value"], ns.args)
        self.assertListEqual(["--unknownflag"], unknown)

        ns, unknown = parser.parse_known_args(
            ["--flag", "--unknownflag", "a.txt"], unknown_dest="args"
        )
        self.assertListEqual(["--flag", "--unknownflag", "a.txt"], ns.args)
        self.assertListEqual(["--unknownflag"], unknown)

        ns, unknown = parser.parse_known_args(
            ["--flag", "a.txt", "--unknownflag"], unknown_dest="args"
        )
        self.assertListEqual(["--flag", "a.txt", "--unknownflag"], ns.args)
        self.assertListEqual(["--unknownflag"], unknown)

        ns, unknown = parser.parse_known_args(
            ["--unknown"], unknown_dest=["args", "extra"]
        )
        self.assertListEqual(["--unknown"], ns.args)
        self.assertListEqual(["--unknown"], ns.extra)
        self.assertListEqual(["--unknown"], unknown)

    def test_implicit_default_values(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a")
        parser.add_argument("-b", dest="dest_b")
        parser.add_argument("-c", nargs=2)
        parser.add_argument("-d", action="append")
        parser.add_argument("-e", action="store")
        parser.add_argument("-f", nargs="*")
        parser.add_argument("-g", nargs="+")
        parser.add_argument("-i", nargs="?")
        parser.add_argument("-j", nargs="*", action="append")
        parser.add_argument("-k", nargs="+", action="append")
        parser.add_argument("-l", nargs="?", action="append")
        ns = parser.parse_args([])
        self.assertIsNone(getattr(ns, "a", "default"))
        self.assertIsNone(getattr(ns, "dest_b", "default"))
        self.assertIsNone(getattr(ns, "c", "default"))
        self.assertIsNone(getattr(ns, "d", "default"))
        self.assertIsNone(getattr(ns, "e", "default"))
        self.assertIsNone(getattr(ns, "f", "default"))
        self.assertIsNone(getattr(ns, "g", "default"))
        self.assertIsNone(getattr(ns, "i", "default"))
        self.assertIsNone(getattr(ns, "j", "default"))
        self.assertIsNone(getattr(ns, "k", "default"))
        self.assertIsNone(getattr(ns, "l", "default"))

        parser = ArgumentParserEx()
        parser.add_argument("a")
        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        parser = ArgumentParserEx()
        parser.add_argument("b", nargs=2)
        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        parser = ArgumentParserEx()
        parser.add_argument("c", action="append")
        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )
        parser = ArgumentParserEx()
        parser.add_argument("d", action="store")
        self.assertRaisesRegexp(
            ValueError, "Required attribute not found", parser.parse_args, []
        )

        parser = ArgumentParserEx()
        parser.add_argument("e", nargs="*")
        ns = parser.parse_args([])
        self.assertEqual([], getattr(ns, "e", "default"))

        parser = ArgumentParserEx()
        parser.add_argument("f", nargs="?")
        ns = parser.parse_args([])
        self.assertIsNone(getattr(ns, "f", "default"))

        parser = ArgumentParserEx()
        parser.add_argument("g", nargs="*", action="append")
        ns = parser.parse_args([])
        # ArgumentParser: [[]]
        self.assertEqual([], getattr(ns, "g", "default"))

        parser = ArgumentParserEx()
        parser.add_argument("h", nargs="?", action="append")
        ns = parser.parse_args([])
        # ArgumentParser: [None]
        self.assertIsNone(getattr(ns, "h", "default"))

    def test_positionals_do_not_consume_optionals(self):
        parser = ArgumentParserEx()
        parser.add_argument("positional")
        parser.add_argument("-optional", action="store_true")
        ns, remaining = parser.parse_known_args(["-optional"])
        self.assertListEqual([], remaining)
        self.assertTrue(ns.optional)
        self.assertIsNone(ns.positional)

        parser = ArgumentParserEx()
        parser.add_argument("positional", nargs="+")
        parser.add_argument("-optional", action="store_true")
        ns, remaining = parser.parse_known_args(["-optional"])
        self.assertListEqual([], remaining)
        self.assertTrue(ns.optional)
        self.assertIsNone(ns.positional)

        parser = ArgumentParserEx()
        parser.add_argument("positional", nargs="*")
        parser.add_argument("-optional", action="store_true")
        ns, remaining = parser.parse_known_args(["-optional"])
        self.assertListEqual([], remaining)
        self.assertTrue(ns.optional)
        self.assertEqual([], ns.positional)

    def test_concatenate_flags(self):
        self.skipTest("not implemented yet")
        parser = ArgumentParserEx()
        parser.add_argument("-a", action="store_true")
        parser.add_argument("-b", action="store_true")
        ns = parser.parse_args(["-ab"])
        self.assertTrue(ns.a)
        self.assertTrue(ns.b)

    def test_disable_concatenation(self):
        self.skipTest("not implemented yet")
        parser = ArgumentParserEx()
        parser.enable_flag_concatenation(False)
        parser.add_argument("-a", action="store_true")
        parser.add_argument("-b", action="store_true")
        ns, remaining = parser.parse_args(["-ab"])
        self.assertListEqual(["-ab"], remaining)

    def test_mutually_exclusive_group(self):
        self.skipTest("not implemented yet")
        parser = ArgumentParserEx()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", action="store_const", const="a", dest="mode")
        group.add_argument("-b", action="store_const", const="b", dest="mode")

        ns, remaining = parser.parse_known_args(["-ab"])
        self.assertListEqual(["-ab"], remaining)
        self.assertIsNone(vars(ns).get("mode"))

        ns, remaining = parser.parse_known_args(["-a", "-b"])
        self.assertListEqual(["-b"], remaining)
        self.assertEqual("a", ns.mode)

        ns = parser.parse_args(["-b"])
        self.assertEqual("b", ns.mode)

    def test_conditional_arguments(self):
        self.skipTest("not implemented yet")
        parser = ArgumentParserEx()
        arg = parser.add_argument("-a")
        parser.add_argument("-b", after=[arg])

        ns = parser.parse_args(["-a", "1", "-b", "2"])
        self.assertEqual("1", ns.a)
        self.assertEqual("2", ns.b)

        ns = parser.parse_args(["-a", "1"])
        self.assertEqual("1", ns.a)

        ns, remaining = parser.parse_known_args(["-b", "1"])
        self.assertListEqual(["-b", "1"], remaining)
        self.assertIsNone(vars(ns).get("b"))

    def test_deepcopy_1(self):
        parser = ArgumentParserEx()
        parser.add_argument("-a")

        parser = deepcopy(parser)

        ns = parser.parse_args(["-a", "1"])
        self.assertEqual("1", ns.a)

    def test_deepcopy_2(self):
        self.skipTest("not implemented yet")
        parser = ArgumentParserEx()
        arg = parser.add_argument("-a")
        parser.add_argument("-b", after=[arg])

        parser = deepcopy(parser)

        ns = parser.parse_args(["-a", "1", "-b", "2"])
        self.assertEqual("1", ns.a)
        self.assertEqual("2", ns.b)

        ns = parser.parse_args(["-a", "1"])
        self.assertEqual("1", ns.a)

        ns, remaining = parser.parse_known_args(["-b", "1"])
        self.assertListEqual(["-b", "1"], remaining)
        self.assertIsNone(vars(ns).get("b"))

    def test_gnu_ar_parser(self):
        self.skipTest("not implemented yet")
        # GNU ar has a surprisingly complex syntax,
        # it's a good test-case for ArgumentParserEx
        parser = ArgumentParserEx()
        operation = parser.add_mutually_exclusive_group()
        arg_r = operation.add_argument(flags=["-r", "r"], action="store_true")
        arg_q = operation.add_argument(flags=["-q", "q"], action="store_true")
        arg_a = parser.add_argument("-a", after=[arg_r, arg_q], action="store_true")
        arg_b = parser.add_argument("-b", after=[arg_r, arg_q], action="store_true")
        arg_N = parser.add_argument("-N", after=[arg_r, arg_q], action="store_true")
        parser.add_argument("relpos", after=[arg_a, arg_b])
        parser.add_argument("count", after=[arg_N], type=int)
        parser.add_argument("archive")
        parser.add_argument("member", nargs="*", dest="members")

        ns = parser.parse_args(["-q", "lib.a", "a.o", "b.o"])
        self.assertTrue(ns.q)
        self.assertEqual("lib.a", ns.archive)
        self.assertListEqual(["a.o", "b.o"], ns.members)

        ns = parser.parse_args(["-qa", "a.o", "lib.a", "b.o", "c.o"])
        self.assertTrue(ns.q)
        self.assertTrue(ns.a)
        self.assertEqual("a.o", ns.relpos)
        self.assertEqual("lib.a", ns.archive)
        self.assertListEqual(["a.o", "b.o"], ns.members)

        ns = parser.parse_args(["-qN", "1", "lib.a", "a.o", "b.o"])
        self.assertTrue(ns.q)
        self.assertTrue(ns.N)
        self.assertEqual(1, ns.count)
        self.assertEqual("lib.a", ns.archive)
        self.assertListEqual(["a.o", "b.o"], ns.members)

        ns = parser.parse_args(["-raN", "a.o", "1", "lib.a", "b.o", "c.o"])
        self.assertTrue(ns.r)
        self.assertTrue(ns.a)
        self.assertTrue(ns.N)
        self.assertEqual("a.o", ns.relpos)
        self.assertEqual(1, ns.count)
        self.assertEqual("lib.a", ns.archive)
        self.assertListEqual(["b.o", "c.o"], ns.members)

        ns = parser.parse_args(["raN", "a.o", "1", "lib.a", "b.o", "c.o"])
        self.assertTrue(ns.r)
        self.assertTrue(ns.a)
        self.assertTrue(ns.N)
        self.assertEqual("a.o", ns.relpos)
        self.assertEqual(1, ns.count)
        self.assertEqual("lib.a", ns.archive)
        self.assertListEqual(["b.o", "c.o"], ns.members)

        self.assertRaisesRegexp(
            ValueError, "doot", parser.parse_args, ["rq", "lib.a", "a.o"]
        )

        self.assertRaisesRegexp(
            ValueError, "doot", parser.parse_args, ["-ar", "lib.a", "a.o"]
        )

    def test_optional_positional_argument(self):
        parser = ArgumentParserEx()
        parser.add_argument("infile")
        parser.add_argument("outfile", nargs="?")

        ns = parser.parse_args(["inout.txt"])
        self.assertEqual("inout.txt", ns.infile)

        ns = parser.parse_args(["in.txt", "out.txt"])
        self.assertEqual("in.txt", ns.infile)
        self.assertEqual(["out.txt"], ns.outfile)
