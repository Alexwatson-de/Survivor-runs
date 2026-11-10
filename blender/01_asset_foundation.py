"""ASHFALL RUN original asset workshop. Run in the live Blender connector.
Preserves the user's existing scene; creates a separate asset scene.
Blender authored in meters; human height 1780 mm, lanes 3000 mm apart.
Characters are shaped ring-loft meshes with articulated node rigs, not primitive stand-ins.
"""
import bpy, math, random, os, json
from mathutils import Vector
ROOT = globals().get('ROOT', '/Users/softage/Designer Projects/starter/ashfall-run')
os.makedirs(ROOT+'/public/assets', exist_ok=True)
os.makedirs(ROOT+'/artifacts', exist_ok=True)
scene = bpy.data.scenes.new('ASHFALL • Asset Workshop')
bpy.context.window.scene = scene
scene.unit_settings.system='METRIC'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.fps=24
random.seed(41)
M={}
# Packed albedo maps carry subtle wear into glTF, unlike unbaked procedural shaders.
def material(name, color, rough=.85, metal=0):
    m=bpy.data.materials.new('AF_'+name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    im=bpy.data.images.new('AF_'+name+'_wear', width=128, height=128)
    rng=random.Random(name); pixels=[]
    for y in range(128):
        for x in range(128):
            noise=rng.uniform(.82,1.12)*(1-.08*math.sin(x*.47)*math.sin(y*.31))
            if rng.random()<.018: noise*=.48
            pixels.extend([min(1,c*noise) for c in color]+[1])
    im.pixels=pixels; im.pack()
    tex=m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=im
    m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    m.diffuse_color=(*color,1); M[name]=m; return m
for args in [('olive',(.24,.28,.18)),('canvas',(.42,.36,.23)),('denim',(.14,.19,.22)),('skin',(.53,.34,.24)),('dead',(.39,.45,.35)),('pale',(.5,.49,.39)),('blood',(.21,.035,.028)),('black',(.045,.052,.048)),('steel',(.23,.27,.27),.38,.75),('rust',(.32,.13,.065),.9,.35),('wood',(.24,.19,.12)),('bark',(.16,.17,.135)),('mud',(.16,.13,.09)),('grass',(.21,.24,.12)),('concrete',(.34,.34,.29)),('bone',(.75,.69,.49)),('tan',(.47,.3,.13)),('fur',(.13,.11,.08)),('gray',(.37,.4,.37)),('red',(.54,.17,.08)),('glass',(.15,.25,.26),.22,.25)]: material(*args)
assets={}; rigs={}
def empty(name, parent=None, loc=(0,0,0)):
    o=bpy.data.objects.new(name,None); scene.collection.objects.link(o); o.parent=parent; o.location=loc; return o

def mesh(name,verts,faces,mat,parent=None,smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); scene.collection.objects.link(o); o.parent=parent
    o.data.materials.append(M[mat]); uv=me.uv_layers.new(name='SurfaceUV')
    for p in me.polygons:
        p.use_smooth=smooth
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(v.x*.7+v.y*.3,v.z*.7+v.y*.3)
    return o

def loft(name,rings,mat,parent=None,n=12):
    # rings: local x,y,z, width radius, depth radius; ellipsoid cross sections.
    vs=[]
    for x,y,z,rx,ry in rings:
        for j in range(n):
            a=j*math.tau/n; vs.append((x+rx*math.cos(a),y+ry*math.sin(a),z))
    fs=[tuple(reversed(range(n)))]
    for i in range(len(rings)-1):
        for j in range(n): fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    fs.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh(name,vs,fs,mat,parent,True)

def box(name,loc,dim,mat,parent=None,bevel=.025):
    x,y,z=[v/2 for v in dim]
    vs=[(a,b,c) for c in [-z,z] for b in [-y,y] for a in [-x,x]]
    o=mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat,parent)
    o.location=loc
    if bevel:
        mod=o.modifiers.new('Manufactured edge wear','BEVEL'); mod.width=bevel; mod.segments=2
    return o

def rod(name,a,b,r,mat,parent=None,r2=None,n=8):
    a,b=Vector(a),Vector(b); d=b-a
    o=loft(name,[(0,0,0,r,r),(0,0,d.length,r2 or r,r2 or r)],mat,parent,n)
    o.location=a; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def shape(name,loc,scale,mat,parent=None):
    x,y,z=loc; rx,ry,rz=scale
    return loft(name,[(x,y,z-rz,.02*rx,.02*ry),(x,y,z-rz*.75,rx*.67,ry*.67),(x,y,z-rz*.3,rx*.95,ry*.95),(x,y,z+rz*.3,rx,ry),(x,y,z+rz*.75,rx*.7,ry*.7),(x,y,z+rz,.05*rx,.05*ry)],mat,parent)

def descendants(root): return [root]+list(root.children_recursive)
def register(name):
    r=empty(name); assets[name]=r; return r

def export_asset(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in descendants(assets[name]): o.select_set(True)
    bpy.context.view_layer.objects.active=assets[name]
    bpy.ops.export_scene.gltf(filepath=ROOT+'/public/assets/'+name+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_anim_slide_to_zero=True,export_merge_animation='NLA_TRACK',export_optimize_animation_size=False,export_optimize_animation_keep_anim_object=True,export_extras=True)

result={'scene':scene.name,'materials':len(M),'original_scene_preserved':bpy.data.scenes.get('Scene') is not None}
