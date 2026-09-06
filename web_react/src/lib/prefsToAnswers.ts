/**
 * Map Settings localStorage prefs onto ActionSpec form field defaults.
 * Only keys that exist on both sides are filled — never invents argv.
 */

import type { FormFieldDto } from '../api/types'
import { handoffSeedsForAction } from './bibleHandoff'
import type { SettingsPrefs } from './settingsPrefs'
import { loadSettingsPrefs } from './settingsPrefs'

/** ActionSpec field key → SettingsPrefs key */
export const FIELD_PREF_MAP: Record<string, keyof SettingsPrefs> = {
  genre: 'genre',
  chat_model: 'chat_model',
  video_model: 'video_model',
  duration: 'duration',
  tier: 'quota_tier',
  complexity: 'complexity',
  // quota / session style
  quota_tier: 'quota_tier',
  reasoning_level: 'reasoning_level',
  prompt_cache_key: 'prompt_cache_key',
  region: 'imagine_region',
  imagine_region: 'imagine_region',
}

export type PrefsApplyResult = {
  defaults: Record<string, string>
  /** Field keys overridden by Settings prefs */
  applied: string[]
}

/**
 * Build form defaultValues:
 * ActionSpec default → Settings prefs → Bible handoff seeds (highest priority).
 * Settings duration is skipped for sequence_add_clip (clip length ≠ production total).
 * Saving Settings clears overlapping bible handoff seeds (see clearHandoffSettingsSeeds).
 */
/** ActionSpecs where Settings production duration must not seed the field. */
export const SKIP_SETTINGS_DURATION_ACTIONS = new Set(['sequence_add_clip'])

export function applyPrefsToFieldDefaults(
  fields: FormFieldDto[],
  prefs: SettingsPrefs = loadSettingsPrefs(),
  actionId?: string,
): PrefsApplyResult {
  const defaults: Record<string, string> = {}
  const applied: string[] = []
  const handoff = actionId ? handoffSeedsForAction(actionId) : {}
  const skipDuration =
    actionId != null && SKIP_SETTINGS_DURATION_ACTIONS.has(actionId)

  for (const f of fields) {
    let value = f.default ?? ''
    let source: 'default' | 'settings' | 'bible' = 'default'

    const prefKey = FIELD_PREF_MAP[f.key]
    if (prefKey != null) {
      const skipThis = skipDuration && f.key === 'duration'
      if (!skipThis) {
        const raw = prefs[prefKey]
        if (raw !== '' && raw != null && raw !== false) {
          value = String(raw)
          source = 'settings'
        }
      }
    }

    const hs = handoff[f.key]
    if (hs != null && String(hs).trim() !== '') {
      value = String(hs)
      source = 'bible'
    }

    if (source !== 'default') {
      applied.push(f.key)
    }
    defaults[f.key] = value
  }

  return { defaults, applied: [...new Set(applied)] }
}

/** True when this ActionSpec has any field that Settings can seed. */
export function actionUsesSettingsPrefs(fields: FormFieldDto[]): boolean {
  return fields.some((f) => f.key in FIELD_PREF_MAP)
}
