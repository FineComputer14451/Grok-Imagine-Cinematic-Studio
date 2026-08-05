import type { Plugin } from "@/lib/catalog";

export type SkillEntry = {
  name: string;
  description: string;
  packId: string | null;
  packLabel: string;
  pluginId: string;
  pluginName: string;
};

const PACK_ORDER = [
  "core",
  "camera-image",
  "sequence-narrative",
  "nsfw",
  "delivery-post",
] as const;

/** Exclusive skill membership from satellite packs (full suite is the union). */
export function buildSkillIndex(plugins: Plugin[]): SkillEntry[] {
  const byName = new Map<string, SkillEntry>();

  const satellites = plugins
    .filter((p) => p.packId)
    .sort(
      (a, b) =>
        PACK_ORDER.indexOf(a.packId as (typeof PACK_ORDER)[number]) -
        PACK_ORDER.indexOf(b.packId as (typeof PACK_ORDER)[number]),
    );

  for (const plugin of satellites) {
    for (const skill of plugin.skills) {
      if (byName.has(skill.name)) continue;
      byName.set(skill.name, {
        name: skill.name,
        description: skill.description,
        packId: plugin.packId,
        packLabel: plugin.displayName,
        pluginId: plugin.id,
        pluginName: plugin.name,
      });
    }
  }

  // Any skill only listed on full suite
  const full = plugins.find((p) => p.isFullSuite);
  if (full) {
    for (const skill of full.skills) {
      if (byName.has(skill.name)) continue;
      byName.set(skill.name, {
        name: skill.name,
        description: skill.description,
        packId: null,
        packLabel: "Full Suite",
        pluginId: full.id,
        pluginName: full.name,
      });
    }
  }

  return Array.from(byName.values()).sort((a, b) =>
    a.name.localeCompare(b.name),
  );
}

export function filterSkills(
  skills: SkillEntry[],
  query: string,
  packFilter: string | "all",
): SkillEntry[] {
  const q = query.trim().toLowerCase();
  return skills.filter((s) => {
    if (packFilter !== "all" && s.packId !== packFilter) return false;
    if (!q) return true;
    return (
      s.name.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      s.packLabel.toLowerCase().includes(q)
    );
  });
}

export function packSkillCounts(plugins: Plugin[]): {
  id: string;
  label: string;
  skills: number;
  commands: number;
  requires: string[];
  isFullSuite: boolean;
  recommended: boolean;
}[] {
  return plugins
    .slice()
    .sort((a, b) => {
      if (a.isFullSuite) return -1;
      if (b.isFullSuite) return 1;
      return (
        PACK_ORDER.indexOf(a.packId as (typeof PACK_ORDER)[number]) -
        PACK_ORDER.indexOf(b.packId as (typeof PACK_ORDER)[number])
      );
    })
    .map((p) => ({
      id: p.id,
      label: p.displayName,
      skills: p.skillCount,
      commands: p.commandCount,
      requires: p.requires,
      isFullSuite: p.isFullSuite,
      recommended: p.recommended,
    }));
}
