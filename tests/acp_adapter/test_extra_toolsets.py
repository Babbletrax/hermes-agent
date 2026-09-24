"""ACP extra plugin toolsets: on via HERMES_ACP_EXTRA_TOOLSETS, off when unset."""

from acp_adapter.session import _expand_acp_enabled_toolsets


def test_extra_toolsets_off_by_default(monkeypatch):
    monkeypatch.delenv("HERMES_ACP_EXTRA_TOOLSETS", raising=False)
    assert _expand_acp_enabled_toolsets() == ["hermes-acp"]


def test_extra_toolsets_on_appends_unique_names(monkeypatch):
    monkeypatch.setenv("HERMES_ACP_EXTRA_TOOLSETS", "mermaid, drawio, mermaid")
    assert _expand_acp_enabled_toolsets(["hermes-acp"], ["writer"]) == [
        "hermes-acp",
        "mcp-writer",
        "mermaid",
        "drawio",
    ]


def test_extra_toolsets_empty_string_is_off(monkeypatch):
    monkeypatch.setenv("HERMES_ACP_EXTRA_TOOLSETS", "  ,  ")
    assert _expand_acp_enabled_toolsets() == ["hermes-acp"]
