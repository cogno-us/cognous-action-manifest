"""dump_manifest writes new files with a fixed private mode and never reads or changes the process umask."""
import os
import stat

import pytest

from agent_action_manifest.loader import dump_manifest, load_manifest
from tests.test_runtime_binding import FIXTURE


def _no_umask(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("umask must not be consulted")
    monkeypatch.setattr(os, "umask", fail)


@pytest.mark.parametrize("process_umask", [0o000, 0o022, 0o077, 0o277])
def test_new_file_gets_private_mode_regardless_of_umask(tmp_path, process_umask):
    old = os.umask(process_umask)
    try:
        target = tmp_path / "sub" / "m.json"
        dump_manifest(load_manifest(FIXTURE), target)
    finally:
        os.umask(old)
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert load_manifest(target).manifest_id


def test_no_umask_call_in_dump(tmp_path, monkeypatch):
    _no_umask(monkeypatch)
    dump_manifest(load_manifest(FIXTURE), tmp_path / "m.json")


def test_existing_file_keeps_its_mode(tmp_path):
    target = tmp_path / "m.json"
    target.write_text("{}")
    os.chmod(target, 0o640)
    dump_manifest(load_manifest(FIXTURE), target)
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert load_manifest(target).manifest_id


def test_no_temporary_file_left_and_content_roundtrips(tmp_path):
    target = tmp_path / "m.json"
    manifest = load_manifest(FIXTURE)
    dump_manifest(manifest, target)
    assert sorted(os.listdir(tmp_path)) == ["m.json"]
    assert load_manifest(target) == manifest
