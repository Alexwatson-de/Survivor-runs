# Broken asphalt is a Blender asset, not a clean procedural racing-track plane.
bpy.context.window.scene=scene
r=register('road_slab');random.seed(912)
for i in range(12):
    y=-i*4;left=-4.7+random.uniform(-.3,.25);right=4.7+random.uniform(-.25,.3)
    v=[(left,y,.002),(right,y-.2,.002),(right+random.uniform(-.25,.25),y-3.7,.002),(left+random.uniform(-.25,.25),y-3.8,.002)]
    mesh('Cracked_asphalt_piece',v,[(0,3,2,1)],'asphalt',r,False)
    if i%3!=1:
        box('Faded_road_marking',(random.choice([-.08,.08]),y-1.7,.009),(.07,1.4,.005),'ivory',r,.001)
    for k in range(3):
        x=random.uniform(left,right);beam('Road_fracture',(x,y-1,.007),(x+random.uniform(-.8,.8),y-2.8,.007),.011,'rubber',r,n=6)
export('road_slab')
manifest=json.load(open(ROOT+'/public/assets/manifest.json'));manifest['assets']=list(assets);open(ROOT+'/public/assets/manifest.json','w').write(json.dumps(manifest,indent=2))
bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
result={'road_asset':True,'new_asset_total':len(assets)}
