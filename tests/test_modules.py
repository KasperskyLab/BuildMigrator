import logging
import os
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
import build_migrator.modules  # noqa: E402


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(level=logging.DEBUG)


class TestModules(base.TestBase):
    module_dir = os.path.join(SCRIPT_DIR, "files", "test_modules")
    build_migrator_mock = object()

    def test_load_default_modules(self):
        loader = build_migrator.modules.ModuleLoader()
        loader.load()

    def test_load_custom_modules(self):
        loader = build_migrator.modules.ModuleLoader(
            [self.module_dir, os.path.join(self.module_dir, "invalid")]
        )

        loader.load(builders=["ext1", "ext2"], generators=[], parsers=[], optimizers=[])

        self.assertRaisesRegexp(
            ValueError,
            "(?i)module not found",
            loader.load,
            builders=[os.path.join(self.module_dir, "notfound.py")],
            generators=[],
            parsers=[],
            optimizers=[],
        )

        self.assertRaisesRegexp(
            ValueError,
            r"(?i)must have .+ extension",
            loader.load,
            builders=[os.path.join(self.module_dir, "invalid", "ext.txt")],
            generators=[],
            parsers=[],
            optimizers=[],
        )

        self.assertRaises(
            SyntaxError,
            loader.load,
            builders=[os.path.join(self.module_dir, "invalid", "ext.py")],
            generators=[],
            parsers=[],
            optimizers=[],
        )

        self.assertRaises(
            SyntaxError,
            loader.load,
            builders=["ext"],
            generators=[],
            parsers=[],
            optimizers=[],
        )

    def test_create_custom_modules(self):
        loader = build_migrator.modules.ModuleLoader([self.module_dir])
        modules = loader.load(
            builders=["ext1", "ext2"], generators=[], parsers=[], optimizers=[]
        )
        entry_point, builders = modules.create_builders(
            self.build_migrator_mock, myarg="value"
        )
        self.assertIsNotNone(entry_point)
        self.assertEqual(1, len(builders))

        self.assertRaises(Exception, modules.create_builders, self.build_migrator_mock)

        modules = loader.load(
            builders=["ext2", "ext1"], generators=[], parsers=[], optimizers=[]
        )
        entry_point, builders = modules.create_builders(
            self.build_migrator_mock, myarg="value"
        )
        self.assertIsNotNone(entry_point)
        self.assertEqual(1, len(builders))

        modules = loader.load(
            builders=["ext1"], generators=[], parsers=[], optimizers=[]
        )
        entry_point, builders = modules.create_builders(
            self.build_migrator_mock, myarg="value"
        )
        self.assertIsNotNone(entry_point)
        self.assertEqual(0, len(builders))

        modules = loader.load(
            builders=["ext1", "ext2", "ext3"], generators=[], parsers=[], optimizers=[]
        )
        entry_point, builders = modules.create_builders(
            self.build_migrator_mock, myarg="value"
        )
        self.assertIsNotNone(entry_point)
        self.assertEqual(3, len(builders))

        modules = loader.load(
            builders=["ext2"], generators=[], parsers=[], optimizers=[]
        )
        self.assertRaisesRegexp(
            ValueError,
            "EntryPoint not found",
            modules.create_builders,
            self.build_migrator_mock,
        )

        modules = loader.load(
            builders=["ext1", "ext4"], generators=[], parsers=[], optimizers=[]
        )
        self.assertRaisesRegexp(
            ValueError,
            "Multiple EntryPoints found",
            modules.create_builders,
            self.build_migrator_mock,
        )

    def test_create_default_modules(self):
        loader = build_migrator.modules.ModuleLoader()
        modules = loader.load()

        modules.create_builders(
            self.build_migrator_mock,
            out_dir=".",
            source_dir="..",
            build_commands=["configure", "make"],
        )

        entry_point, parsers = modules.create_parsers(
            self.build_migrator_mock,
            logs=["ninja:file.log"],
            source_dir=".",
            build_dirs=["."],
        )
        self.assertIsNotNone(entry_point)
        self.assertTrue(len(parsers) > 0)
        entry_point, optimizers = modules.create_optimizers(self.build_migrator_mock)
        self.assertIsNotNone(entry_point)
        self.assertTrue(len(parsers) > 0)
        entry_point, generators = modules.create_generators(
            self.build_migrator_mock, out_dir="."
        )
        self.assertIsNotNone(entry_point)
        self.assertTrue(len(parsers) > 0)
