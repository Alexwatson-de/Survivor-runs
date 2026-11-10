"""Player motion correction from the user's run/walk/jump/slide sprite reference.
The supplied cowboy stays unchanged in shape/material. Replace only player clips.
Blender -Y is forward; units are meters (reference height 1800 mm).
Walk/run: stance feet travel linearly backward by a declared stride, with an IK
knee and flat sole; runtime must advance phase by actual grounded displacement.
Jump: separate takeoff, asymmetric raised/trailing legs, extension and landing.
Slide: low reclined torso, one extended leg and one bent leg, not a squat.
Keep the 0.3 workshop/animations as history; save the correction in a new blend.
"""
import bpy, math, json
from mathutils import Vector, Matrix, Quaternion
ROOT='/Users/softage/Designer Projects/starter/ashfall-run'
RIG_NAME='survivor_cowboy_rig'
# Distance per FULL left+right cycle, not guessed animation playback multipliers.
GAITS={
    'walk': {'stride':1.10,'duration':.82,'stance':.62,'lift':.105},
    'run': {'stride':2.40,'duration':.66,'stance':.40,'lift':.28},
    'sprint': {'stride':3.00,'duration':.56,'stance':.31,'lift':.34},
}
FPS=60

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def reset(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode='QUATERNION';pb.matrix_basis=Matrix.Identity(4)

def orient(rig,name,head,tail):
    # Minimal swing from the rest axis preserves roll; no arbitrary track-quat twist.
    b=rig.data.bones[name];q=(b.tail_local-b.head_local).rotation_difference(Vector(tail)-Vector(head))@b.matrix_local.to_quaternion()
    rig.pose.bones[name].matrix=Matrix.LocRotScale(Vector(head),q,Vector((1,1,1)))
    bpy.context.view_layer.update()

def leg(rig,side,ankle,pole=(0,-1,0),foot_pitch=0):
    thigh=rig.pose.bones['thigh'+side];shin=rig.pose.bones['shin'+side];foot=rig.pose.bones['foot'+side]
    parent=rig.pose.bones['hips'].matrix@rig.data.bones['hips'].matrix_local.inverted()
    hip=parent@rig.data.bones[thigh.name].head_local;target=Vector(ankle)
    l1=rig.data.bones[thigh.name].length;l2=rig.data.bones[shin.name].length;d=target-hip;length=d.length
    reach=l1+l2-.001
    if length>reach:target=hip+d.normalized()*reach;length=reach
    direction=(target-hip).normalized();along=(l1*l1-l2*l2+length*length)/(2*length);radius=math.sqrt(max(.000001,l1*l1-along*along))
    pv=Vector(pole);pv-=direction*pv.dot(direction)
    if pv.length<.001:pv=Vector((0,-1,0))
    knee=hip+direction*along+pv.normalized()*radius
    orient(rig,thigh.name,hip,knee);orient(rig,shin.name,knee,target)
    q=Quaternion((1,0,0),foot_pitch)@rig.data.bones[foot.name].matrix_local.to_quaternion()
    foot.matrix=Matrix.LocRotScale(target,q,Vector((1,1,1)));bpy.context.view_layer.update()
    return (Vector(ankle)-target).length

def turn(rig,bone,axis,angle):
    rest=rig.data.bones[bone].matrix_local.to_quaternion();rig.pose.bones[bone].rotation_quaternion=Quaternion(rest.inverted()@Vector(axis),angle)

def pelvis(rig,z,lean=0):
    rest=rig.data.bones['hips'].matrix_local
    rig.pose.bones['hips'].matrix=Matrix.LocRotScale(Vector((0,0,z)),rest.to_quaternion(),Vector((1,1,1)))
    turn(rig,'spine',(1,0,0),lean);bpy.context.view_layer.update()

_arm_helper=None
def armed(rig):
    # Keep the established hands/socket interface while the lower body is rebuilt.
    global _arm_helper
    if _arm_helper is None:
        ns={};exec(compile(open(ROOT+'/blender/open-world/rig-supplied-models.py').read(),'rig-supplied-models.py','exec'),ns);_arm_helper=ns['arm_ik']
    _arm_helper(rig,'R',(.12,-.43,1.245));_arm_helper(rig,'L',(-.035,-.50,1.31))

def foot_target(phase,gait,side,direction='forward'):
    p=phase%1;d=gait['stance'];span=gait['stride']*d;half=span/2
    x=-.115 if side=='L' else .115
    # During stance, the sole is flat and its backwards velocity exactly cancels
    # the corresponding full-cycle root displacement (stride), including at wrap.
    if p<d:q=-half+gait['stride']*p;z=.13;pitch=0;stance=True
    else:
        u=(p-d)/(1-d);q=half-span*smooth(u);z=.13+gait['lift']*math.sin(math.pi*u)**1.3;pitch=-.38*math.sin(math.pi*u);stance=False
    vectors={'forward':(0,1),'back':(0,-1),'left':(-1,0),'right':(1,0),'fl':(-.7071067812,.7071067812),'fr':(.7071067812,.7071067812),'bl':(-.7071067812,-.7071067812),'br':(.7071067812,-.7071067812)}
    dx,dy=vectors[direction]
    return (x+q*dx,q*dy,z),pitch*(1 if direction=='forward' else .25),stance

def pose_gait(rig,label,phase):
    base=label.split('_')[0];direction=label.split('_')[1] if '_' in label else 'forward';g=GAITS[base];p=phase%1;run=base!='walk'
    # Enough pelvis compression to reach both contact extremes without foot drift.
    z=(.705 if run else .805)+(.018 if run else .009)*math.cos(p*math.tau*2)
    pelvis(rig,z,.17 if run else .055)
    errors=[]
    for side,offset in [('L',0),('R',.5)]:
        target,pitch,stance=foot_target((p+offset)%1,g,side,direction);errors.append(leg(rig,side,target,foot_pitch=pitch))
    turn(rig,'chest',(0,0,1),math.sin(p*math.tau)*(.035 if run else .02));armed(rig)
    return max(errors)

def pose_jump(rig,t):
    # Physical Y lift belongs to the simulation. These poses are relative to it.
    takeoff=smooth(t/.16);tuck=smooth((t-.12)/.20)*(1-smooth((t-.58)/.25));land=smooth((t-.82)/.18)
    pelvis(rig,.81-.055*(1-takeoff)-.10*land,.12+.10*tuck)
    # Raised leading knee and a separate folded trailing leg, not twin forward kicks.
    left=(-.115,-.08-.28*tuck,.13+.40*tuck)
    right=(.115,.05+.20*tuck,.13+.19*tuck)
    leg(rig,'L',left,foot_pitch=-.12*tuck);leg(rig,'R',right,foot_pitch=-.42*tuck)
    armed(rig)

def pose_slide(rig,t):
    # Reference: seated/reclined, one leg leading, the other folded under.
    # Clip is a low pose throughout the physical slide interval, not a 1 s squat.
    pelvis(rig,.145,-.95)
    leg(rig,'L',(-.13,-.75,.14),foot_pitch=.14)
    leg(rig,'R',(.16,-.17,.14),pole=(.4,-1,0),foot_pitch=.05)
    armed(rig)

def pose_land(rig,t):
    a=math.sin(math.pi*t);pelvis(rig,.815-.10*a,.09+.1*a)
    leg(rig,'L',(-.115,-.09,.13));leg(rig,'R',(.115,.05,.13));armed(rig)

def make_review_copy():
    src=bpy.data.objects[RIG_NAME];source_mesh=bpy.data.objects['SR03_Cowboy_GameMesh']
    scene=bpy.data.scenes.new('Survivor Runs - planted player motion');bpy.context.window.scene=scene;scene.render.fps=FPS;scene.unit_settings.system='METRIC'
    root=bpy.data.objects.new('survivor_cowboy_motion',None);scene.collection.objects.link(root)
    rig=src.copy();rig.data=src.data.copy();rig.animation_data_clear();scene.collection.objects.link(rig);rig.parent=root;rig.name='survivor_cowboy_motion_rig'
    ob=source_mesh.copy();ob.data=source_mesh.data.copy();scene.collection.objects.link(ob);ob.parent=rig;ob.name='Cowboy_planted_motion';ob.hide_render=False;ob.hide_set(False)
    for m in ob.modifiers:
        if m.type=='ARMATURE':m.object=rig
    # Side-isolated anatomical skinning, with rigid soles and smooth ankle/knee
    # transitions. No boot inherits the opposite leg or floats toward the shin.
    for v in ob.data.vertices:
        x,y,z=v.co
        if z>=1.0 or abs(x)>.32 and z>.84:continue
        s='L' if x<0 else 'R'
        if z<.16:w={'foot'+s:1}
        elif z<.30:
            a=smooth((z-.16)/.14);w={'foot'+s:1-a,'shin'+s:a}
        elif z<.43:w={'shin'+s:1}
        elif z<.59:
            a=smooth((z-.43)/.16);w={'shin'+s:1-a,'thigh'+s:a}
        elif z<.79:w={'thigh'+s:1}
        else:
            a=smooth((z-.79)/.21);w={'thigh'+s:1-a,'hips':a}
        for vg in ob.vertex_groups:vg.remove([v.index])
        for n,a in w.items():
            if a>0:ob.vertex_groups[n].add([v.index],a,'REPLACE')
    reset(rig);return scene,root,rig,ob

def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:yield curve

def author_clip(scene,rig,label,duration,fn):
    rig.animation_data_create();rig.animation_data.action=None;reset(rig)
    frames=round(duration*FPS);reach=0
    for f in range(frames+1):
        scene.frame_set(f);reset(rig);err=fn(rig,label,f/frames) if label.split('_')[0] in GAITS else fn(rig,f/frames)
        reach=max(reach,err or 0)
        for pb in rig.pose.bones:
            pb.keyframe_insert(data_path='location',frame=f);pb.keyframe_insert(data_path='rotation_quaternion',frame=f)
    action=rig.animation_data.action;action.name='SR031_player_'+label
    for curve in curves(action):
        for k in curve.keyframe_points:k.interpolation='LINEAR'
    track=rig.animation_data.nla_tracks.new();track.name=label;track.strips.new(label,0,action);track.mute=True;rig.animation_data.action=None
    return {'label':label,'frames':frames+1,'duration':frames/FPS,'max_ik_reach_error_mm':reach*1000}

def build_player_motion():
    """Run inside the connector with the 0.3 supplied actor workshop loaded.
    Returns a NEW scene/rig, preserves existing scenes and all original actions.
    Saving the review blend is a separate explicit operation after inspection.
    """
    scene,root,rig,mesh=make_review_copy();rows=[]
    for base,g in GAITS.items():
        directions=['forward'] if base=='sprint' else ['forward','fr','right','br','back','bl','left','fl']
        for direction in directions:
            label=base if direction=='forward' else base+'_'+direction
            rows.append(author_clip(scene,rig,label,g['duration'],pose_gait))
    for label,duration,fn in [('jump',.8,pose_jump),('land',.22,pose_land),('slide',.92,pose_slide)]:rows.append(author_clip(scene,rig,label,duration,fn))
    source=bpy.data.objects[RIG_NAME]
    for label in ['idle','shoot','reload','dodge','stumble','hurt','death']:
        a=source.animation_data.nla_tracks[label].strips[0].action
        tr=rig.animation_data.nla_tracks.new();tr.name=label;strip=tr.strips.new(label,0,a);strip.scale=FPS/30;tr.mute=True
    for label,g in GAITS.items():root['stride_'+label+'_m']=g['stride'];root['stance_'+label]=g['stance']
    root['motion_revision']='0.3.1-foot-contact';root['reference_intent']='Alternating planted walk/run, asymmetric knee-tuck jump and low reclined slide'
    reset(rig);scene.frame_set(0)
    return scene,root,rig,mesh,rows

def export_motion(scene,root,rig):
    bpy.context.window.scene=scene;rig.animation_data.action=None;reset(rig);scene.frame_set(0)
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root]+list(root.children_recursive):o.select_set(True)
    bpy.context.view_layer.objects.active=root
    path=ROOT+'/public/assets/supplied/survivor_cowboy_motion.glb'
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_merge_animation='NLA_TRACK',export_anim_slide_to_zero=True,export_frame_step=1,export_extras=True)
    return path
