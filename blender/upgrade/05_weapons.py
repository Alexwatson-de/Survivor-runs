# Six original firearms, separate moving bolt/magazine/pump/cylinder, modeled bores,
# trigger guards, sights, grip ribs, stocks, ejection slots and sling fittings.
from mathutils import Euler

def weapon_animation(root,name,kind):
    moving=[o for o in root.children_recursive if o.type=='EMPTY' and 'moving' in o.name]
    for label,duration in [('fire',.20),('reload',2.4)]:
        for o in moving:o.animation_data_create();o.animation_data.action=None
        frames=round(duration*30)
        for f in range(0,frames+1,2):
            t=f/frames
            for o in moving:
                o.location=(0,0,0);o.rotation_euler=(0,0,0)
                if 'bolt' in o.name:o.location.y=.035*math.sin(math.pi*t) if label=='fire' else .04*max(0,math.sin((t-.65)*math.pi*3))
                if 'mag' in o.name and label=='reload':o.location.z=-.27*math.sin(math.pi*t)**2;o.rotation_euler.x=.13*math.sin(math.pi*t)
                if 'pump' in o.name:o.location.y=.09*math.sin(math.pi*t) if label=='fire' else .02*math.sin(t*math.tau)
                if 'cylinder' in o.name:o.rotation_euler.y=(math.pi/3*t if label=='fire' else math.tau*t);o.location.x=.07*math.sin(math.pi*t) if label=='reload' else 0
                o.keyframe_insert(data_path='location',frame=f);o.keyframe_insert(data_path='rotation_euler',frame=f)
        for o in moving:
            action=o.animation_data.action;action.name=label;track=o.animation_data.nla_tracks.new();track.name=label;track.strips.new(label,0,action);track.mute=True;o.animation_data.action=None;o.location=(0,0,0);o.rotation_euler=(0,0,0)

for kind in ['pistol','revolver','shotgun','rifle','smg','hunting']:
    name='weapon_'+kind;r=register(name)
    bolt=empty(name+'_moving_bolt',r);mag=empty(name+'_moving_mag',r)
    length={'pistol':.19,'revolver':.27,'shotgun':.76,'rifle':.61,'smg':.34,'hunting':.80}[kind]
    long=kind in ['rifle','shotgun','hunting']
    box('Machined_receiver',(0,0,0),(.055,.21,.070),'steel',r,.010)
    box('Grip_frame',(0,.042,-.075),(.047,.061,.125),'leather',r,.012,rot=(-.18,0,0))
    box('Grip_cap',(0,.054,-.137),(.05,.065,.017),'rubber',r,.005)
    for x in [-.026,.026]:
        for z in [-.09,-.065,-.04]:beam('Grip_checkering',(x,.012,z),(x,.072,z+.015),.002,'webbing',r,n=6)
        for y in [-.07,.06]:ellipsoid('Receiver_pin',(x,y,-.008),(.004,.004,.004),'steel',r,n=10,rings=6)
    # Open trigger guard is a rectangular loop of rounded rails, not a solid block.
    for x in [-.024,.024]:
        beam('Guard_rail',(x,-.055,-.045),(x,-.035,-.105),.004,'steel',r,n=8)
        beam('Guard_rail',(x,-.035,-.105),(x,.018,-.105),.004,'steel',r,n=8)
    beam('Trigger',(0,-.024,-.035),(0,-.014,-.075),.004,'steel',r,n=8)
    beam('Barrel',(0,-.10,.017),(0,-length,.017),.018 if kind!='shotgun' else .024,'steel',r,n=20)
    beam('Bore',(0,-length-.001,.017),(0,-length-.006,.017),.010 if kind!='shotgun' else .017,'rubber',r,n=20)
    if kind=='pistol':
        box('Slide',(0,-.006,.043),(.062,.225,.033),'steel',bolt,.006)
        for i in range(8):box('Slide_serration',(.032,.045+i*.006,.043),(.003,.002,.023),'rubber',bolt,.0005)
        box('Magazine',(0,.043,-.14),(.039,.051,.06),'steel',mag,.005)
    elif kind=='revolver':
        cyl=empty(name+'_moving_cylinder',r)
        beam('Cylinder',(0,-.055,.014),(0,.035,.014),.042,'steel',cyl,n=24)
        for i in range(6):
            a=i*math.tau/6;x=math.cos(a)*.029;z=.014+math.sin(a)*.029
            beam('Chamber_flute',(x,-.058,z),(x,.038,z),.009,'rubber',cyl,n=10)
        beam('Hammer',(0,.085,.05),(0,.11,.07),.009,'steel',r,n=8)
    else:
        box('Ejection_port',(.029,-.02,.015),(.004,.068,.022),'rubber',r,.002)
        box('Charging_handle',(.041,.025,.025),(.025,.025,.018),'steel',bolt,.003)
        if long:
            # Sculpted stock has neck, cheek piece, shoulder pad and sling swivel.
            outline=[(.10,.025),(.20,.05),(.38,.055),(.40,-.10),(.32,-.12),(.18,-.07),(.10,-.04)];nv=len(outline)
            stockvs=[(x,y,z) for x in [-.034,.034] for y,z in outline];stockfs=[tuple(reversed(range(nv))),tuple(range(nv,2*nv))]+[(i,(i+1)%nv,(i+1)%nv+nv,i+nv) for i in range(nv)]
            mesh('Contoured_stock',stockvs,stockfs,'wood' if kind in ['shotgun','hunting'] else 'leather',r,True)
            box('Butt_pad',(0,.39,-.028),(.078,.04,.16),'rubber',r,.010)
            box('Cheek_piece',(0,.29,.045),(.065,.15,.028),'leather',r,.008)
        else:
            for x in [-.025,.025]:beam('Folding_stock',(x,.10,0),(x,.28,-.01),.007,'steel',r,n=8)
            box('Stock_end',(0,.28,-.015),(.06,.018,.10),'rubber',r,.006)
        guard=empty(name+'_moving_pump',r) if kind=='shotgun' else r
        for i in range(10):
            y=-.13-i*(.025 if long else .014);box('Handguard_rib',(0,y,.008),(.071,.018,.063),'wood' if kind in ['shotgun','hunting'] else 'leather',guard,.004)
        if kind in ['rifle','smg']:
            box('Detachable_magazine',(0,-.04,-.12),(.045,.065,.19 if kind=='rifle' else .23),'leather',mag,.010,rot=(.14,0,0))
            for z in [-.07,-.10,-.13,-.16]:box('Magazine_rib',(.024,-.04,z),(.003,.056,.004),'steel',mag,.001)
        if kind in ['hunting','rifle']:
            for y in [.025,-.12]:box('Optic_mount',(0,y,.075),(.031,.025,.045),'steel',r,.004)
            beam('Scope',(0,.09,.12),(0,-.22,.12),.025,'leather',r,n=24)
            beam('Objective',(0,-.22,.12),(0,-.265,.12),.038,'steel',r,n=24)
            beam('Lens',(0,-.267,.12),(0,-.270,.12),.032,'glass',r,n=24)
            beam('Elevation_turret',(0,-.06,.13),(0,-.06,.167),.013,'steel',r,n=16)
        if kind=='shotgun':beam('Magazine_tube',(0,-.08,-.035),(0,-.59,-.035),.017,'steel',r,n=16)
    for y in [-length+.035,.075]:box('Iron_sight',(0,y,.075),(.012,.013,.022),'rubber',r,.002)
    r['muzzle_y']=-length;r['family']=kind;r['revision']='0.2'
    weapon_animation(r,name,kind);export(name)
result={'weapon_families':6,'weapon_assets':[n for n in assets if n.startswith('weapon_')]}
