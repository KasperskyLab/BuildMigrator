import os
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
import build_migrator.settings  # noqa: E402


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


class TestSettings(base.TestBase):
    settings_dir = os.path.join(SCRIPT_DIR, "files", "test_settings")
    preset1_path = os.path.join(settings_dir, "preset1.json")
    preset2_path = os.path.join(settings_dir, "preset2.json")

    def test_load_settings(self):
        loader = build_migrator.settings.SettingsLoader()
        settings = loader.load(["windows"])
        self.assertEqual("windows", settings.get("platform"))

    def test_custom_settings(self):
        loader = build_migrator.settings.SettingsLoader([self.settings_dir])
        settings = loader.load(["preset1"])
        expected = {"value": "1", "list": ["1", "2"]}
        self.assertEqual(expected, settings)

    def test_merge_settings1(self):
        loader = build_migrator.settings.SettingsLoader([self.settings_dir])
        settings = loader.load(["preset1", "preset2"])
        expected = {"value": "2", "list": ["1", "2", "3", "4"]}
        self.assertEqual(expected, settings)

    def test_merge_settings2(self):
        loader = build_migrator.settings.SettingsLoader()
        settings = loader.load([self.preset2_path, self.preset1_path])
        expected = {"value": "1", "list": ["3", "4", "1", "2"]}
        self.assertEqual(expected, settings)

    def test_file_not_found(self):
        loader = build_migrator.settings.SettingsLoader()
        self.assertRaises(IOError, loader.load, ["not-found.json"])

    def test_merge_error(self):
        loader = build_migrator.settings.SettingsLoader()
        dict1 = {"a": 1}
        dict2 = {"a": [2, 3]}
        self.assertRaisesRegexp(ValueError, "type conflict", loader.merge, dict1, dict2)
