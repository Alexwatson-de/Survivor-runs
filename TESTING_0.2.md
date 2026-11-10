# Survivor Runs 0.2 — verification record

This report covers the **in-place 0.2 survival-shooter overhaul**, not the archived three-lane 0.1 game. Optimized local build: **http://127.0.0.1:5193**. No deployment, native installer, account/cloud-save, paid service or unrelated application-source change.

## Completed evidence

### 98 pure-system / asset / build checks — PASS

`npm test` runs only the current overhaul suite. [Actual output](artifacts/survivor-unit-tests.txt).

- **50 simulation checks:** continuous steering/acceleration/path bounds; sprint/exhaustion/stamina recovery; aim/reload movement penalties; jump/landing/timing; slide/dodge; realistic prop envelopes; free-route avoidance; camera/muzzle ray hit zones; headshots/leg slows/armor/nearest-body cover; friendly dog excluded from bullets; finite magazines with no automatic reload; partial reserves/cancelled reloads; six firearm families; off-track chase/emergence; attack windups and dodge escape; dead-enemy exclusion; companion A* obstacle corridor/intercept/bite/return/health/retreat/down/medical treatment; pickups/rescue; objectives/rewards; record migration; unlocks and world curvature.
- **46 asset checks:** 42 production glTF models with normals/UVs/resolvable binary and texture resources; nine real skins/armatures and authored clip inventories; required new infected/weapon/location models; actual Blender selection-image renders; weapon socket; matching ground boundary heights/upward normals; CC0 provenance and saved production blend.
- **1 build-parity check:** all runtime geometry/binaries/textures/selection images in the built game match current source-export bytes; visible title is Survivor Runs, not Ashfall Run.
- **1 particle-format check:** the final smoke texture has a real RGBA channel, not an opaque RGB square.

The previous test files remain historical in the workspace; they are not used as evidence for new mechanics.

### Asset and performance audit

[Actual inventory](artifacts/survivor-asset-audit.json): **42 production models**, nine skinned actor assets, ten selection images; shared glTF runtime set **24,774,038 bytes** before selection images/site code.

Original full-map GLBs repeated textures and totalled approximately 141 MB. Blender exports were optimized to shared separate glTF/binary/textures, then the game builds a color/normal/roughness/metallic atlas. A diagnostic comparison reduced the sampled low-quality scene from 244 draw calls / 123 textures to around 41 calls / 11 textures. This is a render-budget improvement, not a promise of a fixed FPS on all hardware.

Full PBR maps/rigs are editable in [the production blend](blender/survivor-runs-production.blend). Human anatomy/skin use legally documented CC0 groundwork; all derivatives, equipment, dogs, environment props, rigs and animations are recorded in [provenance](blender/upgrade/SOURCES.md).

### Browser integration / actual gameplay

The first production pass executed 24 browser checks: **21 passed**, with three Chrome timing-sensitive failures. All six WebKit checks passed in that pass. The corrected focused Chrome repeat passed **3/3**: [focused repeat](artifacts/survivor-focused-tests.txt).

Corrections to test setup, not hidden gameplay shortcuts:
- A supposed 180 ms held steering interval was much longer on the overloaded host; the test incorrectly assumed it could not travel beyond 3 m. It now checks continuous path-bounded displacement and absence of a lane property; exact acceleration/intermediate positions are covered in deterministic units.
- The jump fixture inserted a near obstacle before a delayed keyboard event, so the survivor collided before jumping. It now stages the obstacle at the actual keyboard-event time and resets controlled-fixture health. The normal jump/slide simulation is not bypassed.
- The moving-target headshot fixture aimed once at a stale screen projection. It now reacquires the target through the actual camera and fires ordinary mouse shots; it does not freeze/kill the target or set aiming rays directly.

A clean full production regression passed **24/24** checks: **18 Chrome** (including four touch workflows) and **6 WebKit**, with no retries. [Full output](artifacts/survivor-final-browser-tests.txt), [structured results](artifacts/survivor-browser-results.json).

After that full pass, visual inspection caught an RGB-only particle export that made smoke/flash points visibly square. Blender's [RGBA repair stage](blender/upgrade/14_particle_alpha.py) creates a genuine soft mask; its corner alpha is zero and center alpha 229/255. The image was rebuilt into the game. **All 98 pure-system/asset/build checks** passed again, plus **5/5 Chrome/WebKit loading/fire/reload/touch checks**: [effects repeat](artifacts/survivor-effects-repeat.txt). Corrected screenshots were visually inspected; square particle edges are gone. Gameplay source/logic did not change for this image-only fix, and the entire 24-check suite was not repeated after it.

### Continuous real-input mission — PASS

The initial production browser pass completed the 500 m first mission via visible menus, ordinary held steering keys, optional assisted firing and **manual R reload inputs**. The route-driving agent observes encounter state, but does not teleport, add invulnerability, set health, remove enemies, force objectives or force kills.

Observed finish: **500.0689 m**, **30 health**, **38 infected stopped**, **11 companion kills**, **80 shots**, **70 damage received**. Final sampled mean of 180 frame intervals: **19.44 ms**, approximately 51 FPS on that sample, with 85 render calls / 395,521 triangles / seven recycled segments. Host load/startup varies; this is not a sustained universal 60 FPS claim.

The clean full repeat also completed normally: **500.0040 m**, **100 health**, **36 kills**, **10 companion kills**, **72 shots**, no damage. Final sampled frame interval was **38.42 ms** with 88 calls / 445,506 triangles / 43 geometries / 36 textures / seven segments. The two samples show load variability, not a fixed frame-rate guarantee.

### Input, visual and sound verification

Executed browser checks include actual Chrome DevTools multitouch: analog-steering finger release is separately logged while held-fire continues. Real touch jump/slide/aim/fire/reload and portrait/landscape UI navigation pass in the first production run.

Six locations were rendered and visually inspected as controlled fixtures; geometry/texture/segment inventories remain bounded during recycling. Menu and selection previews render actual authored assets; previews are not concept-image replacements.

The audio fixture samples the real browser master AudioContext bus. Six firearm signatures produced finite non-silent sub-full-scale signals with distinct RMS values. HRTF threat-positioning code is exercised. Original synthesis is not a claim of recorded real guns, dogs or human performers; physical speaker output/human listening are separate acceptance gates.

### Build/tooling — PASS

- Optimized build succeeds: [build output](artifacts/survivor-build.txt). Built website is approximately 30 MB with runtime assets and selection images.
- `node --check` on source/system/host/config JavaScript and Python AST parsing on upgrade stages pass.
- `npm audit --omit=dev`: zero production vulnerabilities when checked; [output](artifacts/survivor-dependency-audit.txt).
- Vite reports a roughly 673 kB JavaScript chunk above its 500 kB advisory. It is not a build failure; further splitting/lazy loading remains an optimization opportunity.

## Important scope and limits

- The game is now a complete playable **continuous-movement survival shooter**, not a static environment or three-lane arcade re-skin. Art is substantially rebuilt but still budget-conscious procedural indie art—not AAA photorealism, motion capture or equivalent commercial-game visual quality.
- Weighted skeletal animation, mapped PBR detail, anatomical CC0-derived human surfaces and original equipment are real assets. Clothing has secondary pack movement, not a full cloth simulation; dogs use mapped coats, not expensive simulated fur.
- Blender's cinematic review uses bounded volumetric mist. Browser rendering uses less expensive scene fog, particles, shadows and grading; it does not physically simulate full volumetric scattering.
- Human art/audio approval, blind playtesting, long-term economy/difficulty balance, physical-phone input/thermal behavior, broad GPU/OS coverage and long human soak tests remain unverified.
- Companion health/retreat/recovery is functional, but no permanent dog death. All companions remain friendly; there is no enemy-dog system.
- Browser-local progress can be lost when storage is cleared. No public hosting, native app, multiplayer, online leaderboard or cloud sync is supplied.
- Individual Blender stages were executed through the live integration and inspected; portability of a full automatic rebuild on another workstation remains a separate check.

## Final regression and delivery

The final standalone built-game smoke test passes at the original **http://127.0.0.1:5190/**, without QA hooks: normal menu → run → held steering → mouse fire → explicit reload → distance 20 m → pause. Magazine 12 / reserve 58 demonstrates actual consumed/reloaded rounds. **No page exceptions or external HTTP/HTTPS requests** occurred. [Standalone record](artifacts/survivor-standalone-verification.json), [final menu](artifacts/survivor-final-menu.png), [final gameplay](artifacts/survivor-final-gameplay.png).

The original URL continues to serve the new built game, allowing same-origin v1 progress migration. The new [launcher](Play-Survivor-Runs.command) requires Node.js only; no npm dependency install is required for the included static build.

The [game/source ZIP](artifacts/releases/Survivor-Runs-0.2.0-game-and-source.zip) is approximately 63 MB and has per-file SHA-256 verification, ZIP CRC checks and executable launcher-mode verification. It includes the production blend, optimized game, current source/tests, shared assets, CC0 provenance and reports; it excludes node_modules, unrelated workspace files, the 99 MB source skin-pack download cache and redundant full-map GLBs.

An extracted copy was launched from an independent temporary folder using only Node.js built-in HTTP, **without node_modules**. Normal-URL real steering, firing and manual reload passed; distance 12 m, magazine 12 / reserve 59, no QA hooks, no page exceptions. [Extracted verification](artifacts/releases/survivor-extracted-verification.json), [release manifest](artifacts/releases/survivor-release-manifest.json), [checksum](artifacts/releases/Survivor-Runs-SHA256.txt). The archived 0.1 report is not evidence for this revision.
