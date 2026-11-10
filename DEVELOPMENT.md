# Survivor Runs — development record

## Current revision: 0.2.0

The user rejected the original arcade/lane structure and requested a substantial survival-shooter transformation. The title is now Survivor Runs, in the same project folder. Continuous steering/stamina/sprint/dodge, ray/muzzle hit zones, manual finite reloads, flanking infected, friendly companion health/A* retreat/recovery, six weapon families, six locations and five objectives replace the original systems. Nine skinned actor assets, original weapons/ruins/natural props and shared PBR maps were authored and inspected through the live Blender integration before replacement gameplay integration.

98 unit/asset/build checks, 24 production browser workflows, five post-alpha-fix repeats and standalone no-QA smoke pass. See [current report](TESTING_0.2.md) and [upgrade intent](UPGRADE_0.2.md). Old progress migrates by browser origin; old workshop/scenes and unrelated applications are preserved. Human/physical-device/AAA-quality acceptance is not claimed.

## Historical 0.1 record

Original third-person zombie survival runner. Reference images supplied by the user guide worn clothing, mechanical weapon detail, weathered military supply crates, and a foggy abandoned countryside. No reference image is redistributed as a game texture.

## Required order
1. Inspect existing tooling and the live Blender integration.
2. Create reusable modeled, UV-mapped, textured and animated assets in Blender; assemble and visually inspect a countryside scene before game implementation.
3. Export engine-ready assets and implement modular movement, weapons, enemy/dog AI, procedural segments, pickups, progression, UI and audio.
4. Build, exercise real gameplay, inspect screenshots and fix regressions.

## Design intent
- Three lanes, continuous travel, smooth switching, jump and slide, avoidable encounters.
- Third-person shoulder camera; finite ammunition, reloads, distinct weapon handling.
- Walker/runner/brute enemies; at least two distinct companion appearances and abilities.
- Forest, farm, ruined road, checkpoint and settlement section themes with recycling.
- Endless plus finite missions, saved records, unlocks and upgrades.
- Local-first game; no paid services, deployment, credentials or edits to other applications.
- Assets first; no placeholder cube world or primitive stand-in characters.

## Status
Completed the Blender-first workshop and environment review, then implemented a playable Three.js/Vite game. The library has 34 GLBs with packed maps, UVs, authored NLA clips and LODs. The user's original Blender scene was preserved.

88 logic/asset/build-parity tests pass. The optimized-build acceptance run passes 24 Chromium/WebKit browser checks, including independent multi-touch and a real-input continuous 500 m mission. A final ground-normal repair has two additional browser render checks and a standalone, no-QA-hooks production smoke pass. See TESTING.md for exact scope and earlier failures/corrections.

Delivered as a stylized engineering preview: no photorealism, AAA-production, physical-device acceptance, native installer, public deployment or human listening/playtesting claim. No credentials, paid services or unrelated application source changes.
