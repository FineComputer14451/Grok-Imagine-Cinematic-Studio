/**
 * Post-generate handoff from Guided Bible → DNA / Sequence / Quota ActionSpecs.
 * Browser session only; seeds form defaults (never free-form argv).
 */

import { liveChatModel, loadSettingsPrefs } from './settingsPrefs'

const STORAGE_KEY = 'cinematic-studio.web-react.bible-handoff.v1'
export const BIBLE_HANDOFF_EVENT = 'cinematic-studio:bible-handoff'

export type BibleHandoff = {
  generated_at: string
  title: string
  genre: string
  duration: number
  complexity: string
  video_model: string
  chat_model: string
  director_signature: string
  written_path: string | null
  /** ActionSpec id → field seeds */
  seeds: Record<string, Record<string, string>>
  next_steps: { label: string; to: string; action?: string; blurb: string }[]
}

function str(v: unknown, fallback = ''): string {
  if (v == null) return fallback
  return String(v).trim() || fallback
}

function leadNameFromAnswers(answers: Record<string, unknown>, title: string): string {
  const raw = str(answers.characters_text)
  if (raw) {
    // "Mara: exhausted detective" → Mara
    const first = raw.split(/[\n,;]/)[0]?.trim() ?? ''
    const beforeColon = first.split(':')[0]?.trim()
    if (beforeColon && beforeColon.length < 48) return beforeColon
  }
  const short = title.split(/\s+/).slice(0, 3).join(' ')
  return short ? `Lead — ${short}` : 'Lead Character'
}

export function buildBibleHandoff(input: {
  bible: Record<string, unknown>
  kwargs?: Record<string, unknown> | null
  answers: Record<string, unknown>
  written_path?: string | null
}): BibleHandoff {
  const { bible, kwargs, answers, written_path } = input
  const title = str(kwargs?.title ?? bible.project_title, 'Untitled')
  const genre = str(kwargs?.genre ?? bible.genre, 'Cinematic')
  const duration = Number(kwargs?.target_duration_seconds ?? bible.target_duration_seconds ?? 60) || 60
  const complexity = str(kwargs?.complexity ?? bible.complexity, 'Medium')
  const video_model = str(kwargs?.video_model ?? 'grok-imagine-video', 'grok-imagine-video')
  const chat_model = liveChatModel(str(kwargs?.chat_model ?? 'grok-4.6', 'grok-4.6'))
  const director_signature = str(
    kwargs?.director_signature ?? bible.director_signature,
    '',
  )
  const prefs = loadSettingsPrefs()
  const lead = leadNameFromAnswers(answers, title)
  const actName = 'Act 1'
  const path = written_path || 'production_bible.json'

  const seeds: Record<string, Record<string, string>> = {
    dna_init: {
      name: lead,
      core: str(answers.logline) || `Lead for ${title}`,
      emotion: complexity,
    },
    dna_lock: { name: lead },
    dna_show: { name: lead },
    dna_handoff: { name: lead },
    sequence_init: {
      name: actName,
      duration: String(duration),
      genre,
    },
    sequence_show: { name: actName },
    sequence_handoff: { name: actName },
    sequence_add_clip: {
      name: actName,
      prompt: str(answers.logline) || `${title} opening beat`,
      duration: '10',
    },
    quota_budget: {
      tier: prefs.quota_tier || 'supergrok_pro',
    },
    quota_sequence_estimate: { name: actName },
    bible_create: {
      title,
      genre,
      chat_model,
      video_model,
      output: path,
    },
  }

  return {
    generated_at: new Date().toISOString(),
    title,
    genre,
    duration,
    complexity,
    video_model,
    chat_model,
    director_signature,
    written_path: written_path ?? null,
    seeds,
    next_steps: [
      {
        label: 'Init Character DNA',
        to: '/dna',
        action: 'dna_init',
        blurb: `Scaffold “${lead}” from bible title / characters`,
      },
      {
        label: 'Init Sequence',
        to: '/sequences',
        action: 'sequence_init',
        blurb: `${actName} · ${duration}s · ${genre}`,
      },
      {
        label: 'Quota budget',
        to: '/quota',
        action: 'quota_budget',
        blurb: `Tier ${prefs.quota_tier || 'supergrok_pro'}`,
      },
      {
        label: 'Sequence cost estimate',
        to: '/sequences',
        action: 'quota_sequence_estimate',
        blurb: `Estimate spend for ${actName}`,
      },
      {
        label: 'Studio validate',
        to: '/production',
        action: undefined,
        blurb: 'Run validate / stack health from Production',
      },
    ],
  }
}

export function saveBibleHandoff(handoff: BibleHandoff): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(handoff))
  window.dispatchEvent(new CustomEvent(BIBLE_HANDOFF_EVENT, { detail: handoff }))
}

export function loadBibleHandoff(): BibleHandoff | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as BibleHandoff
  } catch {
    return null
  }
}

export function clearBibleHandoff(): void {
  sessionStorage.removeItem(STORAGE_KEY)
  window.dispatchEvent(new CustomEvent(BIBLE_HANDOFF_EVENT, { detail: null }))
}

/** Field seeds for an ActionSpec from the latest bible handoff (if any). */
export function handoffSeedsForAction(actionId: string): Record<string, string> {
  const h = loadBibleHandoff()
  return h?.seeds[actionId] ?? {}
}
