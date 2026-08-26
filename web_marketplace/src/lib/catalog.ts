import catalogJson from "@/data/catalog.json";

export type Skill = {
  name: string;
  description: string;
};

export type Command = {
  name: string;
  description: string;
};

export type Plugin = {
  id: string;
  name: string;
  displayName: string;
  version: string;
  description: string;
  longDescription: string;
  category: string;
  packId: string | null;
  requires: string[];
  recommended: boolean;
  consentRequired: boolean;
  isFullSuite: boolean;
  tags: string[];
  icon: string;
  installCommand: string;
  updateCommand?: string;
  homepage: string;
  repository: string;
  author: { name: string; url: string };
  license: string;
  skillCount: number;
  commandCount: number;
  skills: Skill[];
  commands: Command[];
};

export type MarketplaceMeta = {
  name: string;
  title: string;
  description: string;
  version: string;
  owner: { name: string; url: string };
  homepage: string;
  requiresGrokBuild: string;
  pinSha: string;
};

export type FilterId =
  | "all"
  | "recommended"
  | "installed"
  | "core"
  | "camera-image"
  | "sequence-narrative"
  | "delivery-post"
  | "nsfw";

export const REPO_INSTALL_CMD =
  "grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust";

export const FULL_SUITE_UPDATE_CMD =
  "grok plugin update grok-imagine-cinematic-studio";

function normalizePlugin(
  raw: Partial<Plugin> & { id?: string; name?: string },
): Plugin | null {
  const id = raw.id || raw.name;
  const name = raw.name || raw.id;
  if (!id || !name) return null;

  const skills = Array.isArray(raw.skills)
    ? raw.skills
        .filter((s) => s && typeof s.name === "string")
        .map((s) => ({
          name: s.name,
          description: typeof s.description === "string" ? s.description : "",
        }))
    : [];
  const commands = Array.isArray(raw.commands)
    ? raw.commands
        .filter((c) => c && typeof c.name === "string")
        .map((c) => ({
          name: c.name,
          description:
            typeof c.description === "string" ? c.description : "",
        }))
    : [];

  return {
    id,
    name,
    displayName: raw.displayName ?? name,
    version: raw.version ?? "0.0.0",
    description: raw.description ?? "",
    longDescription: raw.longDescription ?? raw.description ?? "",
    category: raw.category ?? "creative",
    packId: raw.packId ?? null,
    requires: Array.isArray(raw.requires) ? raw.requires : [],
    recommended: Boolean(raw.recommended),
    consentRequired: Boolean(raw.consentRequired),
    isFullSuite: Boolean(raw.isFullSuite),
    tags: Array.isArray(raw.tags) ? raw.tags : [],
    icon: raw.icon ?? "package",
    installCommand: raw.installCommand || REPO_INSTALL_CMD,
    updateCommand:
      raw.updateCommand ||
      (raw.isFullSuite
        ? FULL_SUITE_UPDATE_CMD
        : `grok plugin update ${name}`),
    homepage:
      raw.homepage ||
      "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
    repository:
      raw.repository ||
      "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git",
    author: raw.author ?? {
      name: "FineComputer14451",
      url: "https://github.com/FineComputer14451",
    },
    license: raw.license ?? "MIT",
    skillCount: raw.skillCount ?? skills.length,
    commandCount: raw.commandCount ?? commands.length,
    skills,
    commands,
  };
}

const rawMarketplace = (catalogJson as { marketplace?: Partial<MarketplaceMeta> })
  .marketplace;

export const marketplace: MarketplaceMeta = {
  name: rawMarketplace?.name ?? "finecomputer14451-cinematic-studio",
  title: rawMarketplace?.title ?? "Grok Imagine Cinematic Studio",
  description: rawMarketplace?.description ?? "",
  version: rawMarketplace?.version ?? "3.11.0",
  owner: rawMarketplace?.owner ?? {
    name: "FineComputer14451",
    url: "https://github.com/FineComputer14451",
  },
  homepage:
    rawMarketplace?.homepage ??
    "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
  requiresGrokBuild: rawMarketplace?.requiresGrokBuild ?? "≥ 1.0.5",
  pinSha: rawMarketplace?.pinSha ?? "",
};

export const plugins: Plugin[] = (
  Array.isArray((catalogJson as { plugins?: unknown[] }).plugins)
    ? ((catalogJson as { plugins: Array<Partial<Plugin>> }).plugins)
    : []
)
  .map((p) => normalizePlugin(p))
  .filter((p): p is Plugin => Boolean(p));

export const filters = (
  Array.isArray((catalogJson as { filters?: unknown }).filters)
    ? (catalogJson as { filters: { id: FilterId; label: string }[] }).filters
    : [{ id: "all" as const, label: "All" }]
);

export function getPlugin(id: string): Plugin | undefined {
  return plugins.find((p) => p.id === id || p.packId === id);
}

export function getPluginByPackId(packId: string): Plugin | undefined {
  return plugins.find((p) => p.packId === packId);
}

export function resolveInstallOrder(pluginId: string): string[] {
  const plugin = getPlugin(pluginId);
  if (!plugin) return [];
  if (plugin.isFullSuite) return [plugin.id];

  const order: string[] = [];
  for (const req of plugin.requires) {
    const dep = getPluginByPackId(req);
    if (dep) order.push(dep.id);
  }
  order.push(plugin.id);
  return order;
}

export function totalSkills(): number {
  const full = plugins.find((p) => p.isFullSuite);
  return full?.skillCount ?? 0;
}

export function totalCommands(): number {
  const full = plugins.find((p) => p.isFullSuite);
  return full?.commandCount ?? 0;
}

/** Prefer update command when installed; otherwise install command. */
export function primaryCliCommand(plugin: Plugin, installed: boolean): string {
  if (installed && plugin.updateCommand) return plugin.updateCommand;
  return plugin.installCommand || REPO_INSTALL_CMD;
}
