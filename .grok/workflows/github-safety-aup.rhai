let meta = #{
    name: "github-safety-aup",
    description: "GitHub repo safety plus SpaceXAI AUP fail-closed coverage audit",
    when_to_use: "Before push or release: secrets, CI hygiene, and Imagine AUP gates",
    phases: [
        #{ title: "Scan", detail: "secrets, GitHub Actions, AUP spend/plan, AUP docs" },
        #{ title: "Verify", detail: "one skeptic per finding" },
        #{ title: "Report", detail: "scratch markdown of confirmed gaps" },
    ],
};

let findings_schema = #{
    "type": "object",
    "required": ["findings"],
    "properties": #{
        "findings": #{
            "type": "array",
            "maxItems": 6,
            "items": #{
                "type": "object",
                "required": ["file", "issue", "severity"],
                "properties": #{
                    "file": #{ "type": "string" },
                    "issue": #{ "type": "string" },
                    "severity": #{ "type": "string" },
                },
            },
        },
    },
};
let verdict_schema = #{
    "type": "object",
    "required": ["real", "reason", "evidence"],
    "properties": #{
        "real": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "evidence": #{ "type": "string" },
    },
};

fn trimmed(s) {
    if type_of(s) == "string" { s.trim(); s } else { "" }
}

fn in_scope(p) {
    let path = trimmed(p);
    if path == "" { return false; }
    if path.contains("tools/") { return true; }
    if path.contains("studio_api/") { return true; }
    if path.contains("web_react/") { return true; }
    if path.contains("web_ui/") { return true; }
    if path.contains("tests/") { return true; }
    if path.contains(".github/") { return true; }
    if path.contains(".grok/") { return true; }
    if path.contains(".grok-plugin/") { return true; }
    if path.contains("config/") { return true; }
    if path.contains("SECURITY.md") { return true; }
    if path.contains("DISCLAIMER.md") { return true; }
    if path.contains(".gitignore") { return true; }
    if path.contains("CHANGELOG.md") { return true; }
    false
}

fn scan_prompt(focus, files, look_for) {
    let p = "Audit this Grok Imagine Cinematic Studio git repo for: ";
    p += focus;
    p += ". Independent community project, not affiliated with xAI. ";
    p += "Read these files with read_file and grep before answering. Do not answer from memory. Files:\n";
    p += files;
    p += "\n";
    p += look_for;
    p += " Report at most 6 items as {file, issue, severity} where severity is blocker, important, or info. ";
    p += "An empty findings list is valid only after you have actually read the listed files.";
    p
}

phase("Scan");
let jobs = [];
jobs.push(#{
    prompt: scan_prompt(
        "GitHub repo secret safety",
        ".gitignore\nSECURITY.md\nDISCLAIMER.md\n.streamlit/secrets.toml.example\nconfig/grok-build.example.toml\nweb_react/.env\n.aup_attestation.json",
        "Look for committed API keys, tokens, .env files, .aup_attestation.json, or .streamlit/secrets.toml that are not gitignored. A finding is a concrete leak or missing ignore rule. Absence of a gitignored local file is not a finding. Quote the ignore line or the leaked path.",
    ),
    label: "scan:secrets",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
jobs.push(#{
    prompt: scan_prompt(
        "GitHub Actions and CI token hygiene",
        ".github/workflows/auto-repin-plugin-catalog.yml\n.github/workflows/cinematic-agent-workflow-ci.yml\n.github/workflows/hol-plugin-scanner.yml\n.github/workflows/monitor-forks.yml\n.github/dependabot.yml",
        "Look for secrets printed to logs, pull_request_target with untrusted checkout, hardcoded tokens, or workflow permissions that are overly broad without a documented reason. A finding must quote a YAML key or step. Do not invent GitHub branch-protection state you cannot read from these files.",
    ),
    label: "scan:actions",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
jobs.push(#{
    prompt: scan_prompt(
        "SpaceXAI AUP fail-closed Imagine spend and planning",
        "tools/aup_gate.py\ntools/imagine_client.py\ntools/batch_runner.py\ntools/character_dna.py\ntools/imagine_bridge.py\ntools/handoff_validate.py\ntools/nsfw_sequence_extender.py\ntools/cli/nsfw_commands.py\n.grok/skills/character-dna-extractor/scripts/dna_inject.py\n.grok/skills/nsfw-sequence-extender/scripts/plan_extension.py",
        "Policy: 18+ imaginary adults, R-rated only, no CSAM/minor-coded tropes, no real-person undress/nudify, nsfw attest for intimate work, 403/429 must not hop Imagine regions. A finding is a function that submits or emits an Imagine prompt (including recap/sound/notes paste) without aup_gate. Quote the function name.",
    ),
    label: "scan:aup-code",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
jobs.push(#{
    prompt: scan_prompt(
        "SpaceXAI AUP operator docs and attestation UI",
        "tools/doctor_checks.py\nstudio_api/meta.py\nweb_react/src/components/SettingsView.tsx\nweb_react/src/lib/settingsPrefs.ts\nSECURITY.md\nDISCLAIMER.md\n.grok-plugin/marketplace.json",
        "Look for NSFW opt-in without four-flag attestation, missing AUP URL, doctor skipping attestation when NSFW batches exist, or marketplace copy that claims official xAI affiliation. A finding must quote a field or UI label.",
    ),
    label: "scan:aup-ui",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
let scan_results = parallel(jobs);

let findings = [];
let dropped = 0;
for r in scan_results {
    if r == () || !r.success || r.output == () || r.output.findings == () { continue; }
    for f in r.output.findings {
        if f == () { continue; }
        if !in_scope(f.file) {
            dropped += 1;
            continue;
        }
        if findings.len() < 8 { findings.push(f); } else { dropped += 1; }
    }
}
if dropped > 0 { log("dropped " + dropped.to_string() + " out-of-scope or overflow findings"); }
if findings.len() == 0 {
    let empty_md = "# GitHub safety + AUP audit\n\nNo confirmed secrets, CI, or SpaceXAI AUP gaps in the scanned files.\n";
    let empty_path = write_scratch_file("github-safety-aup.md", empty_md);
    complete(#{ summary: "No findings.", confirmed: [], path: empty_path });
}

phase("Verify");
let vjobs = [];
for f in findings {
    let issue_q = json_encode(f.issue);
    let file_q = json_encode(f.file);
    let vp = "Adversarially verify this GitHub-safety or SpaceXAI AUP finding by reading the shipped file. ";
    vp += "File: ";
    vp += file_q;
    vp += " Claim: ";
    vp += issue_q;
    vp += " Use read_file and grep. Set real=true only with a quoted line you independently inspected. ";
    vp += "Match evidence to the claim type — do not require an Imagine emit path for CI, doctor, or docs claims. ";
    vp += "Secrets: a committed token or a missing gitignore rule. ";
    vp += "CI: missing workflow permissions, persist-credentials left true on a no-push job, write tokens without a comment, or a scheduled/write job with no github.repository owner guard. ";
    vp += "AUP code: an Imagine emit/submit/paste path without aup_gate. ";
    vp += "Doctor: idle/attest logic that ignores committed NSFW JSON. ";
    vp += "Docs: missing AUP URL or four-flag attest where the file already discusses NSFW. ";
    vp += "Otherwise real=false. Do not treat docs that already warn correctly as findings.";
    vjobs.push(#{
        prompt: vp,
        label: "verify-safety",
        capability_mode: "read-only",
        output_schema: verdict_schema,
    });
}
let verdicts = parallel(vjobs);

let confirmed = [];
let idx = 0;
for v in verdicts {
    if v != () && v.success && v.output != () && v.output.real == true {
        let evidence = trimmed(v.output.evidence);
        if evidence != "" { confirmed.push(findings[idx]); }
    }
    idx += 1;
}
log(confirmed.len().to_string() + "/" + findings.len().to_string() + " findings survived verification");

phase("Report");
let md = "# GitHub safety + AUP audit\n\nConfirmed gaps:\n\n";
if confirmed.len() == 0 {
    md = "# GitHub safety + AUP audit\n\nScan produced findings but none survived adversarial verification.\n";
} else {
    for c in confirmed {
        md += "- `";
        md += trimmed(c.file);
        md += "` (";
        md += trimmed(c.severity);
        md += "): ";
        md += trimmed(c.issue);
        md += "\n";
    }
}
let report_path = write_scratch_file("github-safety-aup.md", md);
complete(#{ summary: confirmed.len().to_string() + " confirmed findings", confirmed: confirmed, path: report_path });
