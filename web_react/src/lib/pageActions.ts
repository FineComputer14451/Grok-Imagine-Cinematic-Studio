/**
 * ActionSpec IDs per route.
 * NiceGUI six-route cockpit + Streamlit phase-2 Tools/Settings/NSFW gate.
 * No free-form argv.
 */

export interface PageConfig {
  title: string
  blurb: string
  /** One-shot buttons (no form) — e.g. status, dna_list */
  quickActions: string[]
  /** Form-backed ActionSpecs */
  formActions: string[]
  /** Primary list refresh action (shown in result panel on load) */
  listAction?: string
}

export const PAGE_CONFIG: Record<string, PageConfig> = {
  production: {
    title: 'Production',
    blurb:
      'Production bible + studio health via ActionSpec / execute. Full multi-stage wizard stays on Streamlit.',
    quickActions: [
      'status',
      'validate',
      'stack',
      'doctor_quick',
      'models_verify',
      'models_list',
    ],
    formActions: ['bible_create', 'handoff_validate'],
    listAction: 'status',
  },
  dna: {
    title: 'Character DNA',
    blurb: 'Identity profiles via studio_core execute. Same ActionSpec catalog as the Textual cockpit.',
    quickActions: ['dna_list'],
    formActions: ['dna_init', 'dna_lock', 'dna_show', 'dna_handoff'],
    listAction: 'dna_list',
  },
  sequences: {
    title: 'Sequences',
    blurb: 'Long-form chain planning via ActionSpec. Mutating actions keep confirm gates.',
    quickActions: ['sequence_list'],
    formActions: [
      'sequence_init',
      'sequence_add_clip',
      'sequence_show',
      'sequence_handoff',
      'quota_sequence_estimate',
    ],
    listAction: 'sequence_list',
  },
  imagine: {
    title: 'Imagine',
    blurb:
      'Job queue + agent-handoff bridge. Live xAI batch spend stays on Streamlit when an API key is set.',
    quickActions: ['imagine_list'],
    formActions: ['imagine_bridge', 'sequence_handoff', 'dna_handoff'],
    listAction: 'imagine_list',
  },
  quota: {
    title: 'Quota',
    blurb: 'Session spend, budget, and sequence estimates via execute_action.',
    quickActions: ['quota_dashboard', 'quota_sync'],
    formActions: ['quota_budget', 'quota_sequence_estimate'],
    listAction: 'quota_dashboard',
  },
}

/** Always-on Streamlit-parity pages (NSFW is opt-in via Settings). */
export const NAV_ITEMS: { to: string; label: string }[] = [
  { to: '/', label: 'Dashboard' },
  { to: '/production', label: 'Production' },
  { to: '/dna', label: 'DNA' },
  { to: '/sequences', label: 'Sequences' },
  { to: '/imagine', label: 'Imagine' },
  { to: '/quota', label: 'Quota' },
  { to: '/bible', label: 'Bible' },
  { to: '/tools', label: 'Tools' },
  { to: '/settings', label: 'Settings' },
]
