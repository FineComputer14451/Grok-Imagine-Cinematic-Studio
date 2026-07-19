"""Safe launcher catalog for the studio TUI (static; no Typer scraping)."""

from __future__ import annotations

from dataclasses import dataclass


FORBIDDEN_ARGV_TOKENS: frozenset[str] = frozenset(
    {
        "--wizard",
        "run",
        "submit",
        "record",
        "cancel",
        "declutter",
    }
)


@dataclass(frozen=True)
class LauncherEntry:
    id: str
    label: str
    description: str
    argv: list[str]


LAUNCHER_CATALOG: tuple[LauncherEntry, ...] = (
    LauncherEntry("status", "Studio status", "Version, agents, activation", ["status"]),
    LauncherEntry(
        "dashboard_compact",
        "Dashboard (compact)",
        "Summary panels only",
        ["dashboard", "--compact"],
    ),
    LauncherEntry("models_list", "Models list", "Registered model stack", ["models", "list"]),
    LauncherEntry("models_verify", "Models verify", "Compatibility check", ["models", "verify"]),
    LauncherEntry(
        "quota_dashboard",
        "Quota dashboard",
        "Session spend and budget",
        ["quota", "dashboard"],
    ),
    LauncherEntry("dna_list", "DNA list", "Character DNA profiles", ["dna", "list"]),
    LauncherEntry(
        "sequence_list",
        "Sequences list",
        "Long-form sequences",
        ["sequence", "list"],
    ),
    LauncherEntry("imagine_list", "Imagine jobs", "Recent Imagine jobs", ["imagine", "list"]),
    LauncherEntry("plugin_list", "Plugin list", "Installed plugin skills", ["plugin", "list"]),
)
