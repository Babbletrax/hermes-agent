"""Owner approval of one destructive disk command at a time."""

import pytest

from tools.approval import check_all_command_guards, disable_session_yolo, enable_session_yolo
from tools.approval_context import reset_current_session_key, set_current_session_key


@pytest.fixture
def interactive_owner(monkeypatch):
    monkeypatch.setenv("HERMES_INTERACTIVE", "1")
    monkeypatch.delenv("HERMES_CRON_SESSION", raising=False)
    monkeypatch.delenv("HERMES_SINGLE_QUERY_SESSION", raising=False)
    token = set_current_session_key("disk-review-test")
    disable_session_yolo("disk-review-test")
    try:
        yield
    finally:
        disable_session_yolo("disk-review-test")
        reset_current_session_key(token)


@pytest.mark.parametrize("command", [
    "mkfs.ext4 /dev/sdb1",
    "sudo mkfs.xfs /dev/nvme1n1p1",
    "dd if=/dev/zero of=/dev/sdb bs=1M",
    "echo bad > /dev/sdb",
])
def test_disk_command_requires_owner_approval_each_time(interactive_owner, command):
    prompts = []

    def approve_once(actual, description, **options):
        prompts.append((actual, description, options))
        return "once"

    for _ in range(2):
        result = check_all_command_guards(command, "local", approval_callback=approve_once)
        assert result["approved"] is True
    assert len(prompts) == 2
    assert all(actual == command and "DESTRUCTIVE DISK OPERATION" in description
               for actual, description, _ in prompts)
    assert all(options["allow_permanent"] is False and options["smart_denied"] is True
               for _, _, options in prompts)


def test_denial_and_absent_owner_prevent_disk_command(interactive_owner, monkeypatch):
    command = "mkfs.ext4 /dev/sdb1"
    denied = check_all_command_guards(command, "local", approval_callback=lambda *a, **k: "deny")
    assert denied["approved"] is False
    monkeypatch.delenv("HERMES_INTERACTIVE")
    unattended = check_all_command_guards(command, "local")
    assert unattended["approved"] is False
    assert unattended["hardline"] is True


def test_yolo_still_requires_one_command_approval(interactive_owner):
    enable_session_yolo("disk-review-test")
    seen = []

    def approve_once(*args, **kwargs):
        seen.append(args)
        return "once"

    result = check_all_command_guards("mkfs.ext4 /dev/sdb1", "local", approval_callback=approve_once)
    assert result["approved"] is True
    assert len(seen) == 1


@pytest.mark.parametrize("command", [
    "mkfs.ext4 /dev/sdb1 && reboot",
    "mkfs.ext4 $(reboot)",
    "echo bad > /dev/sdb; reboot",
    "rm -rf / && mkfs.ext4 /dev/sdb1",
    "reboot",
])
def test_other_hardline_actions_never_reach_disk_prompt(interactive_owner, command):
    prompts = []
    result = check_all_command_guards(command, "local", approval_callback=lambda *a, **k: prompts.append(a))
    assert result["approved"] is False
    assert result["hardline"] is True
    assert prompts == []
