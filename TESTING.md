# ASHFALL RUN — verification report

## Delivered state

A playable original stylized third-person survival runner, not just models or a static scene. Local optimized game: **http://127.0.0.1:5190**. No public deployment, accounts, paid services, native installer or changes to unrelated application sources.

## Executed checks

### 88 logic, asset and build-parity tests — PASS

Command: `npm test`. [Actual output](artifacts/unit-tests.txt).

- **40 simulation checks:** deterministic encounters, forward movement, smooth/clamped lanes, jump/landing, slide duration, differentiated obstacle collisions, evasive movement, damage immunity window, weapon cadence/range/cover, ammunition conservation, partial reloads, cancellation by weapon switching, shotgun spread, assisted fire, distinct enemy pursuit/attacks, non-attacking dead enemies, dog detection/interception/bite/return/cooldown/cover, distinct breeds, pickup effects, death/rewards, mission gates, purchases/upgrades, corrupt-profile repair and persistence.
- Generator exercised over **200 seeds** with advancing 3000 m encounter windows: no obstacle row fills all three lanes.
- A separate **18,000-tick simulation fixture** checks bounded entity inventory during extended generation. Its restored health/invulnerability is explicit fixture setup, not a claim of real-player long-run survival.
- **46 Blender asset checks:** 34 valid GLBs, selected-scene-only export, no original default Cube in any game export, normals/UVs/embedded textures, required human/zombie/dog/weapon animation names and non-empty sampled channels, actual triangle reduction in four LOD families, editable workshop/source-stage existence.
- **2 final surface/build checks:** all 1089 exported earth vertex normals face glTF +Y, and all 34 production GLBs match source-export bytes exactly.

### 24 optimized-build browser checks — PASS

Executed against **http://127.0.0.1:5189**, not the hot-reloading development server:

`ASHFALL_URL=http://127.0.0.1:5189 npx playwright test`

[Actual 24-pass output](artifacts/production-tests.txt), [structured results](artifacts/browser-results.json).

- **18 Chrome checks**, including four mobile/touch workflows and an audio signal fixture.
- **6 WebKit checks:** loading/rendering, actual keyboard movement/jump/slide/pause, manual firing/reload/audio unlock, menu/settings persistence, controlled combat/death/rewards, controlled autonomous dog behavior.
- **14 real-input/UI workflows** versus **10 explicitly labeled controlled fixtures**. Fixtures set encounters, profile salvage, objective thresholds or audio events; they are not presented as unmodified end-to-end survival.
- Touch verification uses actual Chrome DevTools multi-touch events. Logs confirm the **movement** finger lifts while the fire finger remains held, and shots continue afterward.
- Controlled biome inspection visits all five sections, verifies rain and seven recycled segments, and exercises 120 successive segment shifts with bounded geometry inventory.
- Eight restart cycles preserve fresh-run health/kills and bounded pooled-resource counts.

### Continuous real-input mission — PASS

The optimized-build browser test starts Mission 01 through the visible menu, observes nearby encounter state and issues ordinary A/D and R key inputs. It does **not** teleport, set health, add invulnerability, delete enemies, force kills or modify the simulation.

Observed final acceptance run:

- **500.1469 m**, mission complete.
- **58 health remaining**.
- **24 infected stopped**, including **9 companion kills**.
- Seven world segments; 11 visible encounter actors; 19 pooled objects.
- Sampled final renderer: **102 draw calls**, **123,564 triangles**, **78 geometries**, **14 textures**.
- Mean of the final 180 frame intervals: **26.94 ms** (about 37 FPS on this loaded host), not a universal performance guarantee.

An earlier revision also completed 500 m with 100 health, 34 kills and seven companion kills. It is historical evidence, not substituted for the optimized acceptance result above. Initial shader compilation and shared GPU/host load can be much slower; use Low quality on constrained devices. There is no sustained universal 60 FPS claim.

### Post-acceptance terrain correction — PASS, separately scoped

Final visual review identified reversed earth winding that caused self-shadow bands. The original authoring stage now winds upward, and the idempotent [repair stage](blender/08_surface_normals.py) corrected 1024 original polygons. The terrain was re-exported and the optimized build rebuilt. Gameplay source/logic did not change.

After this surface-only correction:

- All **88 unit/asset/parity tests** were rerun and passed.
- Two additional Chrome/WebKit loading/render checks passed: [output](artifacts/surface-verification.txt).
- Final game/menu screenshots were visually inspected; shadow bands are absent from the corrected surface.
- Standalone built-game smoke below passed against the final assets. The entire 24-check suite was not rerun after this normal-only correction; the 24-pass record applies to the otherwise identical pre-correction build.

### Standalone optimized delivery — PASS

[Dependency-free local host](serve-built-game.mjs) serves the included build with Node.js only. HTTP checks returned 200 for the index and GLBs and 403 for an encoded path-traversal attempt. The launcher can use another loopback port if its starting port is occupied.

`node tests/standalone-smoke.mjs`

[Recorded result](artifacts/standalone-verification.json):

- Normal game URL, **without QA hooks**.
- Visible menu → play → real lane input → manual shot → finite-ammo reload → distance advanced to 29 m → pause.
- No page exceptions and **zero external HTTP/HTTPS requests**.
- Embedded GLB textures legitimately decode through 109 same-origin in-memory `blob:` URLs; those are not external network traffic.
- [Final menu](artifacts/final-menu.png) and [final gameplay](artifacts/final-gameplay.png) inspected.

### Audio — PASS at signal level

The optimized suite resumes the real browser AudioContext and measures signals downstream of the master bus for pistol, shotgun, rifle, bark and impact cues. Each produced finite non-silent, sub-full-scale signals, with distinct RMS measurements. The actual measurements are in the `AUDIO_SIGNAL` entry in the [production output](artifacts/production-tests.txt).

This verifies generated Web Audio signals, not physical speaker output or human judgment of realism. All audio is original synthesis, not recorded real firearm/dog audio.

### Build/tooling — PASS

- `npm run build`: successful optimized static build; [output](artifacts/build.txt).
- `node --check` on application JavaScript; Python AST parsing on authoring stages passed.
- `npm audit --omit=dev`: zero production dependency vulnerabilities at the time checked.
- Build warns that the approximately 625 kB JavaScript bundle exceeds Vite's 500 kB advisory. It is not a build failure; code splitting remains an optimization opportunity.
- Blender packed assets report no missing external files. Original scene preserved; editable multi-scene workshop saved.

## Bugs found and corrected

- Exporter initially included the user's default Cube in a second scene. Restricted exports to the active selected scene, re-exported and verified every GLB.
- Export optimization initially omitted constant idle/slide tracks. Kept object animation channels and verified clip inventories.
- Blender/glTF forward-axis mismatch faced the survivor toward the camera. Corrected player, infected, dogs and weapon/flash orientation.
- Dense unbatched forest rendering was slow. Added texture atlas, material/joint batching, actual LODs, instancing, actor reuse, instance-buffer disposal and resolution budgets.
- Very short taps could fall between frames and not fire. Fire now occurs immediately on press; held fire remains rate-limited.
- Global pointer release could cancel a different held action. Fire is tracked by pointer id; actual multi-touch verification passes.
- Prop contact originally used one generic footprint. Collision now uses the modeled wreck/barricade/log/beam dimensions, and cover follows the shot line.
- Ground winding caused shadow bands. Corrected the source winding/export and independently checked final normals/rendering.

Testing corrections are distinguished from game fixes: the first multi-touch fixture released the fire finger; event logs identified this and the fixture now explicitly verifies a movement-finger release. A development-server acceptance run had a page reload and was not treated as passing; the stable optimized build completed all 24 checks. An early external-request assertion incorrectly counted embedded `blob:` texture decoding; the corrected check filters actual HTTP/HTTPS origins and passes.

## Outstanding acceptance gates / intentional limits

- Human art review, listening, blind playtesting and long-term difficulty/economy balance.
- Physical iPhone/Android touch, installability, thermal/battery and accessibility acceptance; tested mobile layouts are emulation, not physical phones.
- Broader GPU/OS/browser coverage, long continuous human play and leak/soak testing beyond the stated fixtures.
- Art is procedural, stylized and budget-conscious, with articulated overlapping meshes; it is not photorealistic skinning, motion capture or a commercial AAA asset library. Packed albedos are 128 px except the 512 px earth map.
- Dogs have different AI/abilities and animations but no separate injury/permadeath system. There is no vehicle driving, multiplayer, online leaderboard, cloud save or native application package.
- Data is browser-local and can be lost when browser storage is cleared. Source-art rebuild wrapper is syntax-checked; individual construction/export stages were executed through the live connector, not a portability test on another machine.
