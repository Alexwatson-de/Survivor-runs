# Player motion correction - 0.3.1

## Request and cause

The owner reported that the supplied cowboy looked like it was surfing despite
having a walk clip, and that jumping kicked both legs forward. The supplied sprite
reference establishes alternating walk/run support and recovery, an asymmetric
jump, and a low reclined slide. It is used as pose/timing direction, not copied art.

The previous renderer moved the root at 4.7 m/s while selecting a slow 1.6 s walk
with a small sinusoidal leg arc. Playback used an arbitrary speed/4.7 multiplier;
there was no planted support-foot interval. The jump applied identical rotations
to both legs. Slide was effectively a moving squat. Ground display was also 25 mm
below the actor origin, and Low quality had no player contact shadow.

## Changes

- [New Blender authoring source](blender/open-world/player-motion.py) builds new
  walk/run/sprint clips using two-bone leg IK, flat support soles and a linear
  backward foot path during stance. Strides are **1100 / 2400 / 3000 mm per full
  left-plus-right cycle**. Recovery feet lift and return independently.
- Reweighted lower-body vertices by side/anatomical height, with rigid boot soles
  and smooth ankle/knee transitions. A boot no longer blends toward the opposite
  leg/shin while it is supposed to be planted. The supplied surface/materials and
  29550-triangle budget are retained.
- [Runtime motion controller](src/player-motion.js) advances gait phase from
  **actual grounded distance**, not elapsed render time. Collision-blocked roots
  stop stepping. Normal travel selects run; careful aimed travel/low analog input
  selects walk, and Shift selects sprint. Existing normal/sprint travel pace is
  preserved; careful aimed travel is reduced to approximately 1550 mm/s.
- Eight directional walk/run variants support backward/sideways/diagonal travel
  while aiming, without requiring the gun to face away from the camera.
- Jump is sampled from its physical launch/flight progress, not started late when
  the player exceeds a 100 mm height threshold. The leading knee rises while the
  trailing leg folds separately. Legs extend toward landing; stationary landings
  have a brief compression pose. Moving landings resume the travel-driven gait.
- Slide is low and reclined, with one extended and one folded leg. Physical slide
  movement coasts along its entry direction and slows after input release, rather
  than running the ordinary walking controller under a crouch. Its top stays below
  the game's low collider top in the measured pose. The slide period remains 0.92 s.
- The root display offset matches the actual ground plane; a lightweight contact
  shadow remains enabled on Low. Jump lift remains owned by the simulation, not
  double-applied by animation root motion.
- The selected asset is a separately named
  [new runtime GLB](public/assets/supplied/survivor_cowboy_motion.glb). The old actor
  GLB, supplied downloads, zombie animation and earlier workshops are preserved.
- [Separate editable motion workshop](blender/open-world/survivor-runs-player-motion.blend)
  contains the new native clips. Other Blender scenes/default objects remain.

## View the result

- [Actual game movement preview](artifacts/player-motion/player-motion-review.mp4).
- [Native pose/contact sheet](artifacts/player-motion/motion-contact-sheet.jpg).
- [In-game run](artifacts/player-motion/game-run-side.png),
  [walk](artifacts/player-motion/game-walk-side.png),
  [jump](artifacts/player-motion/game-jump-side.png),
  [slide](artifacts/player-motion/game-slide-side.png).
- [Normal third-person grounded view](artifacts/player-motion/game-grounded.png).

The video uses the actual game renderer and real key/mouse controls, with an
explicit **side-camera QA fixture and combat disabled** to expose the feet. It is
not a claim of untouched normal gameplay, real-time benchmark or human approval.
The native sheet shows authored poses plus simulated jump lift, without the game
weapon attached. Game images/video include the weapon socket/attachment.

## Verification

- Production build passes. The existing large-JS-chunk advisory remains.
- **132 unit/asset checks pass, 0 fail**, including 14 new locomotion regressions:
  clip selection, directional clips, early jump launch, physics phase, no ground
  gait advance in flight, one landing, coasting slide, collision-stopped strides,
  frame-rate-independent distance phase and exact selected GLB/stride metadata.
- **All 16 Chrome/WebKit workflows pass**, 8 per browser: 8 new motion workflows
  plus the retained 8 world/keyboard/actor/mobile workflows. New motion workflows
  use real W/aim/Shift/Space/Ctrl inputs and labelled non-combat fixtures; they
  assert asymmetry during actual flight, landing and slide deceleration, and sample
  the exported skinned geometry rather than merely seeing bone channels.
- Normal production-origin launch with **no QA hook** passes the retained real
  control smoke journey without page errors.
- Exported-geometry fixture samples **461 actual left-sole vertices**. Maximum
  world-space drift over the sampled steady stance interval:
  - Walk: **0.151 mm**.
  - Run: **0.770 mm**.
  - Sprint: **2.576 mm**.
  - Backward walk: **0.148 mm**.
  - Rightward run: **0.956 mm**.
- At the exported mid-jump pose, the feet differ by **610 mm fore/aft** and
  **210 mm vertically**, instead of matching forward kicks.
- Sampled slide top is **862 mm in game Y coordinates**, below its 880 mm collider
  top. The ground plane is -25 mm; measured sole bottom is -24.1 mm (about 0.9 mm
  above the visible plane). These are game-coordinate measurements, not a claim
  that top-minus-ground is 862 mm.
- Native Blender stance cancellation residual is below **0.002 mm** for the three
  forward gaits, with no IK reach clipping after adjustment. The slightly larger
  exported residual includes sampling/interpolation, which the browser checks.
- Actual final game screenshots/native frames inspected, including full jump
  envelope and the low slide. Initial slide export was 917 mm at the top; native
  pose was corrected and the export remeasured before completion.

Evidence:
- [Build log](artifacts/player-motion/build.log).
- [132-check log](artifacts/player-motion/unit.log).
- [16-workflow log](artifacts/player-motion/browser.log) and
  [structured browser results](artifacts/open-world-browser-results.json).
- [Exported skinned contact measurements](artifacts/player-motion/exported-contact.json).
- [Native contact and IK evidence](artifacts/player-motion/native-contact.json).
- [Normal-launch log](artifacts/player-motion/standalone.log).
- [Preview capture result](artifacts/player-motion/preview-results.json).

## Boundaries

The sub-3 mm drift values describe sampled straight, steady support phases in the
specified clips. They do **not** prove perfect foot locking during every turn,
transition, collision interruption or on arbitrary slopes. Current world ground is
mostly level; this is not a general uneven-terrain foot-placement solver. Fast turns
and blend acceptance still benefit from human play review. New poses use the supplied
scan's topology; no AAA/motion-capture/anatomical-perfection claim is made.

Physical-phone/thermal performance, human input/animation acceptance and cowboy
redistribution rights remain unverified. No public deployment, account/billing change,
new models for unrelated actors or unrelated application-source edits were made.
Local play stays **http://127.0.0.1:5190**; refresh an older open tab to load 0.3.1.
