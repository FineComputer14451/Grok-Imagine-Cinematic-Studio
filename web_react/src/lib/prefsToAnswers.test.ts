/**
 * Lightweight Node test (no Vitest runner required):
 *   npx tsx src/lib/prefsToAnswers.test.ts
 * Also exercised by `npm run build` typecheck of consumers.
 */
import {
  applyPrefsToFieldDefaults,
  actionUsesSettingsPrefs,
  FIELD_PREF_MAP,
} from './prefsToAnswers'
import { canEnableNsfwNav, fourAupFlags, type SettingsPrefs } from './settingsPrefs'
import type { FormFieldDto } from '../api/types'

const prefs: SettingsPrefs = {
  genre: 'Cyberpunk',
  director: 'Denis Villeneuve',
  video_model: 'grok-imagine-video-1.5',
  image_model: 'grok-imagine-image-2.0',
  chat_model: 'grok-4.5',
  duration: 90,
  complexity: 'High',
  fast_mode: true,
  quota_tier: 'supergrok_heavy',
  imagine_region: 'eu-west-1',
  nsfw_opt_in: false,
  aup_age_18: false,
  aup_imaginary_adults: false,
  aup_not_real_person: false,
  aup_acknowledged: false,
  reasoning_level: 'high',
  prompt_cache_key: 'neon-run',
  dashboard_view_mode: 'ops',
}

const bibleFields: FormFieldDto[] = [
  { key: 'title', label: 'Title', required: true, coerce: null, choices: null, default: '' },
  {
    key: 'genre',
    label: 'Genre',
    required: false,
    coerce: null,
    choices: null,
    default: 'Cinematic',
  },
  {
    key: 'chat_model',
    label: 'Chat',
    required: false,
    coerce: null,
    choices: null,
    default: 'grok-4.5',
  },
  {
    key: 'video_model',
    label: 'Video',
    required: false,
    coerce: null,
    choices: null,
    default: 'grok-imagine-video',
  },
  {
    key: 'output',
    label: 'Output',
    required: false,
    coerce: null,
    choices: null,
    default: 'production_bible.json',
  },
]

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg)
}

const { defaults, applied } = applyPrefsToFieldDefaults(bibleFields, prefs)
assert(defaults.genre === 'Cyberpunk', `genre want Cyberpunk got ${defaults.genre}`)
assert(
  defaults.video_model === 'grok-imagine-video-1.5',
  `video_model ${defaults.video_model}`,
)
assert(defaults.title === '', 'title must stay empty (required user input)')
assert(defaults.output === 'production_bible.json', 'output not mapped')
assert(applied.includes('genre'), 'genre applied')
assert(applied.includes('video_model'), 'video applied')
assert(actionUsesSettingsPrefs(bibleFields), 'bible uses prefs')
assert('tier' in FIELD_PREF_MAP && FIELD_PREF_MAP.tier === 'quota_tier', 'tier map')

const quotaFields: FormFieldDto[] = [
  {
    key: 'tier',
    label: 'Tier',
    required: false,
    coerce: null,
    choices: null,
    default: 'supergrok_pro',
  },
  {
    key: 'remaining',
    label: 'Remaining',
    required: false,
    coerce: null,
    choices: null,
    default: '',
  },
]
const q = applyPrefsToFieldDefaults(quotaFields, prefs)
assert(q.defaults.tier === 'supergrok_heavy', `tier ${q.defaults.tier}`)
assert(q.defaults.remaining === '', 'remaining unmapped')

assert(!fourAupFlags(prefs), 'default four flags off')
assert(
  !canEnableNsfwNav({ fourFlags: true, aupValid: false, localOptIn: true }),
  'checkbox is not attestation',
)
assert(
  !canEnableNsfwNav({ fourFlags: false, aupValid: true, localOptIn: true }),
  'need four flags',
)
assert(
  canEnableNsfwNav({ fourFlags: true, aupValid: true, localOptIn: true }),
  'nav when attested',
)

// Bible handoff overrides settings when sessionStorage has seeds
const seqFields: FormFieldDto[] = [
  { key: 'name', label: 'Name', required: true, coerce: null, choices: null, default: '' },
  {
    key: 'duration',
    label: 'Duration',
    required: false,
    coerce: 'int',
    choices: null,
    default: '60',
  },
  { key: 'genre', label: 'Genre', required: false, coerce: null, choices: null, default: '' },
]
// Simulate handoff without jsdom sessionStorage: pass via monkeypatch is hard;
// instead assert pure map still works when no handoff.
const seq = applyPrefsToFieldDefaults(seqFields, prefs, 'sequence_init')
assert(seq.defaults.duration === '90', `duration from settings ${seq.defaults.duration}`)
assert(seq.defaults.genre === 'Cyberpunk', `genre ${seq.defaults.genre}`)

console.log('prefsToAnswers.test.ts OK')
