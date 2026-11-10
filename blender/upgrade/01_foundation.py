"""Survivor Runs 0.2 — original PBR/skinned art overhaul in the existing project.
New scenes preserve both the old workshop and any user objects. Dimensions in meters;
reference human height 1820 mm. Authoring direction is -Y; glTF forward becomes +Z.
"""
import bpy, math, random, os, json
from mathutils import Vector
ROOT='/Users/softage/Designer Projects/starter/ashfall-run'
scene=bpy.data.scenes.new('SURVIVOR RUNS • Production Workshop')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.render.engine='BLENDER_EEVEE';scene.render.fps=30
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
random.seed(20261105)
M={}; assets={}; rigs={}; skinparts={}
# Tileable authored albedo/roughness/normal maps. Real glTF PBR maps, not unbaked nodes.
def material(name,color,rough=.8,metal=0,style='cloth'):
    import numpy as np
    size=512;gen=np.random.default_rng(sum((i+1)*ord(c) for i,c in enumerate(name)))
    yy,xx=np.mgrid[0:size,0:size];field=np.zeros((size,size),dtype=np.float32)
    for step,amp in [(64,.14),(32,.09),(16,.055),(4,.025)]:
        grid=gen.random((size//step+1,size//step+1));u=(xx%step)/step;v=(yy%step)/step;u=u*u*(3-2*u);v=v*v*(3-2*v)
        i=xx//step;j=yy//step
        field+=amp*((grid[j,i]*(1-u)+grid[j,i+1]*u)*(1-v)+(grid[j+1,i]*(1-u)+grid[j+1,i+1]*u)*v-.5)
    grain=gen.random((size,size))-.5
    if style=='cloth': detail=(np.sin(xx*math.pi)*0+((xx%4==0)|(yy%4==0))*.025)+grain*.018
    elif style=='fur':detail=np.sin(xx*.16+yy*.8+field*15)*.022+grain*.02
    elif style=='bark':detail=np.sin(xx*.12+field*24)*.08+grain*.025
    elif style=='metal':detail=grain*.04+(gen.random((size,size))>.996)*.13
    else:detail=grain*.035
    height=field+detail
    im=bpy.data.images.new('SR_'+name+'_Albedo',width=size,height=size)
    rgba=np.ones((size,size,4),dtype=np.float32)
    for k,c in enumerate(color):rgba[:,:,k]=np.clip(c*(1+field*1.8+detail),.008,1)
    # Subtle wear patches and pores remain proportional, not periodic contour lines.
    im.pixels.foreach_set(rgba.ravel());im.pack()
    normal=bpy.data.images.new('SR_'+name+'_Normal',width=size,height=size);normal.colorspace_settings.name='Non-Color'
    gy,gx=np.gradient(height);vec=np.stack([-gx*4,-gy*4,np.ones_like(gx)],axis=-1);vec/=np.linalg.norm(vec,axis=-1,keepdims=True)
    rgba[:,:,:3]=vec*.5+.5;normal.pixels.foreach_set(rgba.ravel());normal.pack()
    rm=bpy.data.images.new('SR_'+name+'_Roughness',width=size,height=size);rm.colorspace_settings.name='Non-Color';rv=np.clip(rough+field*.3,.1,1);rgba[:,:,:3]=rv[:,:,None];rm.pixels.foreach_set(rgba.ravel());rm.pack()
    mat=bpy.data.materials.new('SR_'+name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
    for image,socket in [(im,'Base Color'),(rm,'Roughness')]:
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs[socket])
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=normal;nm=mat.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;mat.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    M[name]=mat;return mat
for args in [('skin',(.53,.34,.25),.62,0,'skin'),('infected',(.39,.41,.33),.8,0,'skin'),('ashskin',(.48,.43,.34),.8,0,'skin'),('jacket',(.19,.245,.20)),('parka',(.29,.24,.17)),('denim',(.15,.185,.20)),('leather',(.075,.063,.049)),('webbing',(.27,.29,.22)),('steel',(.26,.28,.29),.42,.8,'metal'),('rust',(.28,.145,.078),.85,.3,'metal'),('red',(.30,.095,.065)),('blood',(.19,.033,.025),.46),('bone',(.65,.58,.40)),('ivory',(.69,.68,.56)),('rubber',(.025,.032,.029)),('fur_tan',(.39,.27,.14),.95,0,'fur'),('fur_dark',(.075,.070,.056),.95,0,'fur'),('fur_grey',(.34,.38,.37),.95,0,'fur'),('fur_cream',(.67,.62,.50),.95,0,'fur'),('wood',(.25,.205,.14),.95,0,'bark'),('bark',(.13,.16,.135),1,0,'bark'),('leaf',(.115,.17,.105),1),('leaf_dead',(.26,.225,.135),1),('earth',(.18,.155,.115),.97,0,'earth'),('concrete',(.31,.32,.29),.95,0,'earth'),('asphalt',(.085,.10,.095),.96,0,'earth'),('glass',(.105,.17,.18),.22,.35,'metal')]:material(*args)

def empty(name,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.parent=parent;o.location=loc;return o

def register(name):
    r=empty(name);assets[name]=r;skinparts[name]=[];return r

def mesh(name,vs,fs,mat,parent=None,smooth=True,uvs=None,weights=None,root=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);o.parent=parent;me.materials.append(M[mat]);uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        poly.use_smooth=smooth
        for li in poly.loop_indices:
            vi=me.loops[li].vertex_index;co=me.vertices[vi].co;uv.data[li].uv=uvs[vi] if uvs else (co.x*.75+co.y*.17,co.z*.9+co.y*.13)
    if weights:
        for bone in set(k for w in weights for k in w):
            vg=o.vertex_groups.new(name=bone)
            for i,w in enumerate(weights):
                if bone in w:vg.add([i],w[bone],'REPLACE')
    if root is not None:skinparts[root].append(o)
    return o

def loft(name,rings,mat,parent=None,n=20,bone=None,root=None,weightfn=None,irregular=0):
    vs=[];uv=[];ws=[]
    for i,(x,y,z,rx,ry) in enumerate(rings):
        for j in range(n):
            a=j*math.tau/n;w=1+irregular*math.sin(j*2.7+i*.91);co=(x+rx*math.cos(a)*w,y+ry*math.sin(a)*w,z);vs.append(co);uv.append((j/n,i/max(1,len(rings)-1)))
            ws.append(weightfn(co) if weightfn else {bone:1} if bone else {})
    fs=[tuple(reversed(range(n)))]
    for i in range(len(rings)-1):
        for j in range(n):fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    fs.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh(name,vs,fs,mat,parent,True,uv,ws if bone or weightfn else None,root)

def ellipsoid(name,loc,radius,mat,parent=None,bone=None,root=None,n=20,rings=10):
    x,y,z=loc;rx,ry,rz=radius;rs=[]
    for i in range(rings+1):
        t=-math.pi/2+math.pi*i/rings;c=max(.012,math.cos(t));rs.append((x,y,z+rz*math.sin(t),rx*c,ry*c))
    return loft(name,rs,mat,parent,n,bone,root)

def beam(name,a,b,r,mat,parent=None,bone=None,root=None,r2=None,n=12):
    a,b=Vector(a),Vector(b);d=b-a;q=d.to_track_quat('Z','Y');vs=[];ws=[];uv=[]
    for i,rad in enumerate([r,r2 if r2 is not None else r]):
        for j in range(n):
            p=a+q@Vector((math.cos(j*math.tau/n)*rad,math.sin(j*math.tau/n)*rad,d.length*i));vs.append(p);ws.append({bone:1} if bone else {});uv.append((j/n,i))
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    return mesh(name,vs,fs,mat,parent,True,uv,ws if bone else None,root)

def box(name,loc,dim,mat,parent=None,bevel=.015,bone=None,root=None,rot=(0,0,0)):
    x,y,z=[v/2 for v in dim];q=__import__('mathutils').Euler(rot).to_matrix();vs=[Vector(loc)+q@Vector((a,b,c)) for c in [-z,z] for b in [-y,y] for a in [-x,x]]
    o=mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat,parent,False,weights=[{bone:1} for _ in vs] if bone else None,root=root)
    if bevel:mod=o.modifiers.new('Rounded worn edges','BEVEL');mod.width=bevel;mod.segments=2
    return o

def armature(name,bones,parent):
    data=bpy.data.armatures.new(name+'_skeleton');rig=bpy.data.objects.new(name+'_rig',data);scene.collection.objects.link(rig);rig.parent=parent
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for bn,h,t,p in bones:
        b=data.edit_bones.new(bn);b.head=h;b.tail=t
        if p:b.parent=data.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT');rigs[name]=rig;return rig

def bind_join(name):
    parts=skinparts[name];bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        o.select_set(True);bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+'_skinned';o.parent=rigs[name]
    mod=o.modifiers.new('Weighted skin deformation','ARMATURE');mod.object=rigs[name];mod.use_deform_preserve_volume=True
    assets[name]['rig_type']='skinned';assets[name]['revision']='0.2';return o

def export(name):
    bpy.context.window.scene=scene;bpy.ops.object.select_all(action='DESELECT')
    for o in [assets[name]]+list(assets[name].children_recursive):o.select_set(True)
    bpy.context.view_layer.objects.active=assets[name]
    bpy.ops.export_scene.gltf(filepath=ROOT+'/public/assets/'+name+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animation_mode='NLA_TRACKS',export_merge_animation='NLA_TRACK',export_animations=True,export_anim_slide_to_zero=True,export_optimize_animation_keep_anim_armature=True,export_extras=True)
result={'scene':scene.name,'pbr_materials':len(M),'texture_size':512,'previous_scenes_preserved':len(bpy.data.scenes)-1}
