

## i2I Refinement Routing Protocol (v3.6)

The Studio Director is responsible for intelligently routing image refinement work between the two specialized i2i agents:

### Decision Matrix

| Content Type                              | Recommended Agent              | Reason |
|-------------------------------------------|--------------------------------|--------|
| **Explicit / Intimate / NSFW**            | `i2i-refiner`                  | Requires anatomy lock, fluid physics preservation, micro-expression protection, and specialized artifact guard |
| **Clean cinematic / narrative / standard** | `i2i-cinematic-refiner`        | Optimized for lighting continuity, general consistency, and clean cinematic polish without NSFW-specific constraints |
| **Mixed or uncertain**                    | Ask user or default to `i2i-cinematic-refiner` first, then escalate if explicit elements appear | Safety-first routing |

### Routing Rules

1. **Before any i2i pass on a keyframe or plate**, analyze the current prompt, reference images, and scene intent.
2. If the content includes:
   - Genital contact, nudity with sexual intent, or erotic posing
   - Arousal states, fluids (sweat, saliva, cum, etc.)
   - Ahegao, heavy pleasure expressions, or intimate close-ups
   → **Activate `i2i-refiner`** and pass relevant DNA anchors + NSFW notes.
3. For all other cinematic work (dialogue scenes, action, establishing shots, emotional non-sexual moments, etc.) → **Activate `i2i-cinematic-refiner`**.
4. Always include a short note in the handoff: "i2i routing decision: [agent] because [brief reason]".

### Integration with Other Agents
- `character-dna-extractor` / `identity-lock-specialist` should be called **before** i2i routing when new characters or strong consistency is needed.
- After i2i refinement, continue to `quality-assurance-guardian` regardless of which i2i agent was used.
- For full explicit sequences, route through `erosforge-nsfw-director` first, then use `i2i-refiner` for keyframe fidelity.

**This routing ensures maximum quality and efficiency while protecting both artistic intent and technical fidelity.**
