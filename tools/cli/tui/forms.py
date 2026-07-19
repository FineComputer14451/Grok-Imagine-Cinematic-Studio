# tools/cli/tui/forms.py
"""Pure cockpit workflow specs: form fields → CLI argv (no Textual)."""

from __future__ import annotations

from dataclasses import dataclass


VALID_QUOTA_TIERS: frozenset[str] = frozenset(
    {"supergrok_pro", "supergrok_heavy", "custom"}
)


@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    required: bool = False
    default: str = ""
    help: str = ""


@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    label: str
    description: str
    fields: tuple[FormField, ...]
    needs_confirm: bool = True


COCKPIT_WORKFLOWS: dict[str, WorkflowSpec] = {
    "bible_create": WorkflowSpec(
        id="bible_create",
        label="Create Production Bible",
        description="Non-interactive create-bible (no wizard)",
        fields=(
            FormField("title", "Project title", required=True),
            FormField("genre", "Genre", default="Cinematic"),
            FormField("chat_model", "Chat model", default="grok-4.5"),
            FormField("video_model", "Video model", default="grok-imagine-video"),
            FormField("output", "Output path", default="production_bible.json"),
        ),
        needs_confirm=True,
    ),
    "dna_init": WorkflowSpec(
        id="dna_init",
        label="Init Character DNA",
        description="Scaffold a Character DNA profile",
        fields=(
            FormField("name", "Character name", required=True),
            FormField("core", "Core identity", help="--core"),
            FormField("facial", "Facial DNA", help="--facial"),
            FormField("hair", "Hair & grooming", help="--hair"),
            FormField("clothing", "Clothing & style", help="--clothing"),
            FormField("emotion", "Emotional baseline", help="--emotion"),
        ),
        needs_confirm=True,
    ),
    "sequence_init": WorkflowSpec(
        id="sequence_init",
        label="Init Sequence",
        description="Create a long-form sequence blueprint",
        fields=(
            FormField("name", "Sequence name", required=True),
            FormField("duration", "Target duration (seconds)", default="60"),
            FormField("genre", "Genre"),
        ),
        needs_confirm=True,
    ),
    "quota_budget": WorkflowSpec(
        id="quota_budget",
        label="Set Quota Budget",
        description="Set subscription tier and remaining credits",
        fields=(
            FormField(
                "tier",
                "Tier (supergrok_pro|supergrok_heavy|custom)",
                required=True,
                default="supergrok_pro",
            ),
            FormField("remaining", "Remaining credits (optional)"),
        ),
        needs_confirm=True,
    ),
    "models_verify": WorkflowSpec(
        id="models_verify",
        label="Models Verify",
        description="Check model stack compatibility",
        fields=(),
        needs_confirm=False,
    ),
}

COCKPIT_ORDER: tuple[str, ...] = (
    "bible_create",
    "dna_init",
    "sequence_init",
    "quota_budget",
    "models_verify",
)


def default_answers(workflow_id: str) -> dict[str, str]:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    if spec is None:
        return {}
    return {f.key: f.default for f in spec.fields}


def validate_answers(workflow_id: str, answers: dict[str, str]) -> list[str]:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    if spec is None:
        return [f"Unknown workflow: {workflow_id}"]
    errors: list[str] = []
    for field in spec.fields:
        raw = (answers.get(field.key) or "").strip()
        if field.required and not raw:
            errors.append(f"{field.label} is required")
    if workflow_id == "sequence_init":
        dur = (answers.get("duration") or "60").strip() or "60"
        try:
            n = int(dur)
            if n <= 0:
                errors.append("Duration must be a positive integer")
        except ValueError:
            errors.append("Duration must be a positive integer")
    if workflow_id == "quota_budget":
        tier = (answers.get("tier") or "").strip()
        if tier and tier not in VALID_QUOTA_TIERS:
            errors.append(
                f"Unknown tier '{tier}'. Choose: {', '.join(sorted(VALID_QUOTA_TIERS))}"
            )
        rem = (answers.get("remaining") or "").strip()
        if rem:
            try:
                float(rem)
            except ValueError:
                errors.append("Remaining credits must be a number")
    return errors


def answers_to_argv(workflow_id: str, answers: dict[str, str]) -> list[str]:
    errors = validate_answers(workflow_id, answers)
    if errors:
        raise ValueError("; ".join(errors))
    if workflow_id == "bible_create":
        return [
            "create-bible",
            answers["title"].strip(),
            "--genre",
            (answers.get("genre") or "Cinematic").strip() or "Cinematic",
            "--chat-model",
            (answers.get("chat_model") or "grok-4.5").strip() or "grok-4.5",
            "--video-model",
            (answers.get("video_model") or "grok-imagine-video").strip()
            or "grok-imagine-video",
            "-o",
            (answers.get("output") or "production_bible.json").strip()
            or "production_bible.json",
        ]
    if workflow_id == "dna_init":
        argv = ["dna", "init", answers["name"].strip()]
        for key, flag in (
            ("core", "--core"),
            ("facial", "--facial"),
            ("hair", "--hair"),
            ("clothing", "--clothing"),
            ("emotion", "--emotion"),
        ):
            val = (answers.get(key) or "").strip()
            if val:
                argv.extend([flag, val])
        return argv
    if workflow_id == "sequence_init":
        dur = (answers.get("duration") or "60").strip() or "60"
        argv = ["sequence", "init", answers["name"].strip(), "-d", str(int(dur))]
        genre = (answers.get("genre") or "").strip()
        if genre:
            argv.extend(["-g", genre])
        return argv
    if workflow_id == "quota_budget":
        argv = ["quota", "budget", "--tier", answers["tier"].strip()]
        rem = (answers.get("remaining") or "").strip()
        if rem:
            argv.extend(["--remaining", rem])
        return argv
    if workflow_id == "models_verify":
        return ["models", "verify"]
    raise ValueError(f"Unknown workflow: {workflow_id}")


def summarize_action(workflow_id: str, answers: dict[str, str]) -> str:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    label = spec.label if spec else workflow_id
    argv = answers_to_argv(workflow_id, answers)
    return f"{label}\n\nCommand:\n  cinematic-studio {' '.join(argv)}"
