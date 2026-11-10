# Inspectable assembly is completed BEFORE any game implementation.
workshop=scene
review=bpy.data.scenes.new('ASHFALL • Countryside Review'); bpy.context.window.scene=review
review.world=bpy.data.worlds.new('AF_Mist'); review.world.use_nodes=True
nt=review.world.node_tree; bg=nt.nodes.get('Background'); bg.inputs[0].default_value=(.24,.29,.28,1); bg.inputs[1].default_value=.6
volume=nt.nodes.new('ShaderNodeVolumePrincipled'); volume.inputs['Density'].default_value=.009; volume.inputs['Color'].default_value=(.5,.59,.56,1); nt.links.new(volume.outputs['Volume'],nt.nodes['World Output'].inputs['Volume'])
review.render.engine='BLENDER_EEVEE'; review.render.resolution_x=1440; review.render.resolution_y=900; review.render.resolution_percentage=100
review.render.fps=24

def place(name,loc,scale=1,rot=0,clip=None):
    src=assets[name]; remap={}
    for ob in descendants(src):
        dup=ob.copy(); review.collection.objects.link(dup); remap[ob]=dup
        if dup.animation_data:
            for tr in dup.animation_data.nla_tracks: tr.mute=tr.name!=clip
    for ob,dup in remap.items(): dup.parent=remap.get(ob.parent)
    rr=remap[src]; rr.location=loc; rr.scale=(scale,)*3; rr.rotation_euler.z=rot; return rr
place('terrain',(0,15,0)); place('terrain',(0,-33,0))
for s in [-1,1]:
    for i in range(14):
        x=s*random.uniform(6,17); y=10-i*5
        place('tree_dead' if i%3 else 'tree_pine',(x,y,0),random.uniform(.8,1.5),random.random()*6)
    for i in range(6): place('fence',(s*5,5-i*6,0),1,math.pi/2)
for i in range(14): place('rock',(random.choice([-1,1])*random.uniform(5,18),random.uniform(-55,10),0),random.uniform(.3,1))
place('farm_ruin',(-12,-22,0)); place('checkpoint',(0,-60,0)); place('settlement_ruin',(12,-48,0))
place('car_wreck',(-2.9,-20,0),1,.1); place('barricade',(3,-32,0)); place('low_log',(0,-45,0))
place('supply_crate',(3,-10,0)); place('overhead',(-3,-51,0))
place('survivor_mara',(-.5,2,0),1,0,'run'); place('dog_shepherd',(-2,1,0),1,0,'run')
for i in range(6): place(['zombie_walker','zombie_runner','zombie_brute'][i%3],((-1+i%3)*3,-15-i*6,0),1,math.pi,'walk')
# Weapon in survivor's forward-facing ready position for review scene.
place('weapon_rifle',(-.33,1.48,1.17))
camd=bpy.data.cameras.new('AF_Cinematic_camera'); c=bpy.data.objects.new('AF_Cinematic_camera',camd); review.collection.objects.link(c)
c.location=(6.2,11,4.3); c.rotation_euler=(Vector((0,-17,1))-c.location).to_track_quat('-Z','Y').to_euler(); camd.lens=34; review.camera=c
ld=bpy.data.lights.new('AF_LowSun','SUN'); ld.energy=2.5; ld.angle=.12; sun=bpy.data.objects.new('AF_LowSun',ld); review.collection.objects.link(sun); sun.rotation_euler=(.6,-.4,-.5)
ld=bpy.data.lights.new('AF_SoftSky','AREA'); ld.energy=1200; ld.size=12; ob=bpy.data.objects.new('AF_SoftSky',ld); review.collection.objects.link(ob); ob.location=(0,1,8)
review.frame_set(6)
# Dedicated named low-detail tree/rock props, not primitive billboard stand-ins.
bpy.context.window.scene=workshop
for source in ['tree_dead','tree_pine','rock','car_wreck']:
    root=register(source+'_lod'); remap={assets[source]:root}
    for ob in assets[source].children_recursive:
        dup=ob.copy(); workshop.collection.objects.link(dup); remap[ob]=dup; dup.parent=remap.get(ob.parent,root)
        if dup.type=='MESH':
            dup.data=ob.data.copy(); dec=dup.modifiers.new('Distance LOD','DECIMATE'); dec.ratio=.42
    export_asset(source+'_lod')
bpy.context.window.scene=review
# Packed original textures, original scene preserved in the saved multi-scene file.
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/ashfall-asset-workshop.blend')
result={'review_scene':review.name,'review_objects':len(review.objects),'assets':len(assets),'blend_saved':bpy.data.filepath}
