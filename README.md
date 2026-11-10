# Survivor Runs - No Road Home

**0.3.1: corrected planted player motion**, following the owner's movement-reference
image. The supplied cowboy now has alternating walk/run support/recovery cycles,
flat rigid boot soles, distance-driven stride phase, an asymmetric leading-knee /
trailing-leg jump synchronized to physics, a landing pose, and a low reclined slide
that coasts and decelerates. Idle/blocked roots do not keep stepping. Existing normal
travel pace now selects **run**, careful aiming/low analog movement selects **walk**,
and Shift selects **sprint**; there is no slow walk clip sliding at running speed.
Backward/sideways aimed motion has directional lower-body clips. Low quality also
retains a lightweight contact shadow. The old model/workshop are kept as history.

- [Motion review/contact sheet](artifacts/player-motion/motion-contact-sheet.jpg).
- [New editable player-motion workshop](blender/open-world/survivor-runs-player-motion.blend).
- [Motion correction verification](PLAYER_MOTION_0.3.1.md).

**0.3.0 foundation: supplied models and real free exploration**, implemented
in the existing Ashfall Run / Survivor Runs project. The earlier 0.2 revision
removed discrete lanes but still auto-ran down a curved corridor. This revision
removes that corridor and forced forward motion rather than merely renaming it.

## Play locally

**GitHub/Vercel publishing requested:** [publishing status](PUBLISHING.md).
Deployment configuration is prepared. The owner confirmed personal/non-commercial
use and cowboy redistribution rights; remote upload/hosting remains blocked by
outbound GitHub/Vercel connectivity and unverified provider authentication.
No public release URL or successful repository upload is claimed.

**http://127.0.0.1:5190** - current optimized build at the same origin used before,
so existing browser-local progress remains available. No public deployment.

[Play Survivor Runs](Play-Survivor-Runs.command) launches the bundled local host.
Requires Node.js 22+; installed npm dependencies are not needed to serve the build.
Opening HTML directly through a file URL cannot load glTF/module assets.

```sh
node serve-built-game.mjs --open
```

Develop/rebuild from this folder:

```sh
npm ci
npm run dev
npm run build
npm test
npm run test:browser
```

The browser tests use the current local production host on port 5190. Historical
0.2 browser tests are retained under the explicitly named `test:browser:legacy`
script; their forward-running assumptions are not the current acceptance contract.
The previous 0.2 download archive is historical and does NOT contain this revision.
No new public release archive is claimed. Owner redistribution permission is now
confirmed; the GitHub/Vercel release is still waiting on working provider access.

## What the request means in this version

### Independent movement, stop and backtracking

One connected **288000 x 288000 mm (288 x 288 m)** world with forest, village,
quarantine, industrial, wreck-yard and camp districts. The districts are reachable
through the same X/S coordinate space, without a lane or forward-only recycle plane.

WASD, arrows and the two-axis touch pad move forward/backward/left/right relative
to the camera. Release to stop. Mouse look can turn through 360 degrees, so movement
is not confined to a fixed straight-ahead presentation. Distance travelled is a
separate cumulative statistic; it no longer drives the player's world coordinate.

Stable two-dimensional chunks retain collected supplies, rescued civilians and
defeated enemy records during backtracking in a run. Irregular vegetation clusters
are independently positioned, scaled and rotated, not alternating mirrored road
edges. Bushes/grass are permeable; tree trunks, wrecks and building exteriors block
movement and bullets. The renderer and collision simulation share scenery records.

A compass and actual world map show position/heading, district layout and nearby
supply/civilian markers. Starting-location unlocks and old save keys are retained.

### Actual supplied models

- **Rugged cowboy:** uses the supplied high-poly model's real geometry and PBR
  textures, reduced from 656667 to 29550 triangles. Added an 18-bone skinned rig,
  locomotion, shooting/reload, jump/slide/dodge and damage/death clips. The weapon
  attaches to the rig's named socket. Both existing character loadouts now use this
  same model, clearly labelled The Drifter / Field Medic rather than pretending
  two different supplied models were provided.
- **Zombie De Goma:** complete supplied glTF/binary/texture package. Retains its
  63-joint skin and all 16 source clips. Runtime aliases connect actual walk, run,
  attack, damage, death and crawling clips to gameplay.
- **Second Zombie:** retains the supplied shirt/boots/head design and textures;
  the static source received an 18-bone skin and new animated clips.
- Existing infected gameplay archetypes use the two supplied bodies, with height
  variants. This is not a claim of five newly authored distinct zombie designs.

[Editable packed Blender actor workshop](blender/open-world/survivor-runs-supplied-actors.blend),
[rig/animation helper](blender/open-world/rig-supplied-models.py), and
[model sources, licenses and changes](blender/open-world/SOURCES.md).

Both zombie packages identify CC BY 4.0 authors/source links in their metadata;
credits are also exposed in in-game Settings. Cowboy redistribution rights were
not supplied or embedded. Local owner preview only until those rights are checked.
Original downloaded files and the old production blend are not overwritten.

### Environment and retained gameplay

Broken cars and trucks, rubble, body bags, ruined exteriors, tents and independent
bush/tree/grass clusters fill the connected districts. An off-centre opening wreck
is a useful landmark. Original ground blood stains and hit-created decals obey the
Blood effects setting. Ground uses procedural earth/moss/leaf detail, not a photo
background. These are existing indie-quality environmental models, not AAA assets.

Six weapon families, finite magazines/reserves, manual reloads, camera/muzzle cover
checks, head/body/leg damage, friendly dog interception/return/treatment, pickups,
rescues, missions, salvage and local-save progression remain. Infected and dogs
now navigate toward radial world-space targets rather than only targets ahead on a
track. Close contacts have attack windups and walls cannot be walked through.

## Controls

- **WASD / arrows:** forward, backward, left and right. Release to stop.
- **Click world:** fire and request mouse capture; **mouse:** look around.
- **RMB:** aim; if capture is unavailable, **RMB drag:** turn the camera.
- **J / L:** keyboard camera turning. **V:** toggle aim mode.
- **Shift:** sprint while moving; spends stamina. **Space:** jump.
- **Ctrl:** timed slide. **Z / X:** left/right dodge.
- **R:** manual reload. **Q / 1-6:** switch carried weapons. **Enter:** fire.
- **E:** nearby civilian rescue / use medical kit for dog. **C:** dog intercept.
- **M / MAP:** show/hide the connected-world map.
- **F:** assisted fire toggle. **Escape / P:** pause; focus loss also pauses.
- **Touch:** independent two-axis left pad and right-side world drag for camera;
  fire, aim, sprint, jump, slide, reload, swap, dog, use and map controls.

## Structure

- [World layout](src/systems/world.js), [streamed rendering](src/environment.js),
  [world map](src/world-map.js), [collision](src/collision.js).
- [Movement](src/systems/movement.js), [infected](src/systems/infected.js),
  [companion](src/systems/companion.js), [navigation](src/systems/navigation.js).
- [Imported model loading](src/assets.js), [camera](src/camera.js),
  [rendering/effects](src/render.js), [controls](src/controls.js).
- [Simulation](src/simulation.js), [combat](src/systems/combat.js),
  [catalog/save migration](src/config.js), [UI](src/ui.js), [audio](src/audio.js).

## Verification and limits

[Current 0.3 test report](TESTING_0.3.md) separates unit/asset checks, actual keyboard
play, spatial fixtures, touch emulation and outstanding physical-device acceptance.
[0.2 testing](TESTING_0.2.md) and [older testing](TESTING.md) are historical evidence,
not proof that their runner-specific assumptions still describe the current game.

This is a **finite, mostly level, connected exploration map**, not an infinite world
or a complete survival/crafting RPG. Buildings are currently exterior cover, not
fully explorable interiors. New static-model skinning/animation needs human art/feel
review. Physical phones, broad hardware FPS/thermal testing, long soaks and human
listening remain unverified. Local single-player browser game only: no multiplayer,
cloud saves, native installer, new accounts, billing or public hosting changes.
