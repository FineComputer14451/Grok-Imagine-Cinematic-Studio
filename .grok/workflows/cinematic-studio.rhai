let meta = #{
    name: "cinematic-studio",
    description: "Parallel Brief a production request into an imagine_agent_mode_handoff packet",
    when_to_use: "New cinematic scene or stills brief: specialist Parallel Briefs, handoff verify, director packet",
    phases: [
        #{ title: "Briefs", detail: "DoP, Prompt Master, Quota, Identity in parallel" },
        #{ title: "Verify", detail: "skeptic against required handoff fields" },
        #{ title: "Report", detail: "director packet to scratch" },
    ],
};

let brief_schema = #{
    "type": "object",
    "required": ["role", "deliverable"],
    "properties": #{
        "role": #{ "type": "string" },
        "deliverable": #{ "type": "string" },
        "notes": #{ "type": "string" },
    },
};
let verdict_schema = #{
    "type": "object",
    "required": ["ready", "reason"],
    "properties": #{
        "ready": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "gaps": #{ "type": "array", "items": #{ "type": "string" } },
    },
};
let packet_schema = #{
    "type": "object",
    "required": ["summary", "prompt", "packet_markdown"],
    "properties": #{
        "summary": #{ "type": "string" },
        "prompt": #{ "type": "string" },
        "packet_markdown": #{ "type": "string" },
        "target_surface": #{ "type": "string" },
        "execution_mode": #{ "type": "string" },
    },
};

fn trimmed(s) {
    if type_of(s) == "string" { s.trim(); s } else { "" }
}

fn aup_block() {
    let t = "AUP: imaginary adults 18+ only. No CSAM, no minor-coded tropes, no real-person likeness, no hidden-camera NCII. ";
    t += "Do not generate images or video; plan and write packets only. Intimate work is R-rated opt-in. ";
    t
}

fn specialist_prompt(role, files, task, brief_q, extra) {
    let p = "You are the ";
    p += role;
    p += " for Grok Imagine Cinematic Studio v3.11.3. ";
    p += aup_block();
    p += "Use read_file and grep on these paths before answering. Do not answer from memory.\n";
    p += files;
    p += "\nProduction brief JSON:\n";
    p += brief_q;
    p += "\nTask: ";
    p += task;
    p += " ";
    p += extra;
    p += " Return {role, deliverable, notes}. deliverable is the specialist packet (camera block, Ultimate Template prompt, quota/surface note, or DNA inject). ";
    p += "Empty deliverable is valid only after you read the listed files and this brief has no work for this role.";
    p
}

let brief = ();
let mode = "image_prompt";
let surface = "grok_build_tools";
let aspect = "16:9";
let nsfw_flag = false;
if args != () {
    brief = args.brief;
    if args.mode != () && type_of(args.mode) == "string" && trimmed(args.mode) != "" { mode = args.mode; }
    if args.surface != () && type_of(args.surface) == "string" && trimmed(args.surface) != "" { surface = args.surface; }
    if args.aspect != () && type_of(args.aspect) == "string" && trimmed(args.aspect) != "" { aspect = args.aspect; }
    if args.nsfw == true { nsfw_flag = true; }
}
if brief == () || trimmed(brief) == "" {
    pause("verification", "Pass args.brief — the scene or production request to Parallel Brief.");
}

let brief_q = json_encode(brief);
let mode_q = json_encode(mode);
let surface_q = json_encode(surface);
let aspect_q = json_encode(aspect);

let extra = "execution_mode=";
extra += mode;
extra += " target_surface=";
extra += surface;
extra += " aspect=";
extra += aspect;
extra += ". ";
if nsfw_flag {
    extra += "NSFW path: ErosForge required. Keep intensity, physics of intimacy, never dilute. Confirmed adults. ";
} else {
    extra += "SFW cinematic path. Suggestive afterglow is ok; do not write an explicit sex-act freeze-frame. ";
}

phase("Briefs");
let jobs = [];
jobs.push(#{
    prompt: specialist_prompt(
        "Director of Photography",
        ".grok/skills/director-of-photography/SKILL.md\nreferences/agents/AGENT_INDEX.md",
        "Design lighting motivation, lens, camera angle, and shallow-DOF composition for this still or first frame.",
        brief_q,
        extra,
    ),
    label: "brief:dop",
    capability_mode: "read-only",
    output_schema: brief_schema,
});
jobs.push(#{
    prompt: specialist_prompt(
        "Imagine Prompt Master",
        ".grok/skills/imagine-prompt-master/SKILL.md\n.grok/skills/grok-imagine-image-tools/SKILL.md",
        "Craft one Ultimate Template image or first-frame prompt. Front-load subject, action, setting, light, style. Natural prose, 2-5 sentences.",
        brief_q,
        extra,
    ),
    label: "brief:prompt",
    capability_mode: "read-only",
    output_schema: brief_schema,
});
jobs.push(#{
    prompt: specialist_prompt(
        "Workflow Quota Optimizer",
        ".grok/skills/workflow-quota-optimizer/SKILL.md\ntools/models.py\ntools/handoff_schema.py",
        "Route still vs video, Image 2.0 vs draft, Video 1.0 vs 1.5, and name quota_note plus model_stack keys chat/build/imagine_image/imagine_video.",
        brief_q,
        extra,
    ),
    label: "brief:quota",
    capability_mode: "read-only",
    output_schema: brief_schema,
});
jobs.push(#{
    prompt: specialist_prompt(
        "Identity Lock Specialist",
        ".grok/skills/identity-lock-specialist/SKILL.md\n.grok/skills/character-dna-extractor/SKILL.md",
        "Write a DNA inject / identity notes block for imaginary adults. If no locked DNA exists, mark pending extract and list must-lock traits from the brief.",
        brief_q,
        extra,
    ),
    label: "brief:identity",
    capability_mode: "read-only",
    output_schema: brief_schema,
});
let results = parallel(jobs);

let briefs = [];
let failed = 0;
for r in results {
    if r == () || !r.success || r.output == () {
        failed += 1;
        continue;
    }
    briefs.push(r.output);
}
if failed > 0 { log(failed.to_string() + " specialist briefs failed or returned empty"); }
if briefs.len() == 0 {
    let empty_md = "# Cinematic Studio Parallel Brief\n\nNo specialist briefs returned.\n";
    let empty_path = write_scratch_file("cinematic-studio-handoff.md", empty_md);
    complete(#{ summary: "No specialist briefs returned.", ready: false, path: empty_path });
}

phase("Verify");
let briefs_q = json_encode(briefs);
let vp = "Adversarially verify whether these Parallel Briefs can become a valid imagine_agent_mode_handoff. ";
vp += "Read tools/handoff_schema.py (IMAGINE_AGENT_MODE_REQUIRED_FIELDS, TARGET_SURFACES, EXECUTION_MODES) before answering. ";
vp += "Required: packet_type, protocol_version, studio_version, target_surface, execution_mode, subject_id, prompt, reference_hints, model_stack, quota_note, return_path, handoff_steps. ";
vp += "Requested execution_mode=";
vp += mode_q;
vp += " target_surface=";
vp += surface_q;
vp += " aspect=";
vp += aspect_q;
vp += ". Briefs JSON:\n";
vp += briefs_q;
vp += "\nSet ready=true only if a prompt, surface, mode, quota note, and identity notes are all present and AUP-safe. Otherwise ready=false and list gaps. Do not invent missing DNA locks.";
let v = agent(vp, #{ label: "verify:handoff", capability_mode: "read-only", output_schema: verdict_schema });

let ready = false;
let reason = "verifier did not return evidence";
if v != () && v.success && v.output != () {
    if v.output.ready == true { ready = true; }
    let rsn = trimmed(v.output.reason);
    if rsn != "" { reason = rsn; }
}
log("handoff ready=" + ready.to_string() + " reason=" + reason);

phase("Report");
let dp = "You are Studio Director for Grok Imagine Cinematic Studio v3.11.3. ";
dp += aup_block();
dp += "Synthesize an imagine_agent_mode_handoff packet in markdown from these Parallel Briefs. ";
dp += "Read tools/handoff_schema.py if needed. Requested execution_mode=";
dp += mode_q;
dp += " target_surface=";
dp += surface_q;
dp += " aspect=";
dp += aspect_q;
dp += ". Verifier ready=";
dp += ready.to_string();
dp += " reason=";
dp += json_encode(reason);
dp += ". Briefs JSON:\n";
dp += briefs_q;
dp += "\nOriginal brief:\n";
dp += brief_q;
dp += "\nReturn summary, a single ready-to-paste prompt, and packet_markdown covering required handoff fields. Do not generate images.";
let d = agent(dp, #{ label: "report:director", capability_mode: "read-only", output_schema: packet_schema });

let md = "# Cinematic Studio Parallel Brief\n\n";
md += "- execution_mode: ";
md += mode;
md += "\n- target_surface: ";
md += surface;
md += "\n- aspect: ";
md += aspect;
md += "\n- nsfw: ";
md += nsfw_flag.to_string();
md += "\n- ready: ";
md += ready.to_string();
md += "\n- verify: ";
md += reason;
md += "\n\n## Brief\n\n";
md += trimmed(brief);
md += "\n\n";
for b in briefs {
    md += "## ";
    let role = "specialist";
    if b.role != () { role = trimmed(b.role); }
    md += role;
    md += "\n\n";
    if b.deliverable != () { md += trimmed(b.deliverable); md += "\n\n"; }
    if b.notes != () { md += trimmed(b.notes); md += "\n\n"; }
}
let prompt_out = "";
if d != () && d.success && d.output != () {
    if d.output.packet_markdown != () && trimmed(d.output.packet_markdown) != "" {
        md += "## Director packet\n\n";
        md += trimmed(d.output.packet_markdown);
        md += "\n";
    }
    if d.output.prompt != () { prompt_out = trimmed(d.output.prompt); }
}

let out_path = write_scratch_file("cinematic-studio-handoff.md", md);
let summary = briefs.len().to_string() + " briefs; ready=" + ready.to_string();
if d != () && d.success && d.output != () && d.output.summary != () {
    let ds = trimmed(d.output.summary);
    if ds != "" { summary = ds; }
}
complete(#{ summary: summary, ready: ready, path: out_path, prompt: prompt_out, execution_mode: mode, target_surface: surface });
