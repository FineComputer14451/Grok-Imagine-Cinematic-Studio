"""Help IA: journey panels, nested group headings, ghost aliases."""

from __future__ import annotations

from cli_helpers import run_cli

ROOT_PANELS = (
    "Orient",
    "Health",
    "Produce",
    "Spend",
    "Gate",
    "Deliver",
    "Surfaces",
    "Meta",
)


def test_bare_invoke_is_help() -> None:
    result = run_cli()
    # Typer no_args_is_help prints help and exits 2 (not 0 like --help).
    assert result.returncode == 2
    assert "Orient" in result.stdout
    assert "cinematic-studio dashboard" in result.stdout


def test_root_help_journey_panels_and_epilog() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    positions = [result.stdout.index(panel) for panel in ROOT_PANELS]
    assert positions == sorted(positions)
    for example in (
        "cinematic-studio dashboard",
        "cinematic-studio doctor --quick",
        "cinematic-studio create-bible --wizard",
        "cinematic-studio quota estimate -d 30",
        "cinematic-studio ui",
    ):
        assert example in result.stdout
    assert "install" in result.stdout
    assert "update" in result.stdout
    assert "verify" in result.stdout
    assert "declutter" in result.stdout
    assert "docs/CLI_REFERENCE.md" in result.stdout
    assert "PATH wrapper" in result.stdout


def test_nested_help_panels() -> None:
    dna = run_cli("dna", "--help")
    assert dna.returncode == 0
    assert "Setup" in dna.stdout
    assert "Lock" in dna.stdout
    assert "Inject" in dna.stdout
    assert "extract" not in dna.stdout

    seq = run_cli("sequence", "--help")
    assert seq.returncode == 0
    assert "Setup" in seq.stdout
    assert "Extend" in seq.stdout
    assert "Gate" in seq.stdout
    assert "Deliver" in seq.stdout
    assert "extend-prompt" in seq.stdout

    plugin = run_cli("plugin", "--help")
    assert plugin.returncode == 0
    assert "Catalog" in plugin.stdout
    assert "Inspect" in plugin.stdout
    assert "Hygiene" in plugin.stdout
    assert "│ check" not in plugin.stdout

    imagine = run_cli("imagine", "--help")
    assert imagine.returncode == 0
    assert "Jobs" in imagine.stdout
    assert "Handoff" in imagine.stdout
    assert "Artifacts" in imagine.stdout

    quota = run_cli("quota", "--help")
    assert quota.returncode == 0
    assert "Health" in quota.stdout
    assert "Spend" in quota.stdout


def test_dna_extract_ghost() -> None:
    result = run_cli("dna", "extract")
    assert result.returncode == 2
    assert "dna init" in result.stdout
    assert "dna lock" in result.stdout
    help_result = run_cli("dna", "extract", "--help")
    assert help_result.returncode == 2
    assert "dna init" in help_result.stdout


def test_sequence_extend_ghost() -> None:
    result = run_cli("sequence", "extend")
    assert result.returncode == 2
    assert "extend-prompt" in result.stdout
    help_result = run_cli("sequence", "extend", "--help")
    assert help_result.returncode == 2
    assert "extend-prompt" in help_result.stdout


def test_plugin_check_forwards() -> None:
    check = run_cli("plugin", "check")
    catalog = run_cli("plugin", "catalog", "check")
    assert check.returncode == catalog.returncode == 0
    assert "up to date" in check.stdout.lower()
    assert "up to date" in catalog.stdout.lower()
    check_rel = run_cli("plugin", "check", "--release")
    catalog_rel = run_cli("plugin", "catalog", "check", "--release")
    assert check_rel.returncode == catalog_rel.returncode


def test_commands_search() -> None:
    listing = run_cli("commands")
    assert listing.returncode == 0
    assert "doctor" in listing.stdout
    assert "dna init" in listing.stdout
    assert "extend-prompt" in listing.stdout

    hits = run_cli("commands", "extend")
    assert hits.returncode == 0
    assert "extend-prompt" in hits.stdout
    assert "dna extract" not in hits.stdout
    assert "You shouldn't use this class directly" not in hits.stdout

    miss = run_cli("commands", "xyzzy-not-a-command")
    assert miss.returncode == 1
    assert "No commands matching" in miss.stdout

    root = run_cli("--help")
    assert "commands" in root.stdout
    assert "Orient" in root.stdout


def test_actionspec_frozen() -> None:
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "tools"))
    sys.path.insert(0, str(root))
    from studio_core.services.actions import ACTIONS

    assert len(ACTIONS) == 29
    assert ACTIONS["models_verify"].base_argv == ("models", "verify")
    assert ACTIONS["doctor_quick"].base_argv == ("doctor", "--quick")
