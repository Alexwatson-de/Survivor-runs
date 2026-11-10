# Named action clips exported from the real Blender articulated hierarchies.
def animate(name,clip,duration,pose):
    js=rigs[name]; base={k:(o.location.copy(),o.rotation_euler.copy()) for k,o in js.items()}
    for o in js.values():
        o.animation_data_create(); o.animation_data.action=None
    frames=max(12,int(duration*24))
    for f in range(0,frames+1,2):
        t=f/frames
        for k,o in js.items(): o.location=base[k][0]; o.rotation_euler=base[k][1]
        pose(js,t)
        for o in js.values():
            o.keyframe_insert(data_path='rotation_euler',frame=f)
            o.keyframe_insert(data_path='location',frame=f)
    for k,o in js.items():
        ad=o.animation_data; a=ad.action; a.name=name+'_'+clip+'_'+k
        track=ad.nla_tracks.new(); track.name=clip; track.strips.new(clip,0,a); track.mute=True
        ad.action=None; o.location=base[k][0]; o.rotation_euler=base[k][1]

def humanpose(clip,zombie=False):
    def pose(j,t):
        cycle=math.sin(t*math.tau); opp=-cycle
        gait=clip in ['run','walk']
        j['armL'].rotation_euler.x=-1.1 if not zombie else -1.25
        j['armR'].rotation_euler.x=-1.0 if not zombie else -1.0
        j['foreL'].rotation_euler.x=-.5; j['foreR'].rotation_euler.x=-.75
        j['armL'].rotation_euler.z=-.3; j['armR'].rotation_euler.z=.25
        if gait:
            amp=.8 if clip=='run' else .35
            j['thighL'].rotation_euler.x=cycle*amp; j['thighR'].rotation_euler.x=opp*amp
            j['shinL'].rotation_euler.x=max(0,-cycle)*1.2; j['shinR'].rotation_euler.x=max(0,cycle)*1.2
            j['hips'].location.z+=abs(cycle)*(.065 if clip=='run' else .02)
            j['spine'].rotation_euler.x=.13 if clip=='run' else .05
            j['head'].rotation_euler.z=cycle*.04
            if zombie:
                j['armL'].rotation_euler.x+=cycle*.22; j['armR'].rotation_euler.x-=cycle*.2
        if clip=='shoot': j['spine'].rotation_euler.x=-.11*math.sin(math.pi*t); j['armR'].rotation_euler.x-=.19*math.sin(math.pi*t)
        if clip=='reload': j['armL'].rotation_euler.x=-1.6+math.sin(t*math.pi)*.9; j['foreR'].rotation_euler.x=-1.5*math.sin(math.pi*t)
        if clip=='jump':
            j['thighL'].rotation_euler.x=-.8*math.sin(t*math.pi); j['thighR'].rotation_euler.x=-.5*math.sin(t*math.pi)
            j['shinL'].rotation_euler.x=1.4*math.sin(t*math.pi); j['shinR'].rotation_euler.x=1.2*math.sin(t*math.pi)
        if clip=='slide':
            j['hips'].location.z-=.56; j['spine'].rotation_euler.x=-.55
            j['thighL'].rotation_euler.x=-1.5; j['thighR'].rotation_euler.x=-1.4
            j['shinL'].rotation_euler.x=.4; j['shinR'].rotation_euler.x=.5
        if clip=='attack':
            j['armL'].rotation_euler.x=-1.4-math.sin(t*math.pi)*.9; j['armR'].rotation_euler.x=-1.4-math.sin(t*math.pi)*.9
            j['spine'].rotation_euler.x=.3*math.sin(t*math.pi)
        if clip in ['death','die']:
            j['hips'].location.z-=.7*t; j['spine'].rotation_euler.x=-1.45*t
            j['thighL'].rotation_euler.x=-.5*t; j['thighR'].rotation_euler.x=.4*t
    return pose
for name in list(rigs):
    if name.startswith('dog_'): continue
    zs=name.startswith('zombie_')
    for clip,d in ([('idle',2),('walk',1.4),('run',.7),('attack',.75),('die',1)] if zs else [('idle',2),('run',.7),('shoot',.22),('reload',1.8),('jump',.9),('slide',.9),('death',1.2)]):
        animate(name,clip,d,humanpose(clip,zs))

def dogpose(clip):
    def pose(j,t):
        s=math.sin(t*math.tau)
        j['tail'].rotation_euler.z=s*.2
        if clip in ['run','attack','jump']:
            for key,sign in [('frontL',1),('frontR',-1),('backL',-1),('backR',1)]: j[key].rotation_euler.x=s*.8*sign
            j['body'].location.z+=abs(s)*.075
        if clip in ['bark','bite','attack']:
            j['jaw'].rotation_euler.x=abs(s)*.55; j['head'].rotation_euler.x=-.15+abs(s)*.18
        if clip=='jump': j['body'].location.z+=math.sin(math.pi*t)*.3
        if clip=='react': j['body'].rotation_euler.z=s*.16; j['head'].rotation_euler.z=s*.4
        if clip=='idle': j['head'].rotation_euler.z=s*.15
    return pose
for name in ['dog_shepherd','dog_husky']:
    for clip,d in [('run',.55),('bark',.8),('attack',.65),('bite',.5),('jump',.7),('idle',2),('react',.8)]: animate(name,clip,d,dogpose(clip))

# Weapons face -Y, with separate bolt/magazine nodes for firing/reload.
for name,kind in [('weapon_pistol','pistol'),('weapon_shotgun','shotgun'),('weapon_rifle','rifle')]:
    r=register(name); length={'pistol':.23,'shotgun':.88,'rifle':.73}[kind]
    box('receiver',(0,0,0),(.065,.22,.09),'steel',r,.012)
    box('grip',(0,.055,-.09),(.055,.065,.16),'black',r,.015).rotation_euler.x=-.22
    bolt=empty(name+'_bolt',r); mag=empty(name+'_magazine',r)
    box('slide',(0,-.01,.045),(.07,.24,.035),'steel',bolt,.008)
    rod('barrel',(0,-.10,.025),(0,-length,.025),.022 if kind!='shotgun' else .026,'steel',r,n=12)
    rod('barrel_bore',(0,-length-.001,.025),(0,-length-.009,.025),.014,'black',r,n=12)
    for y in [-.10,.09]: box('iron_sights',(0,y,.08),(.02,.025,.026),'black',r,.003)
    # Trigger guard, visible trigger, pins, ribbed handguard and magazine.
    for x in [-.035,.035]: box('trigger_guard',(x,-.035,-.08),(.012,.11,.015),'steel',r,.004)
    box('trigger',(0,-.025,-.055),(.012,.018,.055),'steel',r,.004)
    if kind!='pistol':
        box('stock',(0,.24,-.018),(.075,.31,.12),'wood' if kind=='shotgun' else 'black',r,.025)
        box('butt',(0,.4,-.02),(.09,.035,.17),'black',r,.01)
        for i in range(9): box('handguard_rib',(0,-.16-i*.03,.005),(.082,.018,.085),'wood' if kind=='shotgun' else 'black',r,.006)
    if kind=='rifle':
        box('curved_mag',(0,-.055,-.15),(.055,.10,.23),'black',mag,.015).rotation_euler.x=.17
        rod('optic',(0,-.025,.12),(0,-.16,.12),.035,'black',r)
    else: box('magazine',(0,.05,-.13),(.045,.055,.065),'steel',mag,.005)
    rigs[name]={'bolt':bolt,'mag':mag}
    def wp(clip):
        def pose(j,t):
            if clip=='fire': j['bolt'].location.y=.035*math.sin(math.pi*t)
            else: j['mag'].location.z=-.24*math.sin(math.pi*t); j['mag'].rotation_euler.x=.25*math.sin(math.pi*t)
        return pose
    animate(name,'fire',.2,wp('fire')); animate(name,'reload',1.8,wp('reload'))
# Reset layout for origin-based standalone exports.
for name,r in assets.items():
    r.location=(0,0,0)
    if name.startswith(('survivor','zombie','dog','weapon')): export_asset(name)
result={'animated_assets':len(rigs),'nla_tracks':sum(len(o.animation_data.nla_tracks) for js in rigs.values() for o in js.values()),'exported':len(assets)}
