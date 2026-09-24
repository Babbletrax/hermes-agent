"""Fail if a fork patch was dropped during an upstream merge."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_disk_owner_review_patch_survives():
    text = _read("tools/approval.py")
    assert "_REVIEWABLE_DISK_HARDLINE" in text
    assert "once_only=True" in text
    assert "_disk_owner_review_enabled" in text


def test_approvals_test_reports_disk_review():
    text = _read("hermes_cli/approvals_test.py")
    assert "destructive disk command requires explicit owner approval once" in text


def test_acp_runtime_shutdown_patch_survives():
    entry = _read("acp_adapter/entry.py")
    server = _read("acp_adapter/server.py")
    assert "shutdown_acp_runtime" in entry
    assert "_exit_without_finalize" in entry
    assert "def shutdown_acp_runtime" in server


def test_acp_extra_toolsets_patch_survives():
    text = _read("acp_adapter/session.py")
    assert "HERMES_ACP_EXTRA_TOOLSETS" in text
