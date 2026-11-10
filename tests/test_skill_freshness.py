import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "review-tcia-dataset-proposal" / "scripts" / "check_freshness.py"
SPEC = importlib.util.spec_from_file_location("proposal_skill_freshness", SCRIPT)
assert SPEC and SPEC.loader
freshness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freshness)


class SkillFreshnessTests(unittest.TestCase):
    script = SCRIPT
    freshness = freshness

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temporary.name)
        self.skill_root = self.temp_root / self.script.parents[1].name
        shutil.copytree(self.script.parents[1], self.skill_root)
        self.manifest_path = self.skill_root / "skill_version.json"
        self.remote_path = self.temp_root / "remote_skill_version.json"
        self.cache_path = self.temp_root / "freshness_cache.json"

    def tearDown(self):
        self.temporary.cleanup()

    def write_manifest(self, path: Path, version: str) -> dict:
        manifest = self.freshness.build_manifest(version, self.skill_root)
        manifest["update_url"] = self.freshness.DEFAULT_UPDATE_URL
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def check(self, force: bool = False):
        return self.freshness.check_freshness(
            manifest_path=self.manifest_path,
            manifest_url=self.remote_path.as_uri(),
            cache_path=self.cache_path,
            max_age_hours=24,
            timeout=2,
            force=force,
            root=self.skill_root,
        )

    def test_checked_in_manifest_matches_skill_files(self):
        installed_root = self.script.parents[1]
        manifest = self.freshness.load_json(installed_root / "skill_version.json")
        result = self.freshness.validate_manifest(manifest, installed_root)
        self.assertTrue(result["ok"], result)

    def test_default_sources_and_cache_belong_to_this_skill(self):
        name = self.script.parents[1].name
        self.assertTrue(self.freshness.DEFAULT_MANIFEST_URL.endswith(
            f"/skills/{name}/skill_version.json"))
        self.assertTrue(self.freshness.DEFAULT_UPDATE_URL.endswith(f"/skills/{name}"))
        self.assertEqual(self.freshness.default_cache_path().name, f"{name}-freshness.json")

    def test_current_result_is_reused_from_cache(self):
        local = self.write_manifest(self.manifest_path, "2026.08.25.1")
        self.remote_path.write_text(json.dumps(local), encoding="utf-8")

        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("current", 0))

        self.remote_path.unlink()
        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("current_cached", 0))

    def test_new_remote_version_requires_update(self):
        self.write_manifest(self.manifest_path, "2026.08.25.1")
        remote = self.freshness.build_manifest("2026.08.26.1", self.skill_root)
        self.remote_path.write_text(json.dumps(remote), encoding="utf-8")

        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("update_required", 3))
        self.assertEqual(result["remote_version"], "2026.08.26.1")

    def test_local_change_invalidates_cached_current_result(self):
        local = self.write_manifest(self.manifest_path, "2026.08.25.1")
        self.remote_path.write_text(json.dumps(local), encoding="utf-8")
        self.assertEqual(self.check()[1], 0)

        skill_path = self.skill_root / "SKILL.md"
        skill_path.write_text(skill_path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("local_modified", 3))
        self.assertIn("SKILL.md", result["local_integrity"]["changed"])

    def test_unavailable_remote_is_unverified(self):
        self.write_manifest(self.manifest_path, "2026.11.10.1")
        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("unverified", 2))
        self.assertIsNone(result["current"])

    def test_expired_cache_checks_remote_again(self):
        local = self.write_manifest(self.manifest_path, "2026.11.10.1")
        self.remote_path.write_text(json.dumps(local), encoding="utf-8")
        self.assertEqual(self.check()[1], 0)
        cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        cache["checked_at_utc"] = "2000-01-01T00:00:00+00:00"
        self.cache_path.write_text(json.dumps(cache), encoding="utf-8")
        remote = self.freshness.build_manifest("2026.11.10.2", self.skill_root)
        self.remote_path.write_text(json.dumps(remote), encoding="utf-8")
        result, exit_code = self.check()
        self.assertEqual((result["status"], exit_code), ("update_required", 3))


def load_skill_module(name):
    script = ROOT / "skills" / name / "scripts" / "check_freshness.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return script, module


class SupportingDataFreshnessTests(SkillFreshnessTests):
    script, freshness = load_skill_module("remap-tcia-supporting-data")


class WordPressMetadataFreshnessTests(SkillFreshnessTests):
    script, freshness = load_skill_module("curate-tcia-wordpress-metadata")


if __name__ == "__main__":
    unittest.main()
