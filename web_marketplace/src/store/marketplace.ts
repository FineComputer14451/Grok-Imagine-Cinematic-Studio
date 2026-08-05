import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import {
  getPlugin,
  getPluginByPackId,
  resolveInstallOrder,
  type FilterId,
  type Plugin,
} from "@/lib/catalog";

export type InstallRecord = {
  pluginId: string;
  installedAt: string;
  version: string;
};

export type CatalogView = "packs" | "skills" | "graph";

type MarketplaceState = {
  installed: Record<string, InstallRecord>;
  nsfwConsent: boolean;
  search: string;
  filter: FilterId;
  view: CatalogView;
  activePluginId: string | null;
  setSearch: (q: string) => void;
  setFilter: (f: FilterId) => void;
  setView: (v: CatalogView) => void;
  setActivePluginId: (id: string | null) => void;
  grantNsfwConsent: () => void;
  revokeNsfwConsent: () => void;
  isInstalled: (pluginId: string) => boolean;
  install: (
    pluginId: string,
  ) => { ok: boolean; message: string; installed: string[] };
  uninstall: (pluginId: string) => { ok: boolean; message: string };
  installFullSuite: () => { ok: boolean; message: string };
  clearAll: () => void;
  installedCount: () => number;
  matchesFilter: (plugin: Plugin) => boolean;
};

const memoryStorage = (): Storage => {
  const map = new Map<string, string>();
  return {
    get length() {
      return map.size;
    },
    clear() {
      map.clear();
    },
    getItem(key) {
      return map.has(key) ? map.get(key)! : null;
    },
    key(index) {
      return Array.from(map.keys())[index] ?? null;
    },
    removeItem(key) {
      map.delete(key);
    },
    setItem(key, value) {
      map.set(key, value);
    },
  };
};

const safeStorage = createJSONStorage(() =>
  typeof window !== "undefined" ? window.localStorage : memoryStorage(),
);

export const useMarketplace = create<MarketplaceState>()(
  persist(
    (set, get) => ({
      installed: {},
      nsfwConsent: false,
      search: "",
      filter: "all",
      view: "packs",
      activePluginId: null,

      setSearch: (q) => set({ search: q }),
      setFilter: (f) => set({ filter: f }),
      setView: (v) => set({ view: v }),
      setActivePluginId: (id) => set({ activePluginId: id }),

      grantNsfwConsent: () => set({ nsfwConsent: true }),
      revokeNsfwConsent: () => set({ nsfwConsent: false }),

      isInstalled: (pluginId) => Boolean(get().installed[pluginId]),

      installedCount: () => Object.keys(get().installed).length,

      install: (pluginId) => {
        const plugin = getPlugin(pluginId);
        if (!plugin)
          return { ok: false, message: "Plugin not found", installed: [] };

        if (plugin.consentRequired && !get().nsfwConsent) {
          return {
            ok: false,
            message: "Consent required for NSFW pack before install",
            installed: [],
          };
        }

        const order = resolveInstallOrder(pluginId);
        const next = { ...get().installed };
        const newly: string[] = [];
        const now = new Date().toISOString();

        if (plugin.isFullSuite) {
          for (const key of Object.keys(next)) {
            const p = getPlugin(key);
            if (p && !p.isFullSuite) delete next[key];
          }
        }

        for (const id of order) {
          const p = getPlugin(id);
          if (!p) continue;
          if (!next[id]) {
            next[id] = { pluginId: id, installedAt: now, version: p.version };
            newly.push(id);
          }
        }

        set({ installed: next });
        const msg =
          newly.length === 0
            ? `${plugin.displayName} is already installed`
            : newly.length === 1
              ? `Installed ${plugin.displayName}`
              : `Installed ${newly.length} packs (deps resolved)`;
        return { ok: true, message: msg, installed: newly };
      },

      uninstall: (pluginId) => {
        const plugin = getPlugin(pluginId);
        if (!plugin) return { ok: false, message: "Plugin not found" };

        const next = { ...get().installed };
        if (!next[pluginId]) return { ok: false, message: "Not installed" };

        if (plugin.packId === "core") {
          const dependents = Object.keys(next)
            .map((id) => getPlugin(id))
            .filter(
              (p): p is Plugin =>
                Boolean(p) &&
                p!.id !== pluginId &&
                !p!.isFullSuite &&
                p!.requires.includes("core"),
            );
          if (dependents.length > 0) {
            return {
              ok: false,
              message: `Remove dependent packs first: ${dependents.map((d) => d.displayName).join(", ")}`,
            };
          }
        }

        delete next[pluginId];
        set({ installed: next });
        return { ok: true, message: `Removed ${plugin.displayName}` };
      },

      installFullSuite: () => get().install("grok-imagine-cinematic-studio"),

      clearAll: () => set({ installed: {} }),

      matchesFilter: (plugin) => {
        const { filter, search, installed } = get();
        const q = search.trim().toLowerCase();
        if (q) {
          const hay = [
            plugin.displayName,
            plugin.name,
            plugin.description,
            plugin.longDescription,
            ...plugin.tags,
            ...plugin.skills.map((s) => `${s.name} ${s.description}`),
            ...plugin.commands.map((c) => c.name),
          ]
            .join(" ")
            .toLowerCase();
          if (!hay.includes(q)) return false;
        }

        switch (filter) {
          case "all":
            return true;
          case "recommended":
            return plugin.recommended;
          case "installed":
            return Boolean(installed[plugin.id]);
          case "core":
            return plugin.packId === "core" || plugin.isFullSuite;
          case "camera-image":
            return plugin.packId === "camera-image";
          case "sequence-narrative":
            return plugin.packId === "sequence-narrative";
          case "delivery-post":
            return plugin.packId === "delivery-post";
          case "nsfw":
            return plugin.packId === "nsfw";
          default:
            return true;
        }
      },
    }),
    {
      name: "cinematic-studio-marketplace",
      storage: safeStorage,
      partialize: (s) => ({
        installed: s.installed,
        nsfwConsent: s.nsfwConsent,
      }),
    },
  ),
);

export function dependencyLabel(plugin: Plugin): string | null {
  if (!plugin.requires?.length) return null;
  return plugin.requires
    .map((r) => getPluginByPackId(r)?.displayName ?? r)
    .join(", ");
}
