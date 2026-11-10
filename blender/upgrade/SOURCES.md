# Survivor Runs 0.2 asset provenance

## Reference material

The user's supplied screenshots were studied for close infected silhouettes, worn military/survival clothing, weapon framing, misty tree depth, abandoned structures and muted lighting. No screenshot pixels, logos or commercial-game assets are redistributed. No playable gameplay video attachment was available in the upgrade message; unrelated video files in Downloads were not treated as references.

## CC0 anatomical groundwork

- **MakeHuman hm08 base mesh**: https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj . Its own header explicitly declares a September 2020 CC0 release. Downloaded as [makehuman-base.obj](reference-base/makehuman-base.obj). Only visible body topology was used; helper geometry was excluded.
- Official license separation: https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md . MakeHuman application code is AGPL; the **graphical assets** (including base meshes/skins) are CC0. No MakeHuman application code is incorporated.
- **OnlyTheGhosts, middle-age Eurasian skin**: MakeHuman Community's official CC0 natural skin pack, https://static.makehumancommunity.org/assets/assetpacks/skins01.html ; download https://files2.makehumancommunity.org/asset_packs/skins01/skins01_cc0.zip . Individual material and diffuse PNG were extracted, processed inside Blender and packed. The pack lists this author/asset as CC0. [Material metadata](reference-base/onlytheghosts_middle_aged_eurasian_female.mhmat), [selected source texture](reference-base/middleage_eurasian_female_diffuse.png).
- [Official CC0 legal text](reference-base/CC0-LEGAL.txt) and [MakeHuman license overview](reference-base/MAKEHUMAN-LICENSE.md) retained.

CC0 attribution is not required, but provenance is retained for transparency. Characters are therefore **original derivative character designs**, not a claim that the base human topology/skin were invented in this session. Original changes include body/outfit proportions, clothed surfaces, equipment, infected wounds/color treatment, rigging, skin weights and authored animation.

## Original project assets

Dogs, firearms, vehicles, trees, shrubs, grass, ruins, camp, warehouse, checkpoint, bridge, supply props, warnings, smoke texture and all animation clips are authored via this project's Blender integration. Wood/metal/clothing/fur/ground PBR maps are generated and packed by the foundation stage. Skin treatments combine the CC0 skin groundwork with original color/deterioration processing.

The game uses original synthesized Web Audio cues and score rather than copyrighted commercial-game sound effects. These are not claimed as recordings of real firearms, dogs or human performers.

## Workflow

The previous workshop and user scenes were preserved. New production scenes were created inside the existing project, with a separately saved production blend. Stages are editable Python authoring files under this folder. Full original-workshop GLBs remain workspace interchange artifacts; optimized glTF/binary/shared-texture runtime exports are under [runtime assets](../../public/assets/runtime/).

The full 99 MB source skin-pack ZIP is a download cache, not included in the game or packaged deliverable. Only the chosen compatible skin and license evidence are needed to reproduce the art.
