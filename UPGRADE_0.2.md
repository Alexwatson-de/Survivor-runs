# Survivor Runs — in-place 0.2 overhaul

## Reference study / intent
The supplied screenshots show close, threatening infected; human-scale equipment; irregular muddy tracks; dense layered vegetation; ruined industrial/residential spaces; cold sky fill and isolated warm lights; worn firearms and military clothing. They are visual guidance only, not redistributed textures or models. No playable video attachment is available in this message.

## Replace rather than reskin
- Remove discrete three-lane gameplay. Use continuous lateral acceleration, stamina-limited sprint, dodge, jump/slide and aiming/reloading movement penalties.
- Replace the articulated mannequin assets with anatomically shaped, skinned Blender rigs, more detailed heads/clothing/equipment, weighted animation and authored PBR maps.
- Replace roadside rows with staggered encounters, flanking/emerging/chasing infected, military and special variants, hit zones and attack windups.
- Friendly companion only: health, retreat/recovery, obstacle steering, intercept/bite/return, breed abilities and player commands.
- Six weapon families; actual finite magazines and manual reload; recoil, aim camera and distinct sounds/handling.
- Rebuild asymmetric forest/village/checkpoint/industrial/highway/camp scenery with storytelling props, curved tracks, fog, shadowed depth and readable hazards.
- Preserve existing browser-local records through migration; retain menus, endless, mission progression, pickups, quality settings and touch support.

## Sequence
1. Inspect current source, live Blender session and supplied reference images.
2. Author and inspect upgraded character/dog/weapon/environment assets in Blender, preserving the previous workshop.
3. Integrate assets and replace movement/combat/AI/world/camera systems in the existing project.
4. Run pure-system and real-browser tests, inspect final renders and package the tested build.

## Acceptance honesty
No copied game art, screenshot textures, fabricated video review, universal FPS, physical-device acceptance or AAA-photorealism claim. Report actual visual quality and remaining gaps after inspection. Existing 0.1 reports describe the previous revision and are not evidence for this overhaul.

Status: implemented and verified in the same project. 42 production Blender models, nine skinned actors, 111 authored actor clips, six weapon families, continuous movement and modular survival systems are integrated. 98 pure-system/asset/build checks, 24 production Chrome/WebKit workflows, five effects-repair repeats and standalone no-QA smoke pass; full evidence and limitations are in [TESTING_0.2.md](TESTING_0.2.md). A new downloadable game/source package retains the editable production blend and CC0 provenance.
