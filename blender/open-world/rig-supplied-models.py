"""0.3 supplied-model adaptation, executed in the user's Blender connector.
Preserve originals. Cowboy supplied GLB: simplified working copy, same UV/PBR.
Zombie by piRat/GrimZu CC BY 4.0: working copy, new spatial weights and clips.
Original downloaded files and previous production blend are never overwritten.
Human scale 1800/1820 mm. Blender -Y forward, glTF +Z forward.
"""
import bpy, math, os
from mathutils import Vector, Matrix, Quaternion
ROOT='/Users/softage/Designer Projects/starter/ashfall-run'
scene=bpy.context.scene
scene.render.fps=30
rigs={}; roots={}; meshes={}

def prepare_zombie():
    col=bpy.data.collections['SR03_GrimZu_Zombie'];items=[o for o in col.objects if o.type=='MESH'];copies=[]
    for ob in items:
        o=ob.copy();o.data=ob.data.copy();o.parent=None;scene.collection.objects.link(o)
        o.data.transform(ob.matrix_world);o.matrix_world=Matrix.Identity(4);copies.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in copies:o.select_set(True)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='SR03_Zombie_GameMesh'
    zs=[v.co.z for v in o.data.vertices];lo=min(zs);scale=1.82/(max(zs)-lo)
    for v in o.data.vertices:v.co=Vector((v.co.x*scale,v.co.y*scale,(v.co.z-lo)*scale))
    for ob in col.objects:ob.hide_render=True;ob.hide_set(True)
    return o

def build_rig(name,ob,zombie=False):
    root=bpy.data.objects.new(name,None);scene.collection.objects.link(root);root['source']='user supplied; see SOURCES.md';roots[name]=root
    defs=[('hips',(0,0,.90),(0,0,1.03),None),('spine',(0,0,1.03),(0,0,1.26),'hips'),('chest',(0,0,1.26),(0,0,1.44),'spine'),('neck',(0,0,1.44),(0,-.025,1.51),'chest'),('head',(0,-.025,1.51),(0,-.025,1.78),'neck'),('weapon_socket',(.12,-.49,1.31),(.12,-.75,1.31),'chest')]
    for side,sgn in [('L',-1),('R',1)]:
        sh=(sgn*.20,0,1.39);el=(sgn*.40,-.015,1.15);wr=(sgn*.55,-.025,.96)
        if zombie:sh=(sgn*.19,0,1.36);el=(sgn*.21,-.35,1.25);wr=(sgn*.16,-.62,1.22)
        hip=(sgn*.105,0,.91);kn=(sgn*.115,-.025,.51);an=(sgn*.115,0,.13)
        defs.extend([('upper'+side,sh,el,'chest'),('fore'+side,el,wr,'upper'+side),('hand'+side,wr,Vector(wr)+Vector((0,-.07,-.07)),'fore'+side),('thigh'+side,hip,kn,'hips'),('shin'+side,kn,an,'thigh'+side),('foot'+side,an,(sgn*.115,-.17,.065),'shin'+side)])
    data=bpy.data.armatures.new(name+'_bones');rig=bpy.data.objects.new(name+'_rig',data);scene.collection.objects.link(rig);rig.parent=root
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for n,a,b,p in defs:
        bone=data.edit_bones.new(n);bone.head=a;bone.tail=b
        if p:bone.parent=data.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT');rigs[name]=rig;meshes[name]=ob
    # Bounded four-influence segment-distance weights. Hat/head stay rigid.
    segments=[(n,Vector(a),Vector(b)) for n,a,b,p in defs if n!='weapon_socket']
    for n,a,b in segments:ob.vertex_groups.new(name=n)
    for v in ob.data.vertices:
        co=v.co;x,y,z=co
        if z>1.49 and abs(x)<.29:w=[('head',1)]
        else:
            ds=[]
            for n,a,b in segments:
                if z<.87 and not n.startswith(('thigh','shin','foot')):continue
                if z>1.00 and n.startswith(('thigh','shin','foot')):continue
                if n in ['head','neck'] and z<1.39:continue
                d=b-a;t=max(0,min(1,(co-a).dot(d)/d.length_squared));dist=(co-a-d*t).length
                if n.startswith(('upper','fore','hand')) and abs(x)<.20+max(0,(1.4-z)*.4) and not (zombie and y<-.28):dist+=.50
                ds.append((dist,n))
            near=sorted(ds)[:4];ws=[1/(d+.025)**6 for d,n in near];total=sum(ws);w=[(n,a/total) for (d,n),a in zip(near,ws)]
        for n,weight in w:ob.vertex_groups[n].add([v.index],weight,'REPLACE')
    ob.parent=rig;mod=ob.modifiers.new('SR03 weighted skin','ARMATURE');mod.object=rig
    # Independent runtime textures; preserve the supplied maps instead of atlasing them.
    for mat in ob.data.materials:
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image and max(node.image.size)>1024:
                image=node.image.copy();image.name='SR03_'+image.name;image.scale(1024,1024);image.pack();node.image=image
    return rig

def turn(rig,bone,axis,angle):
    if bone not in rig.pose.bones:return
    rest=rig.data.bones[bone].matrix_local.to_quaternion();rig.pose.bones[bone].rotation_quaternion=Quaternion(rest.inverted()@Vector(axis),angle)

def arm_ik(rig,side,target):
    upper=rig.pose.bones['upper'+side];fore=rig.pose.bones['fore'+side];hand=rig.pose.bones['hand'+side]
    chest=rig.pose.bones['chest'].matrix@rig.data.bones['chest'].matrix_local.inverted();a=chest@rig.data.bones[upper.name].head_local;target=chest@Vector(target)
    l1=upper.length;l2=fore.length;delta=target-a;dist=min(l1+l2-.003,max(.02,delta.length));direction=delta.normalized();target=a+direction*dist
    along=(l1*l1-l2*l2+dist*dist)/(2*dist);radius=math.sqrt(max(.000001,l1*l1-along*along));sgn=-1 if side=='L' else 1
    pole=Vector((sgn*.8,.2,-.7));pole-=direction*pole.dot(direction);pole.normalize();elbow=a+direction*along+pole*radius
    for pb,h,t in [(upper,a,elbow),(fore,elbow,target)]:pb.matrix=Matrix.LocRotScale(h,(t-h).to_track_quat('Y','Z'),Vector((1,1,1)));bpy.context.view_layer.update()
    hand.matrix=Matrix.LocRotScale(target,Vector((0,-1,0)).to_track_quat('Y','Z'),Vector((1,1,1)));bpy.context.view_layer.update()

def animate(name,zombie=False):
    rig=rigs[name];rig.animation_data_create()
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
    clips=[('idle',2),('walk',1.6),('run',.8),('sprint',.6),('shoot',.2),('reload',2),('jump',.9),('slide',1),('dodge',.5),('stumble',.6),('hurt',.5),('death',1.4)] if not zombie else [('idle',2),('walk',1.6),('wander',1.6),('run',.8),('attack',.8),('grab',1),('hurt',.5),('hit_head',.5),('hit_leg',.5),('crawl',1.6),('die',1.5)]
    for label,duration in clips:
        rig.animation_data.action=None;frames=round(duration*30)
        for f in range(0,frames+1,2):
            scene.frame_set(f)
            for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
            t=f/frames;wave=math.sin(t*math.tau);moving=label in ['walk','run','sprint','wander'];amp=.55 if label in ['run','sprint'] else .27
            if moving:
                for side,sgn in [('L',1),('R',-1)]:turn(rig,'thigh'+side,(1,0,0),wave*amp*sgn);turn(rig,'shin'+side,(1,0,0),-max(0,-wave*sgn)*amp*1.7)
            turn(rig,'head',(0,0,1),math.sin(t*math.tau)*.025)
            if label in ['death','die']:
                rig.pose.bones['hips'].location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.75*t));turn(rig,'hips',(1,0,0),1.5*t)
            if label in ['hurt','hit_head','hit_leg','stumble']:turn(rig,'chest',(1,0,0),-.22*math.sin(t*math.pi))
            if label=='jump':
                for side in ['L','R']:turn(rig,'thigh'+side,(1,0,0),-.5*math.sin(t*math.pi));turn(rig,'shin'+side,(1,0,0),-.9*math.sin(t*math.pi))
            if label in ['slide','crawl']:
                rig.pose.bones['hips'].location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.48));turn(rig,'spine',(1,0,0),.8 if zombie else -.35)
                for side in ['L','R']:turn(rig,'thigh'+side,(1,0,0),-1.1);turn(rig,'shin'+side,(1,0,0),-.7)
            bpy.context.view_layer.update()
            if not zombie and label!='death':
                drop=math.sin(t*math.pi)**2 if label=='reload' else 0
                arm_ik(rig,'R',(.12,-.43,1.245));arm_ik(rig,'L',(-.035,-.50+drop*.30,1.31-drop*.31))
                if label=='shoot':turn(rig,'weapon_socket',(1,0,0),-.06*math.sin(t*math.pi))
            elif zombie:
                for side,sgn in [('L',-1),('R',1)]:turn(rig,'upper'+side,(1,0,0),-.15+wave*.2*sgn if moving else -.5*math.sin(t*math.pi) if label in ['attack','grab'] else 0)
            for pb in rig.pose.bones:pb.keyframe_insert(data_path='rotation_quaternion',frame=f);pb.keyframe_insert(data_path='location',frame=f)
        action=rig.animation_data.action;action.name='SR03_'+name+'_'+label;track=rig.animation_data.nla_tracks.new();track.name=label;track.strips.new(label,0,action);track.mute=True;rig.animation_data.action=None
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    scene.frame_set(0)

def export_actor(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [roots[name]]+list(roots[name].children_recursive):o.select_set(True)
    bpy.context.view_layer.objects.active=roots[name]
    path=ROOT+'/public/assets/supplied/'+name+'.glb';os.makedirs(os.path.dirname(path),exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_merge_animation='NLA_TRACK',export_anim_slide_to_zero=True,export_extras=True)
