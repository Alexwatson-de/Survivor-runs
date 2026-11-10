# Runtime glTF set with shared external PBR textures, avoiding repeated embedded GLB downloads.
# Geometry/rigs/clips stay authored in Blender. Original full-map GLBs remain interchange files.
import os
bpy.context.window.scene=scene
for ob in assets['road_slab'].children_recursive:
    if ob.type=='MESH' and ob.name.startswith('Cracked_asphalt_piece'):
        for face in ob.data.polygons:
            if face.normal.z<0:face.flip()
        ob.data.update()
for mat in M.values():
    for node in mat.node_tree.nodes:
        if node.type!='TEX_IMAGE' or not node.image:continue
        image=node.image;target=128 if 'Roughness' in image.name else 256 if 'Normal' in image.name else 0
        if target and image.size[0]>target:image.scale(target,target);image.pack()
os.makedirs(ROOT+'/public/assets/runtime',exist_ok=True)
for name,root in assets.items():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [root]+list(root.children_recursive):ob.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=ROOT+'/public/assets/runtime/'+name+'.gltf',export_format='GLTF_SEPARATE',export_texture_dir='textures',use_selection=True,use_active_scene=True,export_apply=True,export_animation_mode='NLA_TRACKS',export_merge_animation='NLA_TRACK',export_animations=True,export_anim_slide_to_zero=True,export_optimize_animation_keep_anim_armature=True,export_extras=True)
manifest=json.load(open(ROOT+'/public/assets/manifest.json'));manifest['runtimeFormat']='gltf-separate';manifest['runtimeRoot']='runtime/';manifest['textures']='512 albedo / 1024 skin / 256 normal / 128 roughness';manifest['legacyEffects']=[];open(ROOT+'/public/assets/manifest.json','w').write(json.dumps(manifest,indent=2))
bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
result={'runtime_exports':len(assets),'format':'glTF + shared textures','maps':'512/1024 albedo, 256 normal, 128 roughness'}
