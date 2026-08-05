import type { MarketplaceMeta, Plugin } from "@/lib/catalog";
import {
  FULL_SUITE_UPDATE_CMD,
  REPO_INSTALL_CMD,
  marketplace as staticMarketplace,
  plugins as staticPlugins,
} from "@/lib/catalog";

const MARKETPLACE_URL =
  "https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/.grok-plugin/marketplace.json";
const PLUGIN_URL =
  "https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/.grok-plugin/plugin.json";

export type RemoteMarketplace = {
  name?: string;
  description?: string;
  owner?: { name?: string; url?: string };
  homepage?: string;
  install_command?: string;
  update_command?: string;
  skill_count?: number;
  command_count?: number;
  agent_count?: number;
  plugins?: Array<{
    name: string;
    description?: string;
    version?: string;
    recommended?: boolean;
    pack_id?: string | null;
    requires?: string[];
    source?: { sha?: string; url?: string };
    homepage?: string;
    skill_count?: number;
    command_count?: number;
    install_command?: string;
    update_command?: string;
  }>;
};

export type RemotePluginJson = {
  version?: string;
  description?: string;
  skills?: string[];
  commands?: string[];
};

export type SyncResult = {
  marketplace: MarketplaceMeta;
  plugins: Plugin[];
  pinSha: string;
  version: string;
  fetchedAt: string;
};

function packRequiresConsent(name: string): boolean {
  return name.includes("nsfw");
}

function isFullSuite(name: string): boolean {
  return name === "grok-imagine-cinematic-studio";
}

function scrubVersion(text: string | undefined, version: string): string {
  if (!text) return "";
  return text
    .replace(/v3\.9\.0/g, `v${version}`)
    .replace(/\b62 skills\b/g, "64 skills")
    .replace(/\b54-skill\b/g, "64-skill");
}

export async function fetchRemoteCatalog(): Promise<{
  marketplace: RemoteMarketplace;
  plugin: RemotePluginJson;
}> {
  const [mpRes, pjRes] = await Promise.all([
    fetch(MARKETPLACE_URL, { headers: { Accept: "application/json" } }),
    fetch(PLUGIN_URL, { headers: { Accept: "application/json" } }),
  ]);
  if (!mpRes.ok) {
    throw new Error(`marketplace.json HTTP ${mpRes.status}`);
  }
  if (!pjRes.ok) {
    throw new Error(`plugin.json HTTP ${pjRes.status}`);
  }
  const marketplace = (await mpRes.json()) as RemoteMarketplace;
  const plugin = (await pjRes.json()) as RemotePluginJson;
  return { marketplace, plugin };
}

/** Merge remote marketplace metadata into the local rich catalog (skills stay local). */
export function mergeRemoteCatalog(
  remote: RemoteMarketplace,
  pluginJson: RemotePluginJson,
  basePlugins: Plugin[] = staticPlugins,
  baseMeta: MarketplaceMeta = staticMarketplace,
): SyncResult {
  const remotePlugins = remote.plugins ?? [];
  const byName = new Map(remotePlugins.map((p) => [p.name, p]));
  const pinSha =
    remotePlugins.find((p) => p.source?.sha)?.source?.sha ||
    baseMeta.pinSha ||
    "";
  const version =
    pluginJson.version ||
    remotePlugins.find((p) => isFullSuite(p.name))?.version ||
    baseMeta.version;

  const remoteSkillTotal =
    remote.skill_count ??
    (Array.isArray(pluginJson.skills) ? pluginJson.skills.length : undefined);
  const remoteCommandTotal =
    remote.command_count ??
    (Array.isArray(pluginJson.commands)
      ? pluginJson.commands.length
      : undefined);

  const installCmd = remote.install_command || REPO_INSTALL_CMD;
  const fullUpdateCmd = remote.update_command || FULL_SUITE_UPDATE_CMD;

  const plugins: Plugin[] = basePlugins.map((local) => {
    const remotePlugin = byName.get(local.name) || byName.get(local.id);
    if (!remotePlugin) {
      return {
        ...local,
        version: version || local.version,
        skillCount:
          local.isFullSuite && remoteSkillTotal
            ? remoteSkillTotal
            : local.skillCount,
        commandCount:
          local.isFullSuite && remoteCommandTotal
            ? remoteCommandTotal
            : local.commandCount,
        description: scrubVersion(local.description, version),
        longDescription: scrubVersion(local.longDescription, version),
        updateCommand:
          local.updateCommand ||
          (local.isFullSuite
            ? fullUpdateCmd
            : `grok plugin update ${local.name}`),
        installCommand: local.installCommand || installCmd,
      };
    }

    const desc = scrubVersion(
      remotePlugin.description ?? local.description,
      version,
    );
    const skillCount =
      typeof remotePlugin.skill_count === "number"
        ? remotePlugin.skill_count
        : local.isFullSuite && remoteSkillTotal
          ? remoteSkillTotal
          : local.skillCount;
    const commandCount =
      typeof remotePlugin.command_count === "number"
        ? remotePlugin.command_count
        : local.isFullSuite && remoteCommandTotal
          ? remoteCommandTotal
          : local.commandCount;

    return {
      ...local,
      version: remotePlugin.version || version || local.version,
      description: desc,
      longDescription: desc || local.longDescription,
      recommended: remotePlugin.recommended ?? local.recommended,
      requires: Array.isArray(remotePlugin.requires)
        ? remotePlugin.requires
        : local.requires,
      consentRequired:
        packRequiresConsent(remotePlugin.name) || local.consentRequired,
      isFullSuite: isFullSuite(remotePlugin.name) || local.isFullSuite,
      homepage: remotePlugin.homepage || local.homepage,
      skillCount,
      commandCount,
      installCommand: remotePlugin.install_command || installCmd,
      updateCommand: isFullSuite(remotePlugin.name)
        ? fullUpdateCmd
        : remotePlugin.update_command ||
          `grok plugin update ${remotePlugin.name}`,
    };
  });

  for (const rp of remotePlugins) {
    if (plugins.some((p) => p.name === rp.name || p.id === rp.name)) continue;
    plugins.push({
      id: rp.name,
      name: rp.name,
      displayName: rp.name
        .replace(/^grok-imagine-/, "")
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase()),
      version: rp.version || version,
      description: scrubVersion(rp.description, version),
      longDescription: scrubVersion(rp.description, version),
      category: "creative",
      packId: rp.pack_id ?? null,
      requires: rp.requires ?? [],
      recommended: Boolean(rp.recommended),
      consentRequired: packRequiresConsent(rp.name),
      isFullSuite: isFullSuite(rp.name),
      tags: ["remote"],
      icon: "package",
      installCommand: rp.install_command || installCmd,
      updateCommand: isFullSuite(rp.name)
        ? fullUpdateCmd
        : `grok plugin update ${rp.name}`,
      homepage:
        rp.homepage ||
        "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
      repository:
        "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git",
      author: {
        name: "FineComputer14451",
        url: "https://github.com/FineComputer14451",
      },
      license: "MIT",
      skillCount: rp.skill_count ?? 0,
      commandCount: rp.command_count ?? 0,
      skills: [],
      commands: [],
    });
  }

  const marketplace: MarketplaceMeta = {
    ...baseMeta,
    name: remote.name || baseMeta.name,
    description:
      scrubVersion(remote.description, version) || baseMeta.description,
    version,
    homepage: remote.homepage || baseMeta.homepage,
    owner: {
      name: remote.owner?.name || baseMeta.owner.name,
      url: remote.owner?.url || baseMeta.owner.url,
    },
    pinSha,
  };

  return {
    marketplace,
    plugins,
    pinSha,
    version,
    fetchedAt: new Date().toISOString(),
  };
}
