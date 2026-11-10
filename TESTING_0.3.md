# Survivor Runs 0.3 verification

**Historical 0.3 foundation milestone.** The current
[0.3.1 player-motion report](PLAYER_MOTION_0.3.1.md) supersedes animation status
and records 132 checks / 16 Chrome-WebKit workflows. Shared browser-result files
may now contain that newer full suite; the 118 / 8 counts below describe the
original 0.3 milestone, not additional tests to add to the current total.

Date: 2026-11-10. Scope: the existing ashfall-run project only, plus its root
workspace overview. Local production origin remains http://127.0.0.1:5190.
No public deployment, repository upload, account, billing or other app changes.

## Build and pure-system/asset checks

- Production Vite build passes. One existing large-bundle advisory remains; this
  is not a build failure. JS syntax is checked by the production bundler.
- **118 tests pass, 0 fail** via `npm test`.
- The retained combat/progression suite is adapted where the old corridor contract
  was intentionally removed: stationary idle, cumulative travel vs independent
  world coordinates, forward/backward/lateral movement, camera-relative movement,
  normalized diagonal acceleration, collision blocking rather than destroying a
  contacted prop, manual finite reload, hit zones, friendly companion, navigation,
  treatment, pickups/rescues, mission completion and old-save compatibility.
- New world checks cover traversal beyond the old +/-6200 mm track boundary,
  radial infected attacks from behind, reverse shots, quarter-turn wreck collision
  bounds, permeable bushes, deterministic non-mirrored vegetation, connected
  districts/spawns, and collected pickup identity/state after sector revisits.
- New asset checks inspect both derivative GLBs for actual skins/weights/UVs/normals,
  bounded triangle counts, clips and weapon socket. The unmodified animated zombie
  retains 16 source clips, its attribution and all local dependencies.
- SHA-256 checks confirm supplied GLB/glTF/binary bytes in the production build
  match the current source assets. Legacy model/texture/selection-image parity
  checks remain; those alone are not evidence for the newly selected actor bodies.

Logs: [build](artifacts/open-world-build.log), [unit checks](artifacts/open-world-unit-run.log).

## Browser acceptance

**8 workflows pass, 0 fail**: four in Chrome and four in Safari-based WebKit.
The final rebuilt-source run completed in approximately 3.6 minutes; this is suite
wall time, not a gameplay performance metric. See
[structured results](artifacts/open-world-browser-results.json) and
[final run log](artifacts/open-world-browser-final.log).

Inspected final renders:
- [Chrome normal-spawn gameplay](artifacts/world-chrome-play.png).
- [Chrome portrait touch input](artifacts/world-chrome-mobile.png).
- [WebKit gameplay](artifacts/world-webkit-play.png).
- [WebKit portrait layout/fallback input](artifacts/world-webkit-mobile.png).
- [Rapid spatial fixture with both zombie designs and wrecks](artifacts/world-chrome-wrecks-zombies.png).

**Normal production launch also passes**, without ?qa or any application test hook:
real keyboard/mouse/DOM input verifies idle, travel, backward input, short-tap fire,
reload, map show/hide, RMB look and pause/resume, with no page errors.
[Standalone results](artifacts/world-standalone-results.json) and
[normal-game screenshot](artifacts/world-standalone-no-qa.png). The local host
serves manifest revision 0.3.0 with forcedForwardMotion=false.
The macOS launcher passes bash syntax validation and now reuses the live 5190
Survivor Runs host instead of opening a second origin with different local saves.

The current suite explicitly distinguishes:

1. Real DOM keyboard controls from a normal spawn: idle/stop, W/S forward/back,
   A/D strafe, J/L turn, map, short Enter fire, R reload, pause/resume.
2. Asset/component evidence: real skins, independent cloned skeletons, canonical
   gameplay clips and sampled deformed mesh vertices; missing-resource responses.
3. A labelled spatial fixture for rapid district/model/wreck review. This is NOT
   a claim that a player naturally traversed the entire world during that test.
4. Portrait 390 x 844 mobile-layout/input emulation. Chromium uses genuine CDP
   multi-touch points for simultaneous pad, camera drag and fire. WebKit's public
   Playwright interface does not offer multi-touch dragging: it uses active mouse
   pointer pad/RMB look fallback plus a real emulated touch tap. Neither is a
   physical phone test.

Browser suites use Low rendering and muted audio to keep verification bounded on
this memory-constrained 8 GB host. They do not establish High-quality FPS or sound
quality. Earlier inspected High-quality Chrome renders also loaded the new actors.

## Defects found during this work

- The previous implementation was still an auto-running narrow track despite
  continuous lateral steering. Replaced it with independent X/S world coordinates.
- Production asset-copy filter initially omitted the supplied-model directory:
  actual browser 404, corrected and byte-parity checked.
- An environment helper incorrectly referenced an out-of-scope scene variable:
  actual browser load error, fixed.
- Forcing Euler roll to zero inverted the camera while looking backward: inspected
  menu render exposed it; fixed using local roll after lookAt.
- Initial spatial skinning leaked torso weights toward arms: corrected after a
  native Blender render. This is still a new artistic rig, not motion capture.
- Fast Enter taps could occur entirely between render-frame samples. Added
  immediate key-down firing, matching the existing mouse/touch edge behavior.
- WebKit returned zero movementX/Y during an uncaptured RMB drag. The real
  fallback input test caught it. Dragging now uses client-coordinate deltas;
  captured mouse input still uses the native relative movement values.
- Backpedalling while firing now keeps the weapon aligned with camera look,
  rather than turning it around between cooldowns; a regression test covers it.
- First touch test used synthetic inactive pointer IDs, which cannot establish
  native pointer capture. Replaced with actual CDP touch and public WebKit fallback
  input, rather than disabling capture checks in application code.
- One earlier trace-heavy browser pass was cancelled after the short-tap failure
  so corrected source could be rebuilt. Full tracing is off for the final suite
  to avoid duplicating large assets/screencasts under host memory pressure.

## Blender/visual evidence

The live connector imported the supplied cowboy and second Zombie. The former was
actually simplified from 656667 to 29550 triangles, then both static models received
18-bone rigs, weights and native NLA clips. Zombie De Goma was also imported into the
new workshop with original clips. The prior production blend/default scene remain.

- [Packed editable workshop](blender/open-world/survivor-runs-supplied-actors.blend).
- [Three supplied actors, native render](artifacts/supplied-actors-blender-review.png).
- [Cowboy selection image](public/assets/ui/survivor_cowboy.png).
- [Second Zombie skinning review](artifacts/zombie-rig-review.png).
- [Provenance and modifications](blender/open-world/SOURCES.md).

Native review caught an importer-generated bone-shape Icosphere being included in
a naive height measurement. It is hidden, and evaluated skinned geometry rather
than the helper determines the final Blender review scale. Runtime glTF does not
contain that generated helper. Packed workshop reports no missing external files.

## Limits / not claimed

- A finite, mostly level 288 x 288 m connected map, not an infinite open world.
  Building exteriors are collision cover; interiors are not currently traversable.
- Human visual/art/input acceptance, polished scan-quality animation, physical
  iPhone/Android controls, audio listening, thermal/battery behavior, broad GPU/OS
  performance and long-soak progression balance remain separate gates.
- Cowboy source has no embedded distribution license. Local owner preview only;
  no new public release archive or hosting until redistribution rights are checked.
- Existing authored environmental models are reused with new spatial placement;
  no claim that every tree/car/bush was rebuilt as a photorealistic asset.
- No current 60 FPS or AAA-quality claim. Host memory pressure caused long tooling
  startup/waits, so test completion time is not a representative gameplay benchmark.
