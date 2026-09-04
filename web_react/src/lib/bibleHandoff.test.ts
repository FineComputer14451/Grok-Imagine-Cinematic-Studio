/**
 *   npx tsx src/lib/bibleHandoff.test.ts
 */
import { buildBibleHandoff } from './bibleHandoff'

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg)
}

const handoff = buildBibleHandoff({
  bible: {
    project_title: 'Rain Code',
    genre: 'Sci-Fi',
    target_duration_seconds: 90,
    complexity: 'High',
    director_signature: 'Wet neon',
  },
  kwargs: {
    title: 'Rain Code',
    genre: 'Sci-Fi',
    target_duration_seconds: 90,
    complexity: 'High',
    video_model: 'grok-imagine-video-1.5',
    chat_model: 'grok-4.5',
    director_signature: 'Wet neon',
  },
  answers: {
    title: 'Rain Code',
    logline: 'A detective hunts a rogue AI.',
    characters_text: 'Mara: exhausted detective.\nKai: rogue AI.',
    genre: 'Sci-Fi',
    target_duration_seconds: 90,
  },
  written_path: 'artifacts/bibles/rain-code.json',
})

assert(handoff.chat_model === 'grok-4.6', `chat remap ${handoff.chat_model}`)
assert(handoff.title === 'Rain Code', 'title')
assert(handoff.seeds.dna_init.name === 'Mara', `dna name ${handoff.seeds.dna_init.name}`)
assert(handoff.seeds.sequence_init.duration === '90', 'seq duration')
assert(handoff.seeds.sequence_init.genre === 'Sci-Fi', 'seq genre')
assert(handoff.seeds.sequence_init.name === 'Act 1', 'seq name')
assert(handoff.next_steps.length >= 4, 'next steps')
assert(
  handoff.next_steps.some((s) => s.action === 'dna_init' && s.to === '/dna'),
  'dna step',
)
assert(
  handoff.next_steps.some((s) => s.action === 'sequence_init'),
  'seq step',
)

console.log('bibleHandoff.test.ts OK')
