# Stitch Artifact Lexicon

Shared vocabulary and prompt packs for extend/stitch continuity (roadmap #11).

## Usage

- **Module:** `tools/stitch_artifact_lexicon.py`
- **CLI:** `sequence artifact-lexicon` (list / pack / inject)
- **Re-gen:** `extend_regen` consumes suggested packs from seam + chain QA evidence
- **Default pack:** `flicker`, `morph`, `halo`, `identity_melt`, `wardrobe_teleport`, `lighting_pop`, `motion_hitch`

## API

- `list_entries(category=None)` — catalog entries
- `get_entry(entry_id)` — single entry
- `build_negative_pack(entry_ids=None, all_default=False)` — negative prompt phrases
- `build_positive_guards(entry_ids=None)` — affirmative continuity language
- `suggest_entries_from_seam(seam_report)` — map seam factors → entry ids
- `suggest_entries_from_chain_qa(chain_qa)` — map critical QA keys → entry ids
- `format_lexicon_markdown(entry_ids=None)` — this reference format

## Catalog

## `flicker` — Temporal flicker

- **Category:** temporal
- **Aliases:** strobe, frame flicker, temporal flash
- **Description:** Frame flashing or strobing at the stitch boundary where temporal sampling or blend modes fight between adjacent clips.
- **Symptoms:**
  - brief strobe or flash at cut/extend join
  - alternating brightness across 1–3 frames
  - unstable exposure at seam
- **Negative pack:** temporal flicker, frame flicker, strobe flash at stitch, flashing frames, exposure strobing
- **Positive guards:** stable temporal sampling across the stitch; smooth exposure continuity at the join; no frame flash or strobe at the boundary
- **QA hooks:** stitch_artifact_risk, last_frame_continuity

## `morph` — Face/body morph

- **Category:** identity
- **Aliases:** face morph, body melt, geometry morph
- **Description:** Face or body geometry melts or warps between clips at the extend/stitch boundary instead of holding identity lock.
- **Symptoms:**
  - facial landmarks slide or warp at join
  - body proportions briefly intermediate
  - mesh-like melt between two identities or poses
- **Negative pack:** face morph, body morph, geometry melt at stitch, warping face at boundary, melting features between clips
- **Positive guards:** locked facial geometry across the stitch; stable body proportions at the join; hard identity continuity, no morph between frames
- **QA hooks:** character_drift_boundary, identity_lock, stitch_artifact_risk

## `halo` — Edge halo / double contour

- **Category:** geometry
- **Aliases:** edge glow, double contour, outline halo
- **Description:** Edge glow, fringing, or double contour around subjects at the stitch from mismatched mattes, sharpening, or blend residuals.
- **Symptoms:**
  - bright or dark rim around subject edges
  - ghosted double outline
  - chromatic fringe at silhouette
- **Negative pack:** edge halo, double contour, outline glow, fringing around subject, ghost edges at stitch
- **Positive guards:** clean single silhouette edge; no halo or double contour at the boundary; matched edge treatment across the join
- **QA hooks:** stitch_artifact_risk

## `identity_melt` — Identity melt

- **Category:** identity
- **Aliases:** feature blend, identity blend, co-star melt
- **Description:** Character features blend toward a co-star or prior frame identity, breaking DNA / identity lock across the seam.
- **Symptoms:**
  - eyes, nose, or jaw shift toward another face
  - skin tone or age drifts mid-join
  - DNA lock fields no longer match hero reference
- **Negative pack:** identity melt, feature blend toward another face, character identity drift at stitch, face blending with co-star, DNA lock break
- **Positive guards:** strict identity lock to hero DNA across the stitch; unchanged facial landmarks and skin tone at the join; no feature blend toward other characters or prior frames
- **QA hooks:** character_drift_boundary, identity_lock

## `wardrobe_teleport` — Wardrobe teleport

- **Category:** wardrobe
- **Aliases:** costume jump, clothing change, outfit pop
- **Description:** Clothing or accessories change without story motivation at the stitch boundary (teleport outfit, missing layers, color swap).
- **Symptoms:**
  - jacket/shirt color or cut changes at join
  - accessories appear or vanish
  - fabric state (wet/dry, torn) resets
- **Negative pack:** wardrobe teleport, sudden costume change, clothing pop at stitch, outfit discontinuity, accessories appearing or disappearing
- **Positive guards:** identical wardrobe continuity across the stitch; same layers, colors, and accessories at the join; no unmotivated costume change
- **QA hooks:** wardrobe_consistency, stitch_artifact_risk

## `lighting_pop` — Lighting pop

- **Category:** lighting
- **Aliases:** key shift, color pop, exposure jump
- **Description:** Sudden key, fill, or color temperature shift at the seam without motivated lighting change.
- **Symptoms:**
  - key light direction or intensity jumps
  - white balance / color grade snaps
  - shadow density resets at boundary
- **Negative pack:** lighting pop, sudden key shift, color temperature jump, exposure pop at stitch, ungraded lighting discontinuity
- **Positive guards:** matched key and fill continuity across the stitch; stable color temperature and exposure at the join; no unmotivated lighting pop
- **QA hooks:** lighting_color_match, stitch_artifact_risk

## `prop_pop` — Prop pop

- **Category:** geometry
- **Aliases:** prop teleport, object appear, object disappear
- **Description:** Props or set dressing appear, disappear, or jump position at the stitch without narrative cause.
- **Symptoms:**
  - handheld object vanishes mid-action
  - background prop swaps position
  - set dressing density changes abruptly
- **Negative pack:** prop pop, props appearing or disappearing, object teleport at stitch, set dressing jump, background object discontinuity
- **Positive guards:** stable prop placement across the stitch; same handheld objects and set dressing at the join; no unmotivated prop appear or disappear
- **QA hooks:** physics_realism, stitch_artifact_risk

## `lip_desync` — Lip desync

- **Category:** audio
- **Aliases:** mouth desync, lip sync fail, dialogue mouth lag
- **Description:** Mouth motion out of phase with dialogue or audio momentum at the extend boundary (especially native-audio 1.5 pipelines).
- **Symptoms:**
  - mouth still moving after line ends
  - phoneme shapes lag dialogue
  - silent mouth flap or frozen lips under speech
- **Negative pack:** lip desync, mouth out of phase with dialogue, bad lip sync at stitch, dialogue mouth lag, unsynced mouth motion
- **Positive guards:** mouth motion locked to dialogue timing across the stitch; clean lip sync continuity at the join; audio and mouth performance in phase
- **QA hooks:** lip_sync, audio_sync

## `motion_hitch` — Motion hitch

- **Category:** temporal
- **Aliases:** velocity hitch, motion discontinuity, speed pop
- **Description:** Velocity or easing discontinuity at the stitch — motion stalls, snaps, or changes speed without physics motivation.
- **Symptoms:**
  - subject freezes then resumes
  - camera speed pops at join
  - action energy resets abruptly
- **Negative pack:** motion hitch, velocity discontinuity, speed pop at stitch, motion stall then snap, physics hitch at boundary
- **Positive guards:** continuous motion velocity across the stitch; matched easing and momentum at the join; no hitch, stall, or speed pop at the boundary
- **QA hooks:** physics_realism, stitch_artifact_risk, last_frame_continuity

## `resolution_swim` — Resolution swim

- **Category:** temporal
- **Aliases:** sharpness swim, detail pump, soft sharp pump
- **Description:** Soft/sharp pumping or detail level swimming across frames at the seam from inconsistent denoise, upscale, or generation quality.
- **Symptoms:**
  - alternating soft and crisp frames
  - facial detail pumps in and out
  - texture clarity unstable at join
- **Negative pack:** resolution swim, sharpness pumping, soft sharp oscillation, detail swim at stitch, inconsistent sharpness across frames
- **Positive guards:** stable resolution and sharpness across the stitch; matched detail level at the join; no soft/sharp pumping or resolution swim
- **QA hooks:** resolution_stability, stitch_artifact_risk
