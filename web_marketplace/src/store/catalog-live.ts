import { create } from "zustand";
import {
  marketplace as staticMarketplace,
  plugins as staticPlugins,
  type MarketplaceMeta,
  type Plugin,
} from "@/lib/catalog";

type CatalogLiveState = {
  marketplace: MarketplaceMeta;
  plugins: Plugin[];
  lastSyncedAt: string | null;
  syncing: boolean;
  error: string | null;
  source: "bundled" | "github";
  syncFromGitHub: () => Promise<{ ok: boolean; message: string }>;
  getPlugin: (id: string) => Plugin | undefined;
};

export const useCatalogLive = create<CatalogLiveState>((set, get) => ({
  marketplace: staticMarketplace,
  plugins: staticPlugins,
  lastSyncedAt: null,
  syncing: false,
  error: null,
  source: "bundled",

  getPlugin: (id) => {
    const list = get().plugins;
    return list.find((p) => p.id === id || p.packId === id || p.name === id);
  },

  syncFromGitHub: async () => {
    set({ syncing: true, error: null });
    try {
      const res = await fetch("/api/catalog", {
        headers: { Accept: "application/json" },
      });
      const data = (await res.json()) as {
        ok: boolean;
        error?: string;
        marketplace?: MarketplaceMeta;
        plugins?: Plugin[];
        fetchedAt?: string;
      };
      if (!res.ok || !data.ok || !data.marketplace || !data.plugins) {
        const msg = data.error || `Sync failed (${res.status})`;
        set({ syncing: false, error: msg });
        return { ok: false, message: msg };
      }
      set({
        marketplace: data.marketplace,
        plugins: data.plugins,
        lastSyncedAt: data.fetchedAt || new Date().toISOString(),
        syncing: false,
        error: null,
        source: "github",
      });
      return {
        ok: true,
        message: `Synced v${data.marketplace.version} from GitHub`,
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Network error";
      set({ syncing: false, error: msg });
      return { ok: false, message: msg };
    }
  },
}));
