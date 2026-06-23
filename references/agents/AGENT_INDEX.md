

## i2I Refinement Agents (v3.6)

| Agent | File | Role | Activation |
|-------|------|------|------------|
| I2I Cinematic Refiner | `i2i-cinematic-refiner` | Clean cinematic image refinement for narrative work | `ACTIVATE I2I CINEMATIC REFINER` |
| I2I Refiner | `i2i-refiner` | Advanced NSFW/explicit refinement with anatomy + fluid protection | `ACTIVATE I2I REFINER` |

**Routing Note:**
The `studio-director` and `mega-production-architect` now automatically route between these two agents based on content (see `I2I_Routing_Decision_Guide.md`).

- Use `i2i-cinematic-refiner` for most standard cinematic work.
- Use `i2i-refiner` for explicit/intimate scenes.
