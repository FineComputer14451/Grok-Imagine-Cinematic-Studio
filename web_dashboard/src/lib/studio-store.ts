import { create } from "zustand";
import {
  CHARACTERS,
  GRADE_PRESETS,
  LENS_PRESETS,
  QUEUE,
  SEQUENCES,
  SHOTS,
  type AspectRatio,
  type CharacterDNA,
  type DensityMode,
  type ModelTier,
  type OutputMode,
  type QueueItem,
  type Sequence,
  type Shot,
} from "./studio-data";

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
  lockCharacter: (id: string) => void;
  healthLog: { title: string; ok: boolean; out: string } | null;
  runHealthAction: (action: string) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
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
  lockCharacter: (id) =>
    set((s) => ({
      characters: s.characters.map((c) =>
        c.id === id ? { ...c, locked: true, driftScore: Math.min(c.driftScore, 0.05) } : c,
      ),
    })),
  healthLog: null,
  runHealthAction: (action) => {
    const result = healthScripts[action];
    if (result) set({ healthLog: result });
  },
  sidebarOpen: false,
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
}));

/** Density section visibility — mirrors Streamlit/TUI 1·2·3 */
export function sectionVisible(mode: DensityMode, section: string): boolean {
  if (mode === "full") return true;
  if (mode === "compact") {
    return ["kpis", "attention", "status"].includes(section);
  }
  // ops
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
