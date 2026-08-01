import { create } from "zustand";
import {
  ATTENTION,
  CHARACTERS,
  GRADE_PRESETS,
  LENS_PRESETS,
  QUEUE,
  READINESS,
  SEQUENCES,
  SHOTS,
  type AspectRatio,
  type CharacterDNA,
  type DensityMode,
  type ModelTier,
  type OutputMode,
  type QueueItem,
  type ReadinessGate,
  type Sequence,
  type Shot,
} from "./studio-data";
import {
  fetchDna,
  fetchSequences,
  fetchSnapshot,
  lockDna,
  runCliAction,
  type ApiSource,
} from "./studio-api";

export type StudioView =
  | "overview"
  | "production"
  | "dna"
  | "sequences"
  | "compose"
  | "gallery"
  | "queue"
  | "quota"
  | "tools"
  | "projects";

interface ComposeDraft {
  prompt: string;
  negative: string;
  mode: OutputMode;
  aspect: AspectRatio;
  model: ModelTier;
  duration: number;
  camera: string;
  lens: string;
  grade: string;
  projectId: string;
  takes: number;
  videoPipeline: "1.0" | "1.5";
}

interface StudioState {
  view: StudioView;
  setView: (view: StudioView) => void;
  density: DensityMode;
  setDensity: (d: DensityMode) => void;
  shots: Shot[];
  queue: QueueItem[];
  characters: CharacterDNA[];
  sequences: Sequence[];
  selectedShotId: string | null;
  setSelectedShotId: (id: string | null) => void;
  search: string;
  setSearch: (q: string) => void;
  galleryFilter: "all" | Shot["status"] | OutputMode;
  setGalleryFilter: (f: StudioState["galleryFilter"]) => void;
  draft: ComposeDraft;
  updateDraft: (partial: Partial<ComposeDraft>) => void;
  submitDraft: () => void;
  cancelQueueItem: (id: string) => void;
  promoteQueueItem: (id: string) => void;
  lockCharacter: (id: string) => Promise<void>;
  healthLog: { title: string; ok: boolean; out: string } | null;
  runHealthAction: (action: string) => Promise<void>;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  // API-backed snapshot
  apiSource: ApiSource;
  apiVersion: string | null;
  severity: "ok" | "warn" | "critical";
  attention: string[];
  readiness: ReadinessGate[];
  snapshot: Record<string, unknown> | null;
  apiLoading: boolean;
  apiError: string | null;
  lastSyncedAt: string | null;
  refreshFromApi: () => Promise<void>;
}

const defaultDraft: ComposeDraft = {
  prompt: "",
  negative: "blurry, overexposed, watermark, text overlay",
  mode: "image",
  aspect: "16:9",
  model: "cinematic",
  duration: 6,
  camera: "Arri Alexa 65",
  lens: LENS_PRESETS[2],
  grade: GRADE_PRESETS[0],
  projectId: "p-noir",
  takes: 1,
  videoPipeline: "1.5",
};

const frames = ["shot-a", "shot-b", "shot-c", "shot-d", "shot-e", "shot-f"] as const;

const healthScripts: Record<string, { title: string; ok: boolean; out: string }> = {
  doctor: {
    title: "doctor --quick",
    ok: true,
    out: "Studio doctor · OK\n· Role cards 23/23\n· Skills 52 loaded\n· Models stack compatible (grok-4.5)\n· Handoff schema valid",
  },
  validate: {
    title: "validate",
    ok: false,
    out: "validate · exit 1\n· PASS identity continuity (mean drift 0.09)\n· FAIL chain QA: seq-2 Alley confrontation (1 no-go)\n· WARN Moss Archive missing Production Bible",
  },
  "quota-sync": {
    title: "quota sync",
    ok: true,
    out: "quota sync · OK\n· Ledger aligned with session spend\n· Remaining 1840 / 2500\n· Cascade session-ledger · burn 1.15x",
  },
  models: {
    title: "models verify",
    ok: true,
    out: "models verify · OK\n· cinematic: grok-4.5\n· imagine video: 1.5 native audio\n· build: ≥ 0.2.93",
  },
};

function mapApiCharacters(
  list: Awaited<ReturnType<typeof fetchDna>>,
): CharacterDNA[] | null {
  if (!list) return null;
  return list.map((c, i) => ({
    id: c.id || c.slug || `dna-api-${i}`,
    name: c.name,
    role: c.project ? `· ${c.project}` : c.status || "DNA",
    locked: Boolean(c.locked || c.status === "locked"),
    driftScore: typeof c.drift_score === "number" ? c.drift_score : c.locked ? 0.04 : 0.2,
    traits: c.traits?.length ? c.traits : ["api profile"],
    looks: c.looks || "Loaded from snapshot API",
    projectId: "p-noir",
    updatedAt: new Date().toISOString(),
  }));
}

function mapApiSequences(
  list: Awaited<ReturnType<typeof fetchSequences>>,
): Sequence[] | null {
  if (!list) return null;
  return list.map((s, i) => {
    const qa = (s.chain_qa_status || s.health || "pending").toLowerCase();
    const chainQa: Sequence["chainQa"] =
      qa.includes("pass") || qa.includes("ok")
        ? "pass"
        : qa.includes("hold") || qa.includes("fail")
          ? "hold"
          : "pending";
    return {
      id: s.id || s.slug || `seq-api-${i}`,
      name: s.name,
      projectId: "p-noir",
      clips: s.clips ?? 0,
      durationSec: Number(s.target_duration ?? 0),
      status: chainQa === "hold" ? "qa" : "shooting",
      chainQa,
      polishPass: false,
      deliverPass: false,
      identityLock: true,
    };
  });
}

function readinessFromSnapshot(snap: Record<string, unknown> | null): ReadinessGate[] {
  if (!snap) return READINESS;
  const r = snap.readiness as Record<string, unknown> | undefined;
  if (!r) return READINESS;
  const overall = String(r.overall || "unknown").toLowerCase();
  const identity = (r.identity as { label?: string }) || {};
  const chain = (r.chain_qa as { label?: string }) || {};
  const pm = (r.plate_motion as { plate_ok?: number; motion_ok?: number; available?: boolean }) || {};
  return [
    {
      id: "overall",
      label: "Overall",
      status: overall.includes("ready") ? "ready" : overall.includes("hold") ? "hold" : "warn",
      detail: String(r.overall || "—"),
    },
    {
      id: "identity",
      label: "Identity",
      status: String(identity.label || "").toUpperCase().includes("READY") ? "ready" : "warn",
      detail: identity.label || "—",
    },
    {
      id: "chain",
      label: "Chain QA",
      status: String(chain.label || "").toUpperCase().includes("HOLD") ? "hold" : "ready",
      detail: chain.label || "—",
    },
    {
      id: "plate",
      label: "Plate / motion",
      status: pm.available === false ? "na" : "warn",
      detail: pm.available
        ? `${pm.plate_ok ?? 0}ok / ${pm.motion_ok ?? 0}mv`
        : "n/a",
    },
  ];
}

export const useStudioStore = create<StudioState>((set, get) => ({
  view: "overview",
  setView: (view) => set({ view }),
  density: "ops",
  setDensity: (density) => set({ density }),
  shots: SHOTS,
  queue: QUEUE,
  characters: CHARACTERS,
  sequences: SEQUENCES,
  selectedShotId: SHOTS[0]?.id ?? null,
  setSelectedShotId: (id) => set({ selectedShotId: id }),
  search: "",
  setSearch: (search) => set({ search }),
  galleryFilter: "all",
  setGalleryFilter: (galleryFilter) => set({ galleryFilter }),
  draft: defaultDraft,
  updateDraft: (partial) =>
    set((s) => ({ draft: { ...s.draft, ...partial } })),
  submitDraft: () => {
    const { draft, shots, queue } = get();
    if (!draft.prompt.trim()) return;
    const id = `s-${Date.now().toString(36)}`;
    const frame = frames[shots.length % frames.length];
    const shot: Shot = {
      id,
      title:
        draft.prompt.slice(0, 42).trim() +
        (draft.prompt.length > 42 ? "…" : ""),
      prompt: draft.prompt.trim(),
      projectId: draft.projectId,
      status: "queued",
      mode: draft.mode,
      aspect: draft.aspect,
      model: draft.model,
      duration: draft.mode === "video" ? draft.duration : undefined,
      take: draft.takes,
      frame,
      createdAt: new Date().toISOString(),
      seed: Math.floor(Math.random() * 900000) + 100000,
      camera: draft.camera,
      lens: draft.lens,
      grade: draft.grade,
    };
    const item: QueueItem = {
      id: `q-${Date.now().toString(36)}`,
      shotId: id,
      title: shot.title,
      progress: 0,
      etaSeconds: draft.mode === "video" ? 200 : 45,
      stage: "Queued",
      priority: "normal",
    };
    set({
      shots: [shot, ...shots],
      queue: [...queue, item],
      selectedShotId: id,
      view: "queue",
      draft: { ...defaultDraft, prompt: "", projectId: draft.projectId },
    });
  },
  cancelQueueItem: (id) =>
    set((s) => {
      const item = s.queue.find((q) => q.id === id);
      return {
        queue: s.queue.filter((q) => q.id !== id),
        shots: item
          ? s.shots.map((sh) =>
              sh.id === item.shotId ? { ...sh, status: "draft" as const } : sh,
            )
          : s.shots,
      };
    }),
  promoteQueueItem: (id) =>
    set((s) => {
      const item = s.queue.find((q) => q.id === id);
      if (!item) return s;
      const rest = s.queue.filter((q) => q.id !== id);
      return {
        queue: [{ ...item, priority: "rush" as const }, ...rest],
      };
    }),
  lockCharacter: async (id) => {
    const char = get().characters.find((c) => c.id === id);
    // optimistic
    set((s) => ({
      characters: s.characters.map((c) =>
        c.id === id
          ? { ...c, locked: true, driftScore: Math.min(c.driftScore, 0.05) }
          : c,
      ),
    }));
    if (char) {
      const res = await lockDna(char.name);
      if (!res) return;
      // refresh DNA list from API when available
      const list = mapApiCharacters(await fetchDna());
      if (list) set({ characters: list });
    }
  },
  healthLog: null,
  runHealthAction: async (action) => {
    const remote = await runCliAction(action);
    if (remote) {
      set({
        healthLog: {
          title: remote.action,
          ok: remote.ok,
          out: remote.output,
        },
      });
      return;
    }
    const result = healthScripts[action];
    if (result) set({ healthLog: result });
  },
  sidebarOpen: false,
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  apiSource: "offline",
  apiVersion: null,
  severity: "warn",
  attention: ATTENTION.map((a) => a.message),
  readiness: READINESS,
  snapshot: null,
  apiLoading: false,
  apiError: null,
  lastSyncedAt: null,
  refreshFromApi: async () => {
    set({ apiLoading: true, apiError: null });
    const snap = await fetchSnapshot();
    if (!snap) {
      set({
        apiLoading: false,
        apiSource: "offline",
        apiError: "Snapshot API unreachable — using local demo data",
      });
      return;
    }

    const characters =
      mapApiCharacters(await fetchDna()) ?? get().characters;
    const sequences =
      mapApiSequences(await fetchSequences()) ?? get().sequences;

    set({
      apiLoading: false,
      apiSource: snap.source === "live" ? "live" : "mock",
      apiVersion: snap.studio_version,
      severity: snap.severity,
      attention: snap.attention?.length
        ? snap.attention
        : ATTENTION.map((a) => a.message),
      readiness: readinessFromSnapshot(snap.snapshot),
      snapshot: snap.snapshot,
      characters,
      sequences,
      lastSyncedAt: new Date().toISOString(),
      apiError: null,
    });
  },
}));

/** Density section visibility — mirrors Streamlit/TUI 1·2·3 */
export function sectionVisible(mode: DensityMode, section: string): boolean {
  if (mode === "full") return true;
  if (mode === "compact") {
    // Streamlit compact: health_actions + readiness (+ always strip/kpis/attention)
    return [
      "kpis",
      "attention",
      "status",
      "health_actions",
      "readiness",
    ].includes(section);
  }
  return [
    "kpis",
    "attention",
    "status",
    "health_actions",
    "readiness",
    "convergence",
    "studio_quota",
    "sequences",
  ].includes(section);
}
