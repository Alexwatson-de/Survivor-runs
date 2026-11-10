# Actual assembled production environment, separate from the preserved 0.1 workshop.
# Reusable static collections, independent skinned actor copies and bounded volumetric fog.
from mathutils import Vector
# Add original readable safety text to the authored warning sign before final export.
font=bpy.data.curves.new('SR_Warning_lettering','FONT');font.body='STAY BACK';font.size=.12;font.extrude=.0005
text=bpy.data.objects.new('SR_Warning_lettering',font);scene.collection.objects.link(text);text.parent=assets['warning_sign'];text.location=(-.44,-.029,1.63);text.rotation_euler=(math.pi/2,0,0);font.materials.append(M['ivory'])
bpy.ops.object.select_all(action='DESELECT');text.select_set(True);bpy.context.view_layer.objects.active=text;bpy.ops.object.convert(target='MESH');export('warning_sign')
collections={}
for name,root in assets.items():
    col=bpy.data.collections.new('SR_ASSET_'+name);scene.collection.children.link(col)
    for ob in [root]+list(root.children_recursive):
        col.objects.link(ob)
        if ob.name in scene.collection.objects:scene.collection.objects.unlink(ob)
    collections[name]=col
review=bpy.data.scenes.new('SURVIVOR RUNS • Cinematic Countryside');bpy.context.window.scene=review
review.render.engine='BLENDER_EEVEE';review.render.resolution_x=1440;review.render.resolution_y=900;review.render.resolution_percentage=100;review.render.fps=30
review.world=bpy.data.worlds.new('SR_Overcast_world');review.world.use_nodes=True;bg=review.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.10,.15,.16,1);bg.inputs[1].default_value=.6

def place(name,loc,scale=1,rot=0,clip=None):
    if name in rigs:
        remap={}
        for ob in [assets[name]]+list(assets[name].children_recursive):
            dup=ob.copy();review.collection.objects.link(dup);remap[ob]=dup
            if dup.animation_data:
                for track in dup.animation_data.nla_tracks:track.mute=track.name!=clip
        for ob,dup in remap.items():
            dup.parent=remap.get(ob.parent)
            for mod in dup.modifiers:
                if mod.type=='ARMATURE':mod.object=remap.get(mod.object,mod.object)
        obj=remap[assets[name]]
    else:
        obj=bpy.data.objects.new('SR_Placed_'+name,None);review.collection.objects.link(obj);obj.instance_type='COLLECTION';obj.instance_collection=collections[name]
    obj.location=loc;obj.scale=Vector((scale,scale,scale));obj.rotation_euler.z=rot;return obj
place('terrain',(0,12,0));place('terrain',(0,-36,0))
random.seed(75)
for side in [-1,1]:
    for i in range(15):
        y=9-i*4.4;x=side*random.uniform(7,17)
        place('tree_oak' if i%4 else 'tree_dead',(x,y,0),random.uniform(.85,1.35),random.random()*6)
    for i in range(18):place('bush',(side*random.uniform(5.9,14),random.uniform(-70,10),0),random.uniform(.6,1.25),random.random()*6)
    for i in range(40):place('grass_clump',(side*random.uniform(4.8,18),random.uniform(-70,10),0),random.uniform(.65,1.4),random.random()*6)
for i in range(12):place('rock',(random.choice([-1,1])*random.uniform(5.8,14),random.uniform(-70,9),0),random.uniform(.3,.9))
place('car_wreck',(-4.3,-14,0),1,.22);place('truck_wreck',(5.4,-34,0),1,-.25);place('house_ruin',(-12,-30,0),1.25,.12);place('checkpoint',(0,-65,0));place('warehouse',(16,-58,0),1,.3)
place('warning_sign',(4.5,-6,0),1,-.15);place('fence',(-6,-11,0),1,.8);place('body_bag',(-5,-7,0),1,.7);place('rubble',(5,-3,0),1);place('supply_crate',(-3,-23,0));place('barrel',(5,-9,0))
place('survivor_mara',(0,0,0),1,0,'run');place('dog_shepherd',(-1.25,.5,0),.85,0,'run')
for i in range(7):place(['zombie_walker','zombie_military','zombie_runner','zombie_brute','zombie_stalker'][i%5],(random.uniform(-5.5,5.5),-10-i*5,0),1,math.pi,'walk' if i%5!=4 else 'crawl')
# Weapon instance at the survivor's verified grip/socket world pose for this review.
place('weapon_rifle',(.12,-.49,1.31))
# Finite fog bounds avoid infinite-world absorption while giving real volumetric shafts.
mat=bpy.data.materials.new('SR_Bounded_mist');mat.use_nodes=True;mat.node_tree.nodes.clear();out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');vol=mat.node_tree.nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Density'].default_value=.010;vol.inputs['Color'].default_value=(.48,.59,.55,1);mat.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
v=[(x,y,z) for z in [-1,18] for y in [-100,18] for x in [-40,40]];me=bpy.data.meshes.new('SR_Mist_bounds');me.from_pydata(v,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);o=bpy.data.objects.new('SR_Atmosphere',me);review.collection.objects.link(o);me.materials.append(mat)
for name,kind,loc,power,color,size in [('SR_LowSun','SUN',(-20,-40,25),2.8,(.78,.85,.79),0),('SR_SkyFill','AREA',(0,-2,10),2100,(.60,.76,.80),18)]:
    data=bpy.data.lights.new(name,kind);data.energy=power;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    if kind=='SUN':data.angle=.13
    ob=bpy.data.objects.new(name,data);review.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,-20,0))-ob.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('SR_Shoulder_review');cam=bpy.data.objects.new('SR_Shoulder_review',cd);review.collection.objects.link(cam);cam.location=(.9,4.5,2.05);cam.rotation_euler=(Vector((.6,-15,1.25))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=29;review.camera=cam;review.view_settings.exposure=.7;review.frame_set(7)
review.render.filepath=ROOT+'/artifacts/survivor-runs-blender-world.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
# Explicit runtime inventory: unused 0.1 prototypes remain historical, not loaded by the new game.
manifest={'title':'Survivor Runs','revision':'0.2.0','assets':list(assets),'legacyEffects':['fx_flash','fx_impact','fx_blood','fx_dust','fx_smoke','fx_explosion'],'rigType':'armature/skinned','humanBase':'CC0 MakeHuman hm08','skinBase':'CC0 OnlyTheGhosts middle-age Eurasian skin','textures':'512 PBR / 1024 skin'}
open(ROOT+'/public/assets/manifest.json','w').write(json.dumps(manifest,indent=2))
result={'production_blend':bpy.data.filepath,'render':review.render.filepath,'asset_count':len(assets),'review_scene':review.name}
