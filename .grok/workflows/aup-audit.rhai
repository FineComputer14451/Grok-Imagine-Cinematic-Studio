let meta = #{
    name: "aup-audit",
    description: "Fail-closed SpaceXAI AUP coverage audit of Imagine spend, planning packets, and attestation UI",
    when_to_use: "Audit AUP gates, nsfw attest, or Imagine spend/plan bypasses",
    phases: [
        #{ title: "Scan", detail: "spend, planning, attestation UI" },
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
    if path.contains("tests/") { return true; }
    false
}

fn scan_prompt(focus, files) {
    let p = "Audit SpaceXAI AUP fail-closed coverage for: ";
    p += focus;
    p += ". Policy: 18+ imaginary adults, R-rated only, no CSAM/minor-coded tropes, no real-person undress/nudify, no hidden-camera NCII, nsfw attest required for intimate work, 403/429 must not hop Imagine regions. ";
    p += "Read these files with read_file and grep before answering. Do not answer from memory. Files:\n";
    p += files;
    p += "\nLook for Imagine spend or planning paths that skip tools/aup_gate.py (gate_imagine_prompt, gate_text, gate_nsfw_shot, require_attestation). ";
    p += "A finding is a concrete bypass: a function that submits or emits an Imagine prompt without the gate. ";
    p += "Report at most 6 items as {file, issue, severity} where severity is blocker, important, or info. ";
    p += "An empty findings list is valid only after you have actually read the listed files and found no ungated path.";
    p
}

phase("Scan");
let jobs = [];
jobs.push(#{
    prompt: scan_prompt(
        "Imagine API spend",
        "tools/aup_gate.py\ntools/imagine_client.py\ntools/batch_runner.py\ntools/character_dna.py\ntools/imagine_regions.py",
    ),
    label: "scan:spend",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
jobs.push(#{
    prompt: scan_prompt(
        "planning packets and NSFW extend",
        "tools/cli/nsfw_commands.py\ntools/nsfw_sequence_extender.py\ntools/cli/bible_commands.py\ntools/imagine_bridge.py\ntools/handoff_validate.py",
    ),
    label: "scan:plan",
    capability_mode: "read-only",
    output_schema: findings_schema,
});
jobs.push(#{
    prompt: scan_prompt(
        "attestation, doctor, React/API opt-in",
        "tools/doctor.py\ntools/doctor_checks.py\nstudio_api/meta.py\nstudio_api/app.py\nweb_react/src/lib/settingsPrefs.ts\nweb_react/src/components/SettingsView.tsx\nweb_react/src/components/Layout.tsx",
    ),
    label: "scan:attest",
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
        if findings.len() < 6 { findings.push(f); } else { dropped += 1; }
    }
}
if dropped > 0 { log("dropped " + dropped.to_string() + " out-of-scope or overflow findings"); }
if findings.len() == 0 {
    let empty_md = "# AUP audit\n\nNo confirmed ungated Imagine paths in the scanned spend, planning, and attestation files.\n";
    let empty_path = write_scratch_file("aup-audit.md", empty_md);
    complete(#{ summary: "No findings.", confirmed: [], path: empty_path });
}

phase("Verify");
let vjobs = [];
for f in findings {
    let issue_q = json_encode(f.issue);
    let file_q = json_encode(f.file);
    let vp = "Adversarially verify this SpaceXAI AUP audit finding by reading the shipped file. ";
    vp += "File: ";
    vp += file_q;
    vp += " Claim: ";
    vp += issue_q;
    vp += " Use read_file and grep. Set real=true only if you independently inspect a code path that emits or submits an Imagine prompt without aup_gate. Otherwise real=false. Evidence must quote a function or call site.";
    vjobs.push(#{
        prompt: vp,
        label: "verify-aup",
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
let md = "# AUP audit\n\nConfirmed ungated or weak SpaceXAI AUP paths:\n\n";
if confirmed.len() == 0 {
    md = "# AUP audit\n\nScan produced findings but none survived adversarial verification.\n";
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
let report_path = write_scratch_file("aup-audit.md", md);
complete(#{ summary: confirmed.len().to_string() + " confirmed findings", confirmed: confirmed, path: report_path });
