# Match both ends of reusable terrain, including verge height and rut phase.
# Global track curvature is applied by the game; native section boundaries stay watertight.
bpy.context.window.scene=scene
for ob in assets['terrain'].children_recursive:
    if ob.type!='MESH' or not ob.name.startswith('Irregular_earth'):continue
    for vertex in ob.data.vertices:
        x=vertex.co.x;s=-vertex.co.y;outside=max(0,min(1,(abs(x)-5.8)/7));z=outside*(.45*math.sin(x*.32)*math.sin(s*math.tau/48)**2+.19*math.cos(s*math.tau/48+x*.2))
        if abs(x)<5.8:z-=.022*math.sin(s*math.tau/48*3)**2*(math.exp(-((x-1.2)/.28)**2)+math.exp(-((x+1.4)/.32)**2))
        vertex.co.z=z-.035
    ob.data.update()
export('terrain')
bpy.ops.export_scene.gltf(filepath=ROOT+'/public/assets/runtime/terrain.gltf',export_format='GLTF_SEPARATE',export_texture_dir='textures',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_extras=True)
bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
result={'terrain_edges':'matched periodic height and ruts','runtime_reexported':True}
