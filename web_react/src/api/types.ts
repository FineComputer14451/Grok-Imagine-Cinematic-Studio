/** Types aligned with studio_api (PR9) + studio_core contracts. */

export type DashboardMode = 'compact' | 'ops' | 'full'

export interface FormFieldDto {
  key: string
  label: string
  required: boolean
  coerce: string | null
  choices: string[] | null
  default: string
  help?: string
}

export interface ActionSpecDto {
  id: string
  label: string
  group: string
  description: string
  needs_confirm: boolean
  has_form?: boolean
  surfaces: string[]
  base_argv: string[]
  fields: FormFieldDto[]
}

export interface ActionsListResponse {
  count: number
  actions: ActionSpecDto[]
}

export interface ExecuteBody {
  answers?: Record<string, string>
  mode?: 'inprocess' | 'subprocess'
  timeout?: number
}

export interface ActionResultDto {
  ok: boolean
  action_id: string
  argv: string[]
  returncode: number
  stdout: string
  stderr: string
  errors: string[]
  timed_out: boolean
  mode: string
  output?: unknown
}

export interface HealthResponse {
  ok: boolean
  studio_version: string
  actions: number
  xai_api_key_set?: boolean
}

export interface EnvStatus {
  xai_api_key_set: boolean
  xai_api_key_source: string | null
  note: string
}

export interface ProductionOptions {
  genres: string[]
  directors: string[]
  complexities: string[]
  tiers: string[]
  reasoning_levels: string[]
  chat_models: string[]
  video_models: string[]
  image_models?: string[]
  imagine_surfaces?: string[]
  imagine_execution_modes?: string[]
  imagine_regions: string[]
  defaults: Record<string, string | number | boolean>
}

export interface AgentsRoster {
  core_count: number
  total_count: number
  groups: Record<string, string[]>
}

export interface RoleCardListItem {
  stem: string
  filename: string
  relpath: string
}

export interface RoleCardsResponse {
  count: number
  role_cards: RoleCardListItem[]
}

export interface RoleCardPreview {
  stem: string
  filename: string
  truncated: boolean
  content: string
}

export interface BibleStageField {
  key: string
  prompt: string
  example: string
  required: boolean
  default: string | number | null
}

export interface BibleStage {
  id: string
  title: string
  fields: BibleStageField[]
}

export interface BibleStagesResponse {
  count: number
  stages: BibleStage[]
}

export interface BibleGuidedResult {
  ok: boolean
  errors: string[]
  bible: Record<string, unknown> | null
  summary: string | null
  kwargs?: Record<string, unknown>
  written_path: string | null
}

/** Loose dashboard snapshot — stable keys from build_studio_dashboard(). */
export interface DashboardSnapshot {
  generated_at?: string
  studio_version?: string
  project?: Record<string, unknown>
  studio?: Record<string, unknown>
  quota?: Record<string, unknown>
  production?: Record<string, unknown>
  readiness?: Record<string, unknown>
  imagine_jobs?: Record<string, unknown>
  sequences?: Array<Record<string, unknown>>
  characters?: Array<Record<string, unknown>>
  nsfw_batches?: Array<Record<string, unknown>>
  sfw_batches?: Array<Record<string, unknown>>
  recent_jobs?: Array<Record<string, unknown>>
  chain_qa?: Array<Record<string, unknown>>
  production_report?: Record<string, unknown>
  artifacts?: Record<string, unknown>
  parallel_briefs?: unknown
  convergence?: Record<string, unknown>
  delivery?: Record<string, unknown>
  model_stack?: Record<string, unknown>
  [key: string]: unknown
}
