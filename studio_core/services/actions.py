"""Unified action registry (launcher + cockpit) — UI-agnostic.

Single ActionSpec model shared by Textual TUI, future NiceGUI/Web, and API.
Screens/forms only run actions by id + answers; argv is built and validated
here. Forbidden tokens are never emitted.

No Textual/Streamlit/Rich imports — pure Python.
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


# Display labels for cockpit group separators (v3 UX)
COCKPIT_GROUP_LABELS: dict[str, str] = {
    "setup": "Setup",
    "dna": "DNA",
    "sequence": "Sequence",
    "quota": "Quota",
    "delivery": "Delivery",
    "multiagent": "Multi-agent",
    "files": "Files",
    "health": "Health",
}


@dataclass(frozen=True)
class ActionSpec:
    id: str
    label: str
    description: str
    base_argv: tuple[str, ...]
    surfaces: frozenset[str]
    fields: tuple[FormField, ...] = ()
    needs_confirm: bool = False
    group: str = ""  # cockpit section id; empty = no separator

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

VALID_ASPECTS: frozenset[str] = frozenset({"16:9", "9:16", "1:1"})

# Stable display order per surface
LAUNCHER_ORDER: tuple[str, ...] = (
    "status",
    "dashboard_compact",
    "doctor_quick",
    "models_list",
    "models_verify",
    "validate",
    "stack",
    "quota_dashboard",
    "quota_sync",
    "dna_list",
    "dna_show",
    "sequence_list",
    "sequence_show",
    "handoff_validate",
    "imagine_bridge",
    "imagine_list",
    "files_list",
    "files_get",
    "plugin_list",
)

# Setup → Quota → DNA → Sequence → Delivery → Multi-agent → Files → Health
COCKPIT_ORDER: tuple[str, ...] = (
    "bible_create",
    "quota_budget",
    "quota_sequence_estimate",
    "quota_sync",
    "dna_init",
    "dna_lock",
    "dna_handoff",
    "sequence_init",
    "sequence_add_clip",
    "sequence_handoff",
    "sequence_polish_dry",
    "sequence_deliver_dry",
    "wave_a_briefs",
    "imagine_bridge",
    "files_list",
    "files_get",
    "files_upload",
    "files_delete",
    "handoff_validate",
    "doctor_quick",
    "models_verify",
    "validate",
    "stack",
)

ACTIONS: dict[str, ActionSpec] = {
    # --- read-only / health (field-less) ---
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
    "doctor_quick": ActionSpec(
        id="doctor_quick",
        label="Grok Doctor (quick)",
        description="Studio health check (skip long pytest/plugin verify)",
        base_argv=("doctor", "--quick"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="health",
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
        group="health",
    ),
    "validate": ActionSpec(
        id="validate",
        label="Studio validate",
        description="Docs, skills, models, workspace paths",
        base_argv=("validate",),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="health",
    ),
    "stack": ActionSpec(
        id="stack",
        label="Model stack",
        description="Locked Grok 4.6 stack + VIDEO_PIPELINE_SPEC",
        base_argv=("stack",),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="health",
    ),
    "quota_dashboard": ActionSpec(
        id="quota_dashboard",
        label="Quota dashboard",
        description="Session spend, cascade, and burn risk",
        base_argv=("quota", "dashboard"),
        surfaces=frozenset({"launcher"}),
    ),
    "quota_sync": ActionSpec(
        id="quota_sync",
        label="Quota sync",
        description="Exclusive cascade recon + ledger alignment (no Imagine spend)",
        base_argv=("quota", "sync"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="quota",
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
    "files_list": ActionSpec(
        id="files_list",
        label="Files list",
        description="List xAI Files API objects (paginated metadata)",
        base_argv=("files", "list"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="files",
    ),
    "files_get": ActionSpec(
        id="files_get",
        label="Files get",
        description="Show metadata for one stored file_id",
        base_argv=("files", "get"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="files",
        fields=(_f("file_id", "Files API id (file_…)", required=True),),
    ),
    "files_upload": ActionSpec(
        id="files_upload",
        label="Files upload",
        description="Upload a local plate (max 50 MB) and print file_id",
        base_argv=("files", "upload"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="files",
        fields=(
            _f("path", "Local file path (max 50 MB)", required=True),
            _f(
                "expires_after",
                "TTL seconds (3600–2592000)",
                flag="--expires-after",
                coerce="int",
            ),
            _f(
                "purpose",
                "Purpose label",
                default="assistants",
                flag="--purpose",
            ),
            _f(
                "dry_run",
                "Type --dry-run to mock (empty = live)",
                omit_if_empty=True,
            ),
        ),
    ),
    "files_delete": ActionSpec(
        id="files_delete",
        label="Files delete",
        description="Delete a stored file (requires --yes)",
        base_argv=("files", "delete"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="files",
        fields=(
            _f("file_id", "Files API id to delete", required=True),
            _f(
                "yes",
                "Must be --yes",
                default="--yes",
                omit_if_empty=False,
            ),
        ),
    ),
    "plugin_list": ActionSpec(
        id="plugin_list",
        label="Plugin list",
        description="Installed plugin skills",
        base_argv=("plugin", "list"),
        surfaces=frozenset({"launcher"}),
    ),
    "handoff_validate": ActionSpec(
        id="handoff_validate",
        label="Validate handoff packet",
        description="Schema + soft readiness check on a handoff JSON (no spend)",
        base_argv=("handoff", "validate"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="health",
        fields=(
            _f(
                "path",
                "Handoff JSON path",
                required=True,
                flag=None,
                help="Path to handoff_*.json",
            ),
        ),
    ),
    "sequence_polish_dry": ActionSpec(
        id="sequence_polish_dry",
        label="Polish (dry-run)",
        description="Delivery polish readiness + dry-run upscale plan (no real upscale)",
        base_argv=("sequence", "polish"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=False,
        group="delivery",
        fields=(
            _f("name", "Sequence name or slug", required=True),
            _f(
                "dry_run",
                "Must be --dry-run",
                default="--dry-run",
                flag=None,
                omit_if_empty=False,
            ),
        ),
    ),
    "sequence_deliver_dry": ActionSpec(
        id="sequence_deliver_dry",
        label="Deliver (dry-run)",
        description="Delivery masters dry-run (no ffmpeg write)",
        base_argv=("sequence", "deliver"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=False,
        group="delivery",
        fields=(
            _f("name", "Sequence name or slug", required=True),
            _f(
                "dry_run",
                "Must be --dry-run",
                default="--dry-run",
                flag=None,
                omit_if_empty=False,
            ),
        ),
    ),
    "wave_a_briefs": ActionSpec(
        id="wave_a_briefs",
        label="Parallel Brief log (starter)",
        description="Build parallel_brief_dispatch_log packet (Wave A)",
        base_argv=("wave-a", "briefs"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=False,
        group="multiagent",
        fields=(
            _f("session_id", "Session id", required=True),
            _f(
                "to",
                "Specialist slug",
                default="plate-motion-readiness-lead",
                flag="--to",
            ),
            _f("scope", "Scope", default="lock plate + motion", flag="--scope"),
            _f(
                "output",
                "Output path",
                default="artifacts/briefs_session.json",
                flag="-o",
            ),
        ),
    ),
    "imagine_bridge": ActionSpec(
        id="imagine_bridge",
        label="Imagine bridge preview",
        description="Emit grok.com/imagine copy-paste packet (markdown, no spend)",
        base_argv=("imagine", "bridge"),
        surfaces=frozenset({"launcher", "cockpit"}),
        needs_confirm=False,
        group="multiagent",
        fields=(
            _f("sequence", "Sequence slug", flag="-s"),
            _f("clip", "Clip id", flag="-c"),
            _f("batch", "SFW batch slug", flag="-b"),
            _f("shot", "Shot id", flag="--shot"),
            _f(
                "format",
                "format",
                default="markdown",
                flag="-f",
                omit_if_empty=False,
            ),
        ),
    ),
    # --- read-only with form (no confirm) ---
    "dna_show": ActionSpec(
        id="dna_show",
        label="Show DNA",
        description="Display a Character DNA profile",
        base_argv=("dna", "show"),
        surfaces=frozenset({"launcher"}),
        needs_confirm=False,
        fields=(
            _f("name", "Character name or slug", required=True),
            _f("mode", "Inject mode (optional)", flag="-m"),
        ),
    ),
    "sequence_show": ActionSpec(
        id="sequence_show",
        label="Show sequence",
        description="Display a sequence blueprint",
        base_argv=("sequence", "show"),
        surfaces=frozenset({"launcher"}),
        needs_confirm=False,
        fields=(_f("name", "Sequence name or slug", required=True),),
    ),
    # --- cockpit mutating / forms ---
    "bible_create": ActionSpec(
        id="bible_create",
        label="Create Production Bible",
        description="Non-interactive create-bible (no wizard)",
        base_argv=("create-bible",),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="setup",
        fields=(
            _f("title", "Project title", required=True),
            _f("genre", "Genre", default="Cinematic", flag="--genre"),
            _f("chat_model", "Chat model", default="grok-4.6", flag="--chat-model"),
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
        group="dna",
        fields=(
            _f("name", "Character name", required=True),
            _f("core", "Core identity", flag="--core", help="--core"),
            _f("facial", "Facial DNA", flag="--facial", help="--facial"),
            _f("hair", "Hair & grooming", flag="--hair", help="--hair"),
            _f("clothing", "Clothing & style", flag="--clothing", help="--clothing"),
            _f("emotion", "Emotional baseline", flag="--emotion", help="--emotion"),
        ),
    ),
    "dna_lock": ActionSpec(
        id="dna_lock",
        label="Lock Character DNA",
        description="Import DNA into Identity Lock memory bank",
        base_argv=("dna", "lock"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="dna",
        fields=(_f("name", "Character name or slug", required=True),),
    ),
    "dna_handoff": ActionSpec(
        id="dna_handoff",
        label="DNA Identity Handoff",
        description="Generate Identity Lock handoff packet",
        base_argv=("dna", "handoff"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="dna",
        fields=(
            _f("name", "Character name or slug", required=True),
            _f("output", "Output handoff.json path", flag="-o"),
        ),
    ),
    "sequence_init": ActionSpec(
        id="sequence_init",
        label="Init Sequence",
        description="Create a long-form sequence blueprint",
        base_argv=("sequence", "init"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="sequence",
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
    "sequence_add_clip": ActionSpec(
        id="sequence_add_clip",
        label="Add Sequence Clip",
        description="Add a clip to the sequence chain",
        base_argv=("sequence", "add-clip"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="sequence",
        fields=(
            _f("name", "Sequence name or slug", required=True),
            _f("prompt", "Clip prompt", required=True, flag="-p"),
            _f(
                "duration",
                "Clip duration (seconds)",
                default="10",
                flag="-d",
                coerce="int",
                positive=True,
                omit_if_empty=False,
            ),
            _f("recap", "LAST_FRAME_RECAP", flag="-r"),
            _f(
                "aspect",
                "Aspect (16:9|9:16|1:1)",
                default="16:9",
                flag="-a",
                choices=VALID_ASPECTS,
                omit_if_empty=False,
            ),
            _f("ref", "reference_image_id", flag="--ref"),
            _f(
                "transition",
                "Transition",
                default="invisible_edit",
                flag="-t",
                omit_if_empty=False,
            ),
            _f("action", "Momentum: last action", flag="--action"),
            _f("emotion", "Momentum: emotional state", flag="--emotion"),
            _f("dialogue", "Audio momentum: dialogue", flag="--dialogue"),
        ),
    ),
    "sequence_handoff": ActionSpec(
        id="sequence_handoff",
        label="Sequence Clip Handoff",
        description="Generate extend/stitch handoff from a clip",
        base_argv=("sequence", "handoff"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="sequence",
        fields=(
            _f("name", "Sequence name or slug", required=True),
            _f("clip", "Source clip ID", required=True, flag="-c"),
            _f("output", "Output path", flag="-o"),
        ),
    ),
    "quota_budget": ActionSpec(
        id="quota_budget",
        label="Set Quota Budget",
        description="Set subscription tier and remaining credits",
        base_argv=("quota", "budget"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=True,
        group="quota",
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
    "quota_sequence_estimate": ActionSpec(
        id="quota_sequence_estimate",
        label="Estimate Sequence Quota",
        description="Estimate cost for an existing sequence (no spend)",
        base_argv=("quota", "sequence"),
        surfaces=frozenset({"cockpit"}),
        needs_confirm=False,
        group="quota",
        fields=(_f("name", "Sequence name or slug", required=True),),
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


def palette_actions() -> list[ActionSpec]:
    """Deduped launcher+cockpit actions for the command palette (`/`)."""
    seen: set[str] = set()
    out: list[ActionSpec] = []
    for aid in (*LAUNCHER_ORDER, *COCKPIT_ORDER):
        if aid in seen:
            continue
        seen.add(aid)
        try:
            out.append(ACTIONS[aid])
        except KeyError:
            continue
    return out


def filter_palette_actions(query: str) -> list[ActionSpec]:
    """Case-insensitive substring filter over label, id, description, argv."""
    q = (query or "").strip().lower()
    if not q:
        return palette_actions()
    hits: list[ActionSpec] = []
    for spec in palette_actions():
        hay = (
            f"{spec.label} {spec.id} {spec.description} "
            f"{' '.join(spec.base_argv)} {spec.group}"
        ).lower()
        if q in hay:
            hits.append(spec)
    return hits


def menu_rows(surface: Surface) -> list[tuple[str, str | ActionSpec]]:
    """Build menu rows: ('group', label) separators and ('action', ActionSpec).

    Group separators appear only for cockpit when ActionSpec.group is set.
    """
    rows: list[tuple[str, str | ActionSpec]] = []
    last_group = ""
    for spec in actions_for(surface):
        if surface == "cockpit" and spec.group and spec.group != last_group:
            last_group = spec.group
            title = COCKPIT_GROUP_LABELS.get(spec.group, spec.group)
            rows.append(("group", title))
        rows.append(("action", spec))
    return rows


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
