# Authored skeletal clips with analytic two-bone arm placement and smooth skin weights.
from mathutils import Quaternion, Matrix

def turn(rig,bone,axis,angle):
    if bone not in rig.pose.bones:return
    rest=rig.data.bones[bone].matrix_local.to_quaternion();local=rest.inverted()@Vector(axis)
    rig.pose.bones[bone].rotation_quaternion=Quaternion(local,angle)

def arm_ik(rig,side,target,pole=None):
    upper=rig.pose.bones['upper'+side];fore=rig.pose.bones['fore'+side];hand=rig.pose.bones['hand'+side]
    chest=rig.pose.bones['chest'].matrix@rig.data.bones['chest'].matrix_local.inverted()
    shoulder=chest@rig.data.bones['upper'+side].head_local;target=chest@Vector(target)
    length1=rig.data.bones['upper'+side].length;length2=rig.data.bones['fore'+side].length
    delta=target-shoulder;dist=min(length1+length2-.002,max(.02,delta.length));direction=delta.normalized();target=shoulder+direction*dist
    along=(length1*length1-length2*length2+dist*dist)/(2*dist);radius=math.sqrt(max(.000001,length1*length1-along*along))
    s=-1 if side=='L' else 1;pv=Vector(pole or (s*.8,.3,-1));pv-=direction*pv.dot(direction);pv.normalize();elbow=shoulder+direction*along+pv*radius
    for pb,a,b in [(upper,shoulder,elbow),(fore,elbow,target)]:
        pb.matrix=Matrix.LocRotScale(a,(b-a).to_track_quat('Y','Z'),Vector((1,1,1)))
        bpy.context.view_layer.update()
    hand.matrix=Matrix.LocRotScale(target,Vector((0,-1,0)).to_track_quat('Y','Z'),Vector((1,1,1)))
    bpy.context.view_layer.update()

def pose_human(name,clip,t,duration):
    rig=rigs[name];infected=name.startswith('zombie_');fast=clip in ['run','sprint'];period=.62 if clip=='sprint' else .8 if fast else 1.6
    phase=t*duration*math.tau/period;wave=math.sin(phase)
    root=rig.pose.bones['hips'];root.location=(0,0,0)
    # In-place gait. The runtime is responsible for motion, so there is no root-motion mismatch.
    moving=clip in ['walk','wander','run','sprint','aim','shoot','reload','jump','slide','dodge']
    amp=.68 if fast else .28 if clip in ['walk','wander'] else .42
    if moving and clip not in ['jump','slide']:
        for side,sign in [('L',1),('R',-1)]:
            val=wave*sign;turn(rig,'thigh'+side,(1,0,0),val*amp);turn(rig,'shin'+side,(1,0,0),-max(0,-val)*(.95 if fast else .45));turn(rig,'foot'+side,(1,0,0),max(0,val)*.14)
        worldshift=Vector((0,0,abs(wave)*(.027 if fast else .011)))
        root.location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@worldshift
    turn(rig,'spine',(1,0,0),.08 if not infected else .18)
    turn(rig,'chest',(0,0,1),wave*.025 if moving else math.sin(t*math.tau)*.01)
    turn(rig,'pack',(1,0,0),wave*.025 if moving else 0)
    turn(rig,'head',(0,0,1),math.sin(t*math.tau)*(.06 if clip in ['idle','wander'] else .012))
    if clip=='jump':
        for side in ['L','R']:turn(rig,'thigh'+side,(1,0,0),-.6*math.sin(math.pi*t));turn(rig,'shin'+side,(1,0,0),-1.2*math.sin(math.pi*t))
    if clip=='slide':
        root.location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.48));turn(rig,'spine',(1,0,0),-.35)
        for side in ['L','R']:turn(rig,'thigh'+side,(1,0,0),-1.25);turn(rig,'shin'+side,(1,0,0),-.25)
    if clip=='dodge':turn(rig,'spine',(0,1,0),math.sin(math.pi*t)*.28)
    if clip in ['stumble','hurt','hit_head','hit_leg']:
        turn(rig,'chest',(1,0,0),-.22*math.sin(math.pi*t));turn(rig,'head',(1,0,0),-.30*math.sin(math.pi*t) if clip=='hit_head' else .10*math.sin(math.pi*t))
        if clip=='hit_leg':turn(rig,'thighL',(1,0,0),-.45*math.sin(math.pi*t));turn(rig,'shinL',(1,0,0),-.8*math.sin(math.pi*t))
    if clip in ['die','death','fall']:
        root.location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.74*t));turn(rig,'hips',(1,0,0),1.5*t)
        turn(rig,'thighL',(1,0,0),-.25*t);turn(rig,'shinR',(1,0,0),-.8*t)
    if clip=='crawl':
        root.location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.50));turn(rig,'spine',(1,0,0),1.0);turn(rig,'chest',(1,0,0),.15);turn(rig,'thighL',(1,0,0),-.7);turn(rig,'shinL',(1,0,0),-1.2);turn(rig,'thighR',(1,0,0),-.8-wave*.22);turn(rig,'shinR',(1,0,0),-1.3)
    bpy.context.view_layer.update()
    if not infected and clip not in ['death','fall']:
        # Both wrists reach a common gun socket. Left hand drops to the belt during reload.
        rt=(.12,-.43,1.245);lt=(-.035,-.50,1.31)
        if clip=='reload':
            f=math.sin(math.pi*t)**2;lt=(-.06,-.50+f*.30,1.31-f*.31);turn(rig,'weapon_socket',(0,0,1),f*.13)
        if clip=='shoot':turn(rig,'weapon_socket',(1,0,0),-.045*math.sin(math.pi*t))
        arm_ik(rig,'R',rt);arm_ik(rig,'L',lt)
    elif infected and clip in ['attack','grab','crawl']:
        y=-.55-(.12*math.sin(math.pi*t) if clip!='crawl' else .1);z=1.36 if clip!='crawl' else 1.0
        for side,s in [('L',-1),('R',1)]:arm_ik(rig,side,(s*.12,y,z))
    else:
        for side,s in [('L',1),('R',-1)]:turn(rig,'upper'+side,(1,0,0),-.20+(wave*.18*s if moving else 0));turn(rig,'fore'+side,(1,0,0),-.15)

def pose_dog(name,clip,t,duration):
    rig=rigs[name];wave=math.sin(t*duration*math.tau/.6);moving=clip in ['run','attack','jump','return']
    if moving:
        for side,sgn in [('L',1),('R',-1)]:
            turn(rig,'front'+side,(1,0,0),wave*.62*sgn);turn(rig,'frontlower'+side,(1,0,0),max(0,-wave*sgn)*.6)
            turn(rig,'back'+side,(1,0,0),-wave*.60*sgn);turn(rig,'backlower'+side,(1,0,0),max(0,wave*sgn)*.65)
        rig.pose.bones['hips'].location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,abs(wave)*.025))
    turn(rig,'tail',(0,0,1),math.sin(t*math.tau)*.18);turn(rig,'tailtip',(0,0,1),math.sin(t*math.tau+.5)*.16)
    if clip in ['bark','growl','bite','attack']:turn(rig,'jaw',(1,0,0),abs(math.sin(t*math.tau))*.48);turn(rig,'head',(1,0,0),abs(math.sin(t*math.tau))*.12)
    if clip=='jump':turn(rig,'frontL',(1,0,0),-.7);turn(rig,'frontR',(1,0,0),-.7);turn(rig,'backL',(1,0,0),.5);turn(rig,'backR',(1,0,0),.5)
    if clip=='react':turn(rig,'head',(0,0,1),math.sin(t*math.pi)*.35)
    if clip=='idle':turn(rig,'head',(0,0,1),math.sin(t*math.tau)*.12)
    if clip=='down':rig.pose.bones['hips'].location=rig.data.bones['hips'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.25));turn(rig,'spine',(1,0,0),.15)

def clip(name,label,duration,fn):
    rig=rigs[name];rig.animation_data_create();rig.animation_data.action=None
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
    frames=max(6,round(duration*30))
    for f in range(0,frames+1,2):
        scene.frame_set(f)
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
        fn(name,label,f/frames,duration)
        for pb in rig.pose.bones:
            pb.keyframe_insert(data_path='rotation_quaternion',frame=f);pb.keyframe_insert(data_path='location',frame=f)
    a=rig.animation_data.action;a.name=label;tr=rig.animation_data.nla_tracks.new();tr.name=label;tr.strips.new(label,0,a);tr.mute=True;rig.animation_data.action=None
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)

for name in list(rigs):
    if name.startswith('dog_'):seq=[('idle',2),('run',.6),('return',.6),('bark',.8),('growl',1),('bite',.5),('attack',.6),('jump',.7),('react',.6),('down',2)];fn=pose_dog
    elif name.startswith('survivor_'):seq=[('idle',2),('walk',1.6),('run',.8),('sprint',.62),('aim',1.6),('shoot',.2),('reload',2),('jump',.9),('slide',1),('dodge',.6),('stumble',.7),('hurt',.5),('death',1.4)];fn=pose_human
    else:seq=[('idle',2),('wander',1.6),('walk',1.6),('run',.8),('attack',.8),('grab',1.2),('hurt',.5),('hit_head',.4),('hit_leg',.6),('stumble',.7),('fall',1),('crawl',1.6),('die',1.4)];fn=pose_human
    for label,duration in seq:clip(name,label,duration,fn)
    assets[name].location=(0,0,0);export(name)
scene.frame_set(0)
result={'animated_skinned_assets':len(rigs),'clips':sum(len(r.animation_data.nla_tracks) for r in rigs.values()),'exported_assets':list(assets)}
