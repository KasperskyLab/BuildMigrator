import os
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
from build_migrator.common.algorithm import (
    add_unique_stable,
    add_unique_stable_by_key,
    intersect_unique_stable,
    find_best_common_set,
    FitnessByTotalStringLength,
    fitness_by_set_length,
)  # noqa: E402


class TestAlgorithms(base.TestBase):
    def test_add_unique_stable(self):
        lst = ["b", "a"]

        result = add_unique_stable(lst)
        self.assertListEqual(["b", "a"], lst)
        self.assertListEqual(["b", "a"], result)

        add_unique_stable(lst, "b", "c", "a")
        self.assertListEqual(["b", "a", "c"], lst)

        result = add_unique_stable(lst, "d", "d")
        self.assertListEqual(["b", "a", "c", "d"], lst)
        self.assertListEqual(["b", "a", "c", "d"], result)

        result = add_unique_stable(lst, "")
        self.assertListEqual(["b", "a", "c", "d", ""], lst)
        self.assertListEqual(["b", "a", "c", "d", ""], result)

    def test_add_unique_stable_by_key(self):
        lst = [{"v": 2, "k": 1}, {"v": 1, "k": 2}]

        result = add_unique_stable_by_key(lst, "k")
        self.assertListEqual([{"v": 2, "k": 1}, {"v": 1, "k": 2}], lst)

        result = add_unique_stable_by_key(lst, "k", {"v": 0, "k": 1})
        self.assertListEqual([{"v": 2, "k": 1}, {"v": 1, "k": 2}], lst)
        self.assertListEqual([{"v": 2, "k": 1}, {"v": 1, "k": 2}], result)

        result = add_unique_stable_by_key(lst, "k", {"v": 0, "k": None})
        self.assertListEqual(
            [{"v": 2, "k": 1}, {"v": 1, "k": 2}, {"v": 0, "k": None}], lst
        )
        self.assertListEqual(
            [{"v": 2, "k": 1}, {"v": 1, "k": 2}, {"v": 0, "k": None}], result
        )

        lst = [{"v": 1, "k": 1}]
        result = add_unique_stable_by_key(
            lst, "k", {"v": 2, "k": "5"}, {"v": 1, "k": "3"}
        )
        self.assertListEqual(
            [{"v": 1, "k": 1}, {"v": 2, "k": "5"}, {"v": 1, "k": "3"}], lst
        )
        self.assertListEqual(
            [{"v": 1, "k": 1}, {"v": 2, "k": "5"}, {"v": 1, "k": "3"}], result
        )

        lst = [{"v": 1, "k": 1}]
        result = add_unique_stable_by_key(
            lst, "k", {"v": 5, "k": "2"}, {"v": 3, "k": "2"}
        )
        self.assertListEqual([{"v": 1, "k": 1}, {"v": 5, "k": "2"}], lst)
        self.assertListEqual([{"v": 1, "k": 1}, {"v": 5, "k": "2"}], result)

        self.assertRaisesRegexp(
            KeyError, "k", add_unique_stable_by_key, lst, "k", {"v": 5}
        )

    def test_intersect_unique_stable(self):
        r = intersect_unique_stable(["b", "a"])
        self.assertListEqual(["b", "a"], r)

        r = intersect_unique_stable([])
        self.assertListEqual([], r)

        r = intersect_unique_stable([], [], [])
        self.assertListEqual([], r)

        self.assertIsNone(intersect_unique_stable())

        r = intersect_unique_stable(["b", "a", "c"], ["c", "b", "a"])
        self.assertListEqual(["b", "a", "c"], r)

        r = intersect_unique_stable(["b", "a"], ["c", "b"], [])
        self.assertListEqual([], r)

        r = intersect_unique_stable(["b", "a"], ["c", "b"], [])
        self.assertListEqual([], r)

        r = intersect_unique_stable([], ["b", "a"], ["c", "b"])
        self.assertListEqual([], r)

        r = intersect_unique_stable(["b", "a", "c"], ["c", "b", "a"], ["a", "1"])
        self.assertListEqual(["a"], r)

        r = intersect_unique_stable(["a", "b"], ["b", "c"], ["c", "d"])
        self.assertListEqual([], r)

    def test_find_best_common_set(self):
        cs, f = find_best_common_set([{1, 2, 3, 4}, {2, 3, 4}, {3, 4, 5}, {3, 4}])
        self.assertSetEqual({3, 4}, cs)
        self.assertEqual(2, f)

        cs, f = find_best_common_set(
            [{1}, {}, {1, 2}, {3, 1, 2}, {3, 1, 2, 4}, {0, 3, 1, 2}]
        )
        self.assertSetEqual({1, 2, 3}, cs)
        self.assertEqual(3, f)

        cs, f = find_best_common_set(
            [{1}, {}, {1, 2}, {3, 1, 2}, {5, 6, 7, 8, 9, 10, 11, 12, 13}, {3, 1, 2, 4}]
        )
        self.assertSetEqual({1, 2}, cs)
        self.assertEqual(1, f)

        cs, f = find_best_common_set([{1}, {}])
        self.assertSetEqual({1}, cs)
        self.assertEqual(-1, f)

        cs, f = find_best_common_set([{}])
        self.assertIsNone(cs)
        self.assertEqual(0, f)

        cs, f = find_best_common_set([{}, {}])
        self.assertIsNone(cs)
        self.assertEqual(0, f)

        cs, f = find_best_common_set([])
        self.assertIsNone(cs)
        self.assertEqual(0, f)

        values = set(range(0, 2001))
        cs, f = find_best_common_set([values] * 500)
        self.assertSetEqual(values, cs)
        self.assertEqual(997999, f)

        values = set(range(0, 501))
        cs, f = find_best_common_set([values] * 2000)
        self.assertSetEqual(values, cs)
        self.assertEqual(999499, f)

        cs, f = find_best_common_set(
            [{1, 2, 3, 4, 5}, {2, 3, 4, 5}], fitness_func=fitness_by_set_length
        )
        self.assertSetEqual({2, 3, 4, 5}, cs)
        self.assertEqual(2, f)

        cs, f = find_best_common_set(
            [
                {"abc", "def", "123456789012345678901234567890"},
                {"123456789012345678901234567890"},
                {"abc", "def"},
            ],
            fitness_func=FitnessByTotalStringLength(11),
        )
        self.assertSetEqual({"123456789012345678901234567890"}, cs)
        self.assertEqual(8, f)

        cs, f = find_best_common_set(
            [{"abc", "def", "1"}, {"1"}, {"abc", "def"}],
            fitness_func=FitnessByTotalStringLength(11),
        )
        self.assertSetEqual({"abc", "def"}, cs)
        self.assertEqual(-16, f)

        cs, f = find_best_common_set(
            [
                {"-DCCCCCCCCCCCCCCCCC", "-DDDDDDDDDDDDDDDDDD", "-DF1"},
                {
                    "-DAAAAAAAAAAAAAAAAA",
                    "-DBBBBBBBBBBBBBBBBB",
                    "-DCCCCCCCCCCCCCCCCC",
                    "-DDDDDDDDDDDDDDDDDD",
                },
                {},
                {"-DCCCCCCCCCCCCCCCCC", "-DDDDDDDDDDDDDDDDDD", "-DF4"},
                {
                    "-DEEEE",
                    "-DF7",
                    "-DGGGG",
                    "-DAAAAAAAAAAAAAAAAA",
                    "-DBBBBBBBBBBBBBBBBB",
                    "-DCCCCCCCCCCCCCCCCC",
                    "-DDDDDDDDDDDDDDDDDD",
                },
                {"-DEEEE", "-DF8", "-DGGGG"},
                {
                    "-DAAAAAAAAAAAAAAAAA",
                    "-DBBBBBBBBBBBBBBBBB",
                    "-DCCCCCCCCCCCCCCCCC",
                    "-DDDDDDDDDDDDDDDDDD",
                },
            ],
            fitness_func=FitnessByTotalStringLength(17),
        )
        self.assertSetEqual(
            {
                "-DAAAAAAAAAAAAAAAAA",
                "-DBBBBBBBBBBBBBBBBB",
                "-DCCCCCCCCCCCCCCCCC",
                "-DDDDDDDDDDDDDDDDDD",
            },
            cs,
        )
        self.assertEqual(101, f)
