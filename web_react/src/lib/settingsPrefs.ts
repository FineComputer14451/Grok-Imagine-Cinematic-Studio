/**
 * Browser-local production prefs (Streamlit session_state equivalent).
 * Does not write secrets to the server — API key is not stored.
 */

export interface SettingsPrefs {
  genre: string
  director: string
  video_model: string
  image_model: string
  chat_model: string
  duration: number
  complexity: string
  fast_mode: boolean
  quota_tier: string
  imagine_region: string
  nsfw_opt_in: boolean
  aup_age_18: boolean
  aup_imaginary_adults: boolean
  aup_not_real_person: boolean
  aup_acknowledged: boolean
  reasoning_level: string
  prompt_cache_key: string
  dashboard_view_mode: string
}

const STORAGE_KEY = 'cinematic-studio.web-react.settings.v1'

const RETIRED_IMAGE_QUALITY_SLUGS = new Set([
  'grok-imagine-image-quality',
  'grok-imagine-image-pro',
  'grok-imagine-image-quality-latest',
  'grok-imagine-image-quality-20260403',
  'imagine-image-quality',
  'image-quality',
  'quality',
  'pro',
])

/** Deprecated quality slug → Image 2.0 (matches tools/models.py live_image_model). */
export function liveImageModel(slug: string | undefined | null): string {
  const raw = (slug || '').trim()
  if (!raw) return FALLBACK_DEFAULTS.image_model
  if (RETIRED_IMAGE_QUALITY_SLUGS.has(raw)) return 'grok-imagine-image-2.0'
  return raw
}

export const FALLBACK_DEFAULTS: SettingsPrefs = {
  genre: 'Sci-Fi',
  director: 'Denis Villeneuve',
  video_model: 'grok-imagine-video',
  image_model: 'grok-imagine-image',
  chat_model: 'grok-4.5',
  duration: 60,
  complexity: 'Medium',
  fast_mode: false,
  quota_tier: 'supergrok_pro',
  imagine_region: 'us-east-1',
  nsfw_opt_in: false,
  aup_age_18: false,
  aup_imaginary_adults: false,
  aup_not_real_person: false,
  aup_acknowledged: false,
  reasoning_level: 'high',
  prompt_cache_key: '',
  dashboard_view_mode: 'ops',
}

export function loadSettingsPrefs(): SettingsPrefs {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...FALLBACK_DEFAULTS }
    const parsed = JSON.parse(raw) as Partial<SettingsPrefs>
    const merged = { ...FALLBACK_DEFAULTS, ...parsed }
    merged.image_model = liveImageModel(merged.image_model)
    return merged
  } catch {
    return { ...FALLBACK_DEFAULTS }
  }
}

export function saveSettingsPrefs(prefs: SettingsPrefs): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs))
}

/** Subscribe-friendly storage event channel for nav NSFW gate. */
export const NSFW_OPT_IN_EVENT = 'cinematic-studio:nsfw-opt-in'

/** Fired when Settings are saved so forms can remount with new defaults. */
export const PREFS_UPDATED_EVENT = 'cinematic-studio:prefs-updated'

export function setNsfwOptIn(value: boolean): void {
  const prefs = loadSettingsPrefs()
  prefs.nsfw_opt_in = value
  saveSettingsPrefs(prefs)
  window.dispatchEvent(new CustomEvent(NSFW_OPT_IN_EVENT, { detail: value }))
}

export function notifyPrefsUpdated(): void {
  window.dispatchEvent(new CustomEvent(PREFS_UPDATED_EVENT))
}

export function getNsfwOptIn(): boolean {
  return loadSettingsPrefs().nsfw_opt_in === true
}

export function fourAupFlags(prefs: Pick<
  SettingsPrefs,
  'aup_age_18' | 'aup_imaginary_adults' | 'aup_not_real_person' | 'aup_acknowledged'
>): boolean {
  return (
    prefs.aup_age_18 === true &&
    prefs.aup_imaginary_adults === true &&
    prefs.aup_not_real_person === true &&
    prefs.aup_acknowledged === true
  )
}

/** NSFW nav requires four local flags + server attestation + explicit opt-in. */
export function canEnableNsfwNav(opts: {
  fourFlags: boolean
  aupValid: boolean
  localOptIn: boolean
}): boolean {
  return opts.fourFlags === true && opts.aupValid === true && opts.localOptIn === true
}
