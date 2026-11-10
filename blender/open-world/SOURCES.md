# Survivor Runs 0.3 - supplied actors

Owner request: replace the character and infected designs with the three supplied
models, retain their visible textures, and make real free exploration rather than
just removing discrete lanes. No account, hosting or unrelated application change.

## Cowboy

- Owner-supplied source: `/Users/softage/Downloads/ga-free-451-rugged-cowboy-high-poly/source/03e.glb`.
- Source metadata: Khronos glTF Blender I/O v4.4.55; one Mesh_0, 383,913 vertices,
  656,667 triangles, no skin and no animation. Three packed 2048 px images.
- Working derivative: 29,550 triangles, 31,219 vertices before GLB seam expansion;
  native Blender Decimate ratio 0.045. Original geometry remains hidden in the
  new blend, and the supplied file was not edited.
- Added 18-bone spatially weighted rig, in-place locomotion, jump, slide, dodge,
  damage/death, shooting/reload clips and a weapon attachment bone. Corrected
  torso-to-arm weight leakage after an inspected render. Runtime maps are 1024 px.
- Height: 1800 mm. Both retained character/save keys use this one supplied model;
  they are different statistical loadouts, not two independently modeled people.
- **0.3.1 motion correction:** new [player-motion authoring source](player-motion.py)
  and [separate review workshop](survivor-runs-player-motion.blend). Original
  lower-body animation and weights are superseded by side-isolated ankle/knee
  weights, rigid soles, IK planted/support cycles with declared stride lengths,
  directional aimed locomotion, asymmetric jump and low reclined slide. Original
  source geometry/materials and zombie clips are not changed. The game's selected
  derivative is now the separately named survivor_cowboy_motion GLB, not a silently
  overwritten 0.3 actor file. Upper-body shoot/reload and unrelated actions remain.
- No license/author record was embedded in the supplied GLB. The folder name is
  not proof of redistribution rights. On 2026-11-10 the owner explicitly confirmed
  permission to publicly redistribute the supplied model/derivative GLBs, and
  personal/non-commercial use. See [publishing permission record](../../PUBLISHING.md).
  An apparent original publisher is Galaxy Abundant on Sketchfab; no exact
  publisher license is independently verified or invented here.

## Zombie De Goma

- Owner-supplied package: `/Users/softage/Downloads/animation-zombie/source/zombie_de_goma/`.
- Embedded author: [julianmurcia245](https://sketchfab.com/julianmurcia245).
- [Original model](https://sketchfab.com/3d-models/zombie-de-goma-d0da88595c6b47129170937d1e442733).
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Copied the complete original glTF, binary and texture dependency into the local
  runtime. Two mesh primitives, 63 skin joints, 16 original animation clips.
- Runtime adaptation: 1820 mm standing envelope, canonical clip aliases for walk,
  run, attack, hit, death and crawl. The source geometry, texture and original clip
  package are not regenerated. Standing and crawling gameplay states select the
  corresponding supplied clips. Brute variant scales to 1980 mm.
- Blender inspection excludes the importer's non-renderable bone-shape helper
  when measuring the evaluated skinned mesh. The helper is hidden in the saved
  review scene; it is not part of the runtime GLTF.

## Second Zombie

- Owner-supplied source: `/Users/softage/Downloads/zombie.glb`.
- Embedded title/author: Zombie by [piRat / GrimZu](https://sketchfab.com/GrimZu).
- [Original model](https://sketchfab.com/3d-models/zombie-0541416bd635486f95cb3d44f8f676c1).
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Five textured body/clothing primitives; source has no skin or clips. Added an
  18-bone rig and original walk/run/attack/hurt/death/crawl animation derivative.
- Runtime height 1820 mm; military-stat variant scales to 1860 mm. The supplied
  shirt/boots/head design is retained; no claim of five distinct new zombie models.

## Deliverables and earlier art

- [Editable actor workshop](survivor-runs-supplied-actors.blend), with packed
  textures, retained high-poly/source meshes, both new rigs and imported animation.
- [Rig/animation helper source](rig-supplied-models.py).
- Runtime derivatives are under [supplied assets](../../public/assets/supplied/).
- Dogs, six weapons and environmental props remain the project-authored 0.2 art;
  see [historical provenance](../upgrade/SOURCES.md). Their placement is now
  independent two-dimensional clustered terrain, with procedural dirt/leaf ground
  and original blood-stain decals. No image attachment is used as a screenshot
  backdrop or as a replacement for the supplied models' proper UV textures.
- In-game Settings includes both zombie authors, source links, license and changes.
