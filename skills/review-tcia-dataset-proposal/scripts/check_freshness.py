#!/usr/bin/env python3
"""Check an installed proposal-review skill against its public version manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_ROOT / "skill_version.json"
DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/kirbyju/tcia-dataset-proposals/"
    "main/skills/review-tcia-dataset-proposal/skill_version.json"
)
DEFAULT_UPDATE_URL = (
    "https://github.com/kirbyju/tcia-dataset-proposals/"
    "tree/main/skills/review-tcia-dataset-proposal"
)
INCLUDED_TOP_LEVEL_FILES = ("SKILL.md",)
INCLUDED_DIRECTORIES = ("agents", "references", "scripts")
INCLUDED_SUFFIXES = {".csv", ".json", ".md", ".py", ".txt", ".yaml", ".yml"}
EXCLUDED_NAMES = {"__pycache__", ".DS_Store"}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def isoformat(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat()


def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_skill_files(root: Path = SKILL_ROOT) -> Iterable[Path]:
    for name in INCLUDED_TOP_LEVEL_FILES:
        path = root / name
        if path.is_file():
            yield path
    for directory in INCLUDED_DIRECTORIES:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in INCLUDED_SUFFIXES:
                continue
            if any(part in EXCLUDED_NAMES for part in path.parts):
                continue
            yield path


def current_file_hashes(root: Path = SKILL_ROOT) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in sorted(set(iter_skill_files(root)))
    }


def build_manifest(version: str, root: Path = SKILL_ROOT) -> dict[str, Any]:
    if not version.strip():
        raise ValueError("A nonempty skill version is required.")
    return {
        "schema_version": SCHEMA_VERSION,
        "skill_version": version.strip(),
        "updated_at_utc": isoformat(utc_now()),
        "files": current_file_hashes(root),
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def validate_manifest(manifest: dict[str, Any], root: Path = SKILL_ROOT) -> dict[str, Any]:
    expected = manifest.get("files")
    if not isinstance(expected, dict):
        return {"ok": False, "error": "Manifest files must be an object."}
    actual = current_file_hashes(root)
    expected_names = set(expected)
    actual_names = set(actual)
    missing = sorted(expected_names - actual_names)
    untracked = sorted(actual_names - expected_names)
    changed = sorted(
        name for name in expected_names & actual_names if expected.get(name) != actual.get(name)
    )
    schema_ok = manifest.get("schema_version") == SCHEMA_VERSION
    version_ok = bool(str(manifest.get("skill_version") or "").strip())
    return {
        "ok": schema_ok and version_ok and not missing and not untracked and not changed,
        "schema_ok": schema_ok,
        "version_ok": version_ok,
        "skill_version": manifest.get("skill_version"),
        "missing": missing,
        "untracked": untracked,
        "changed": changed,
    }


def default_cache_path() -> Path:
    cache_root = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache"))
    return cache_root / "tcia-skills" / "review-tcia-dataset-proposal-freshness.json"


def fetch_manifest(url: str, timeout: float) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "file":
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = response.read()
    else:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "review-tcia-dataset-proposal-freshness/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Remote manifest is not a JSON object.")
    return value


def manifest_identity(manifest: dict[str, Any]) -> str:
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_cache(path: Path) -> dict[str, Any] | None:
    try:
        return load_json(path)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return None


def write_cache(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def cached_result(
    cache: dict[str, Any] | None,
    local_identity: str,
    max_age_hours: float,
    now: dt.datetime,
) -> dict[str, Any] | None:
    if not cache or cache.get("local_manifest_sha256") != local_identity:
        return None
    checked_at_text = cache.get("checked_at_utc")
    result = cache.get("result")
    if not isinstance(checked_at_text, str) or not isinstance(result, dict):
        return None
    try:
        age = now - parse_time(checked_at_text)
    except (TypeError, ValueError):
        return None
    if age.total_seconds() < 0 or age.total_seconds() >= max_age_hours * 3600:
        return None
    cached = dict(result)
    if cached.get("status") == "current":
        cached["status"] = "current_cached"
    cached["source"] = "cache"
    cached["checked_at_utc"] = checked_at_text
    cached["cache_age_hours"] = round(age.total_seconds() / 3600, 3)
    return cached


def check_freshness(
    manifest_path: Path,
    manifest_url: str,
    cache_path: Path,
    max_age_hours: float,
    timeout: float,
    force: bool,
    root: Path = SKILL_ROOT,
) -> tuple[dict[str, Any], int]:
    local = load_json(manifest_path)
    integrity = validate_manifest(local, root)
    local_version = local.get("skill_version")
    update_url = str(local.get("update_url") or DEFAULT_UPDATE_URL)
    if not integrity.get("ok"):
        return (
            {
                "status": "local_modified",
                "current": False,
                "local_version": local_version,
                "local_integrity": integrity,
                "update_url": update_url,
            },
            3,
        )

    now = utc_now()
    local_identity = manifest_identity(local)
    if not force:
        cached = cached_result(load_cache(cache_path), local_identity, max_age_hours, now)
        if cached is not None:
            return cached, 0 if cached.get("current") else 3

    try:
        remote = fetch_manifest(manifest_url, timeout)
    except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
        return (
            {
                "status": "unverified",
                "current": None,
                "local_version": local_version,
                "error": str(exc),
                "manifest_url": manifest_url,
                "update_url": update_url,
            },
            2,
        )

    remote_version = remote.get("skill_version")
    same_version = local_version == remote_version
    same_files = local.get("files") == remote.get("files")
    is_current = bool(same_version and same_files)
    result = {
        "status": "current" if is_current else "update_required",
        "current": is_current,
        "source": "remote",
        "checked_at_utc": isoformat(now),
        "local_version": local_version,
        "remote_version": remote_version,
        "remote_updated_at_utc": remote.get("updated_at_utc"),
        "manifest_url": manifest_url,
        "update_url": str(remote.get("update_url") or update_url),
    }
    write_cache(
        cache_path,
        {
            "checked_at_utc": result["checked_at_utc"],
            "local_manifest_sha256": local_identity,
            "result": result,
        },
    )
    return result, 0 if is_current else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Write a new local version manifest.")
    generate.add_argument("--version", required=True)
    generate.add_argument("--out", default=str(DEFAULT_MANIFEST))

    check = subparsers.add_parser("check", help="Check local integrity and periodically compare GitHub.")
    check.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    check.add_argument("--manifest-url", default=DEFAULT_MANIFEST_URL)
    check.add_argument("--cache-path", default=str(default_cache_path()))
    check.add_argument("--max-age-hours", type=float, default=24.0)
    check.add_argument("--timeout", type=float, default=20.0)
    check.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.command == "generate":
        manifest = build_manifest(args.version)
        manifest["update_url"] = DEFAULT_UPDATE_URL
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "generated", "path": str(output), **manifest}, indent=2))
        return 0

    if args.max_age_hours <= 0:
        parser.error("--max-age-hours must be greater than zero")
    result, exit_code = check_freshness(
        manifest_path=Path(args.manifest),
        manifest_url=args.manifest_url,
        cache_path=Path(args.cache_path),
        max_age_hours=args.max_age_hours,
        timeout=args.timeout,
        force=args.force,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "unverified", "current": None, "error": str(exc)}))
        raise SystemExit(2)
