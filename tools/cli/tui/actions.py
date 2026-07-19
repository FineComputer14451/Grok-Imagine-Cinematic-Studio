"""Unified TUI action registry: launcher + cockpit, pure (no Textual).

Single ActionSpec model. Screens only run actions by id + answers;
argv is built and validated here. Forbidden tokens are never emitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


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

Surface = str  # "launcher" | "cockpit"


@dataclass(frozen=True)
class FormField:
    """One form input. Maps to a CLI flag or a positional after base_argv."""

    key: str
    label: str
    required: bool = False
    default: str = ""
    help: str = ""
    # None → positional (appended in field order after base_argv)
    flag: str | None = None
    omit_if_empty: bool = True
    coerce: str | None = None  # "int" | "float" | None
    choices: frozenset[str] | None = None
    positive: bool = False  # for numeric: must be > 0


@dataclass(frozen=True)
class ActionSpec:
    id: str
    label: str
    description: str
    base_argv: tuple[str, ...]
    surfaces: frozenset[str]
    fields: tuple[FormField, ...] = ()
    needs_confirm: bool = False

    @property
    def is_launcher(self) -> bool:
        return "launcher" in self.surfaces

    @property
    def is_cockpit(self) -> bool:
        return "cockpit" in self.surfaces

    @property
    def has_form(self) -> bool:
        return bool(self.fields)


def _f(
    key: str,
    label: str,
    *,
    required: bool = False,
    default: str = "",
    help: str = "",
    flag: str | None = None,
    omit_if_empty: bool = True,
    coerce: str | None = None,
    choices: frozenset[str] | None = None,
    positive: bool = False,
) -> FormField:
    return FormField(
        key=key,
        label=label,
        required=required,
        default=default,
        help=help,
        flag=flag,
        omit_if_empty=omit_if_empty,
        coerce=coerce,
        choices=choices,
        positive=positive,
    )


VALID_QUOTA_TIERS: frozenset[str] = frozenset(
    {"supergrok_pro", "supergrok_heavy", "custom"}
)

# Stable display order per surface
LAUNCHER_ORDER: tuple[str, ...] = (
    "status",
    "dashboard_compact",
    "models_list",
    "models_verify",
    "quota_dashboard",
    "dna_list",
    "sequence_list",
    "imagine_list",
    "plugin_list",
)

COCKPIT_ORDER: tuple[str, ...] = (
    "bible_create",
    "dna_init",
    "sequence_init",
    "quota_budget",
    "models_verify",
)

ACTIONS: dict[str, ActionSpec] = {
    # --- launcher (read-only, no form) ---
    "status": ActionSpec(
        id="status",
        label="Studio status",
        description="Version, agents, activation",
        base_argv=("status",),
        surfaces=frozenset({"launcher"}),
    ),
    "dashboard_compact": ActionSpec(
        id="dashboard_compact",
        label="Dashboard (compact)",
        description="Summary panels only",
        base_argv=("dashboard", "--compact"),
        surfaces=frozenset({"launcher"}),
    ),
    "models_list": ActionSpec(
        id="models_list",
        label="Models list",
        description="Registered model stack",
        base_argv=("models", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    "models_verify": ActionSpec(
        id="models_verify",
        label="Models Verify",
        description="Check model stack compatibility",
        base_argv=("models", "verify"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
    ),
    "quota_dashboard": ActionSpec(
        id="quota_dashboard",
        label="Quota dashboard",
        description="Session spend and budget",
        base_argv=("quota", "dashboard"),
        surfaces=frozenset({"launcher"}),
    ),
    "dna_list": ActionSpec(
        id="dna_list",
        label="DNA list",
        description="Character DNA profiles",
        base_argv=("dna", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    "sequence_list": ActionSpec(
        id="sequence_list",
        label="Sequences list",
        description="Long-form sequences",
        base_argv=("sequence", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    "imagine_list": ActionSpec(
        id="imagine_list",
        label="Imagine jobs",
        description="Recent Imagine jobs",
        base_argv=("imagine", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    "plugin_list": ActionSpec(
        id="plugin_list",
        label="Plugin list",
        description="Installed plugin skills",
        base_argv=("plugin", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    # --- cockpit (mutating / forms) ---
    "bible_create": ActionSpec(
        id="bible_create",
        label="Create Production Bible",
        description="Non-interactive create-bible (no wizard)",
        base_argv=("create-bible",),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        fields=(
            _f("title", "Project title", required=True),
            _f("genre", "Genre", default="Cinematic", flag="--genre"),
            _f("chat_model", "Chat model", default="grok-4.5", flag="--chat-model"),
            _f(
                "video_model",
                "Video model",
                default="grok-imagine-video",
                flag="--video-model",
            ),
            _f(
                "output",
                "Output path",
                default="production_bible.json",
                flag="-o",
                omit_if_empty=False,
            ),
        ),
    ),
    "dna_init": ActionSpec(
        id="dna_init",
        label="Init Character DNA",
        description="Scaffold a Character DNA profile",
        base_argv=("dna", "init"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        fields=(
            _f("name", "Character name", required=True),
            _f("core", "Core identity", flag="--core", help="--core"),
            _f("facial", "Facial DNA", flag="--facial", help="--facial"),
            _f("hair", "Hair & grooming", flag="--hair", help="--hair"),
            _f("clothing", "Clothing & style", flag="--clothing", help="--clothing"),
            _f("emotion", "Emotional baseline", flag="--emotion", help="--emotion"),
        ),
    ),
    "sequence_init": ActionSpec(
        id="sequence_init",
        label="Init Sequence",
        description="Create a long-form sequence blueprint",
        base_argv=("sequence", "init"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        fields=(
            _f("name", "Sequence name", required=True),
            _f(
                "duration",
                "Target duration (seconds)",
                default="60",
                flag="-d",
                coerce="int",
                positive=True,
                omit_if_empty=False,
            ),
            _f("genre", "Genre", flag="-g"),
        ),
    ),
    "quota_budget": ActionSpec(
        id="quota_budget",
        label="Set Quota Budget",
        description="Set subscription tier and remaining credits",
        base_argv=("quota", "budget"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        fields=(
            _f(
                "tier",
                "Tier (supergrok_pro|supergrok_heavy|custom)",
                required=True,
                default="supergrok_pro",
                flag="--tier",
                choices=VALID_QUOTA_TIERS,
                omit_if_empty=False,
            ),
            _f(
                "remaining",
                "Remaining credits (optional)",
                flag="--remaining",
                coerce="float",
            ),
        ),
    ),
}


def get_action(action_id: str) -> ActionSpec:
    try:
        return ACTIONS[action_id]
    except KeyError as exc:
        raise KeyError(f"Unknown action: {action_id}") from exc


def actions_for(surface: Surface) -> list[ActionSpec]:
    order = LAUNCHER_ORDER if surface == "launcher" else COCKPIT_ORDER
    out: list[ActionSpec] = []
    for aid in order:
        spec = ACTIONS[aid]
        if surface in spec.surfaces:
            out.append(spec)
    return out


def default_answers(action_id: str) -> dict[str, str]:
    try:
        spec = get_action(action_id)
    except KeyError:
        return {}
    return {f.key: f.default for f in spec.fields}


def _coerce_value(field: FormField, raw: str) -> tuple[str | None, str | None]:
    """Return (normalized_string, error)."""
    if field.coerce == "int":
        try:
            n = int(raw)
        except ValueError:
            return None, f"{field.label} must be a positive integer" if field.positive else f"{field.label} must be an integer"
        if field.positive and n <= 0:
            return None, f"{field.label} must be a positive integer"
        return str(n), None
    if field.coerce == "float":
        try:
            float(raw)
        except ValueError:
            return None, f"{field.label} must be a number"
        return raw, None
    return raw, None


def validate_answers(action_id: str, answers: dict[str, str]) -> list[str]:
    try:
        spec = get_action(action_id)
    except KeyError:
        return [f"Unknown workflow: {action_id}"]

    errors: list[str] = []
    for field in spec.fields:
        raw = (answers.get(field.key) or "").strip()
        if field.required and not raw:
            errors.append(f"{field.label} is required")
            continue
        if not raw:
            continue
        if field.choices is not None and raw not in field.choices:
            choices = ", ".join(sorted(field.choices))
            errors.append(f"Unknown {field.key} '{raw}'. Choose: {choices}")
            continue
        _, err = _coerce_value(field, raw)
        if err:
            # duration wording expected by tests
            if field.key == "duration":
                errors.append("Duration must be a positive integer")
            elif field.key == "remaining":
                errors.append("Remaining credits must be a number")
            else:
                errors.append(err)
    return errors


def answers_to_argv(action_id: str, answers: dict[str, str]) -> list[str]:
    errors = validate_answers(action_id, answers)
    if errors:
        raise ValueError("; ".join(errors))

    spec = get_action(action_id)
    argv: list[str] = list(spec.base_argv)

    positionals = [f for f in spec.fields if f.flag is None]
    flags = [f for f in spec.fields if f.flag is not None]

    for field in positionals:
        raw = (answers.get(field.key) or field.default or "").strip()
        if not raw and field.omit_if_empty:
            continue
        argv.append(raw)

    for field in flags:
        raw = (answers.get(field.key) or "").strip()
        if not raw:
            raw = field.default
        raw = (raw or "").strip()
        if not raw and field.omit_if_empty:
            continue
        if field.coerce:
            normalized, err = _coerce_value(field, raw)
            if err or normalized is None:
                raise ValueError(err or f"invalid {field.key}")
            raw = normalized
        assert field.flag is not None
        argv.extend([field.flag, raw])

    reject_forbidden_argv(argv)
    return argv


def reject_forbidden_argv(argv: Iterable[str]) -> None:
    bad = [t for t in argv if t in FORBIDDEN_ARGV_TOKENS]
    if bad:
        raise ValueError(f"Forbidden argv token(s): {', '.join(bad)}")


def summarize_action(action_id: str, answers: dict[str, str]) -> str:
    try:
        spec = get_action(action_id)
        label = spec.label
    except KeyError:
        label = action_id
    argv = answers_to_argv(action_id, answers)
    return f"{label}\n\nCommand:\n  cinematic-studio {' '.join(argv)}"


def static_allowed_argvs() -> frozenset[tuple[str, ...]]:
    """Exact argv tuples for field-less actions (read-only allowlist)."""
    return frozenset(
        tuple(spec.base_argv) for spec in ACTIONS.values() if not spec.fields
    )


# --- backward-compatible aliases used by older tests / imports ---

@dataclass(frozen=True)
class LauncherEntry:
    id: str
    label: str
    description: str
    argv: list[str]


@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    label: str
    description: str
    fields: tuple[FormField, ...]
    needs_confirm: bool = True


def _launcher_entry(spec: ActionSpec) -> LauncherEntry:
    return LauncherEntry(
        id=spec.id,
        label=spec.label,
        description=spec.description,
        argv=list(spec.base_argv),
    )


def _workflow_spec(spec: ActionSpec) -> WorkflowSpec:
    return WorkflowSpec(
        id=spec.id,
        label=spec.label,
        description=spec.description,
        fields=spec.fields,
        needs_confirm=spec.needs_confirm,
    )


LAUNCHER_CATALOG: tuple[LauncherEntry, ...] = tuple(
    _launcher_entry(ACTIONS[aid]) for aid in LAUNCHER_ORDER if ACTIONS[aid].is_launcher
)

COCKPIT_WORKFLOWS: dict[str, WorkflowSpec] = {
    aid: _workflow_spec(ACTIONS[aid]) for aid in COCKPIT_ORDER if ACTIONS[aid].is_cockpit
}
