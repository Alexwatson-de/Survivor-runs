# Review-only bounded atmospheric volume. Does not alter game exports or user objects.
import bpy
from mathutils import Vector
review=globals().get('review') or bpy.data.scenes.get('ASHFALL • Countryside Review')
ROOT=globals().get('ROOT','/Users/softage/Designer Projects/starter/ashfall-run')
bpy.context.window.scene=review
nt=review.world.node_tree
for link in list(nt.links):
    if link.to_socket==nt.nodes['World Output'].inputs['Volume']: nt.links.remove(link)
# Fog occupies the countryside rather than the entire infinite world.
mat=bpy.data.materials.new('AF_Bounded_morning_mist');mat.use_nodes=True;mat.node_tree.nodes.clear()
out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');vol=mat.node_tree.nodes.new('ShaderNodeVolumePrincipled')
vol.inputs['Density'].default_value=.006;vol.inputs['Color'].default_value=(.64,.71,.65,1)
mat.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
verts=[(x,y,z) for z in [-1,13] for y in [-80,18] for x in [-28,28]]
me=bpy.data.meshes.new('AF_mist_bounds');me.from_pydata(verts,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
o=bpy.data.objects.new('AF_mist_volume',me);review.collection.objects.link(o);me.materials.append(mat)
for ob in review.objects:
    if ob.type=='LIGHT' and ob.data.type=='SUN': ob.data.energy=4
    if ob.type=='LIGHT' and ob.data.type=='AREA': ob.data.energy=2200
review.view_settings.exposure=1
review.render.filepath=ROOT+'/artifacts/blender-countryside-final.png'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/ashfall-asset-workshop.blend')
result={'review_scene':review.name,'render':review.render.filepath,'game_assets_unchanged':True}
