# Detailed original vehicle/architecture/storytelling kit for six continuous locations.
def tire(parent,x,y,z,r=.34):
    vs=[];fs=[];n=28;m=10
    for i in range(n):
        a=i*math.tau/n
        for j in range(m):
            b=j*math.tau/m;rr=r-.065+.065*math.cos(b);vs.append((x+.095*math.sin(b),y+rr*math.cos(a),z+rr*math.sin(a)))
    for i in range(n):
        for j in range(m):fs.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
    mesh('Treaded_tire',vs,fs,'rubber',parent,True)
    beam('Wheel_hub',(x-.06,y,z),(x+.06,y,z),r*.50,'steel',parent,n=20)
    for i in range(7):
        a=i*math.tau/7;beam('Wheel_spoke',(x,y,z),(x,y+math.cos(a)*r*.65,z+math.sin(a)*r*.65),.014,'steel',parent,n=6)

def vehicle(name,kind):
    r=register(name);truck=kind!='car';w=1.95 if truck else 1.78;l=5.8 if truck else 4.25
    # Beveled polygonal body shell retains actual horizontal hood/doors/trunk proportions.
    outline=[(-w/2+.1,-l/2), (w/2-.1,-l/2),(w/2,-l/2+.2),(w/2,l/2-.2),(w/2-.1,l/2),(-w/2+.1,l/2),(-w/2,l/2-.2),(-w/2,-l/2+.2)]
    vs=[(x,y,z) for z in [.33,.80 if not truck else 1.0] for x,y in outline];fs=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    mesh('Dented_body_shell',vs,fs,'rust' if kind=='car' else 'webbing',r,False)
    cabinY=-.25 if not truck else -1.20;cabinZ=1.02 if not truck else 1.35;roofZ=1.50 if not truck else 2.05
    box('Cabin_floor',(0,cabinY,.84 if not truck else 1.04),(w*.9,1.95,.08),'leather',r,.03)
    box('Roof',(0,cabinY+.15,roofZ),(w*.86,1.84,.08),'rust' if not truck else 'webbing',r,.06)
    for x in [-w*.44,w*.44]:
        for y in [cabinY-.88,cabinY+.06,cabinY+.97]:beam('Window_pillar',(x,y,.80 if not truck else 1.02),(x*.94,y+.12,roofZ),.032,'steel',r,n=8)
        for y in [cabinY-.48,cabinY+.50]:
            box('Door_skin',(x,y,.85 if not truck else 1.05),(.045,.80,.30),'rust' if not truck else 'webbing',r,.025)
            box('Door_handle',(x*1.035,y+.23,1.00 if not truck else 1.20),(.028,.13,.024),'steel',r,.004)
            # A few triangular shards leave a genuine open window.
            mesh('Broken_window',[(x,y-.37,1.02 if not truck else 1.25),(x,y-.25,roofZ-.08),(x,y-.02,1.13 if not truck else 1.4)],[(0,1,2)],'glass',r)
    for x in [-.42,.42]:
        ellipsoid('Front_seat',(x,cabinY+.28,.98 if not truck else 1.18),(.27,.32,.23),'leather',r,n=16)
        box('Seat_back',(x,cabinY+.57,1.19 if not truck else 1.49),(.48,.13,.54),'leather',r,.06)
    box('Dashboard',(0,cabinY-.7,1.03 if not truck else 1.40),(w*.83,.22,.16),'leather',r,.04)
    # Battered hood is slightly lifted, with cooling grille, lamps and bumpers.
    box('Damaged_hood',(0,-l/2+.55,.84 if not truck else 1.16),(w*.9,.97,.07),'rust',r,.035,rot=(.17,0,0))
    for x in [-w*.35,w*.35]:box('Headlamp',(x,-l/2-.025,.66 if not truck else .95),(.27,.045,.15),'ivory',r,.03)
    for x in [-.4,-.27,-.14,0,.14,.27,.4]:box('Grille_slot',(x,-l/2-.024,.66 if not truck else .94),(.055,.03,.22),'rubber',r,.005)
    for y in [-l/2,l/2]:box('Bumper',(0,y,.35 if not truck else .51),(w+.1,.14,.13),'steel',r,.025)
    for x in [-w*.52,w*.52]:
        for y in [-l*.30,l*.31]:tire(r,x,y,.36 if not truck else .48,.35 if not truck else .46)
        for i in range(8):
            y=random.uniform(-l*.4,l*.4);z=random.uniform(.47,.75);beam('Paint_scrape',(x*.96,y,z),(x*.96,y+.18,z+.025),.004,'steel',r,n=6)
    if truck:
        for x in [-.86,.86]:
            for y in [.1,.8,1.5,2.2]:box('Bed_side',(x,y,1.12),(.09,.60,.36),'wood' if kind=='truck' else 'webbing',r,.015)
        if kind=='military':
            for y in [.2,1,1.8,2.5]:
                for x in [-.8,.8]:beam('Canvas_frame',(x,y,1.25),(x*.78,y,2.30),.018,'steel',r,n=8)
                beam('Canvas_crossbar',(-.62,y,2.30),(.62,y,2.30),.018,'steel',r,n=8)
            mesh('Torn_transport_canvas',[(-.85,.1,1.3),(-.62,.1,2.3),(.62,.1,2.3),(.85,.1,1.3),(-.85,2.6,1.3),(-.62,2.6,2.3),(.62,2.6,2.3),(.85,2.6,1.3)],[(0,1,5,4),(1,2,6,5),(2,3,7,6)],'webbing',r,False)
    export(name)
vehicle('car_wreck','car');vehicle('truck_wreck','truck');vehicle('military_truck','military')

r=register('house_ruin')
# Open doors and windows are built from piers/lintels, not painted onto solid cubes.
for x in [-2.8,2.8]:
    for y in [-2.2,2.2]:box('Corner_masonry',(x,y,1.55),(.35,.35,3.1),'concrete',r,.025)
for side in [-1,1]:
    y=side*2.2
    for x in [-2.05,0,2.05]:box('Facade_pier',(x,y,1.32),(.65,.24,2.64),'concrete',r,.025)
    box('Facade_lintel',(0,y,2.75),(5.6,.25,.34),'concrete',r,.025)
    for x in [-1.05,1.05]:box('Window_sill',(x,y,.70),(1.35,.28,.18),'concrete',r,.02)
for side in [-1,1]:
    x=side*2.8
    for y in [-1.65,1.65]:box('Side_wall',(x,y,1.37),(.25,.9,2.74),'concrete',r,.02)
    box('Side_lintel',(x,0,2.75),(.25,4.4,.30),'concrete',r,.02)
    box('Side_sill',(x,0,.70),(.25,2.5,.18),'concrete',r,.02)
for y in [-2,-1,0,1,2]:
    for side in [-1,1]:beam('Burned_roof_rafter',(side*3,y,2.9),(0,y,4.35),.065,'wood',r,n=10)
for i in range(5):
    y=-2+i*.95
    if i!=2:mesh('Broken_roof_sheet',[(0,y,4.38),(3,y,2.96),(3,y+.8,2.96),(0,y+.8,4.38)],[(0,1,2,3)],'rust',r,False)
box('Chimney',(-1.7,1.1,3.65),(.58,.65,1.8),'concrete',r,.025)
for i in range(18):
    box('Loose_brick',(random.uniform(-3.1,3.1),random.uniform(-2.8,2.8),.10),(.30,.15,.16),'concrete',r,.018,rot=(random.random()*.2,0,random.random()*6))
box('Interior_floor',(0,0,.02),(5.4,4.1,.07),'wood',r,.01);box('Fallen_door',(-1,-1,.15),(1.0,1.8,.055),'wood',r,.015,rot=(.1,.04,.5));export('house_ruin')

r=register('warehouse')
for y in [-5,-2.5,0,2.5,5]:
    for side in [-1,1]:
        beam('Steel_column',(side*4.4,y,0),(side*4.4,y,4.2),.10,'rust',r,n=8)
        beam('Roof_truss',(side*4.4,y,4.2),(0,y,5.7),.075,'steel',r,n=8)
    beam('Tie_beam',(-4.4,y,4.2),(4.4,y,4.2),.05,'steel',r,n=8)
for side in [-1,1]:
    for j in range(15):
        y=-5+j*.7
        if j in [5,6,11]:continue
        box('Corrugated_wall',(side*4.4,y,1.85),(.08,.68,3.7),'rust',r,.005)
        for k in range(4):beam('Metal_corrugation',(side*4.44,y-.25+k*.16,.1),(side*4.44,y-.25+k*.16,3.6),.014,'steel',r,n=6)
    for j in range(7):
        y=-4.9+j*1.4
        if j==3 and side==1:continue
        mesh('Torn_metal_roof',[(0,y,5.73),(side*4.5,y,4.2),(side*4.5,y+1.2,4.2),(0,y+1.2,5.73)],[(0,1,2,3)],'rust',r,False)
for x in [-2.8,2.8]:
    box('Warehouse_front_pier',(x,-5,1.8),(3.0,.12,3.6),'concrete',r,.02)
for i in range(6):box('Abandoned_pallet',(random.uniform(-3,3),random.uniform(-4,4),.10),(1.2,.9,.15),'wood',r,.01)
export('warehouse')

r=register('checkpoint')
for side in [-1,1]:
    for row in range(3):
        for i in range(5):ellipsoid('Sandbag',(side*3.9,-1.5+i*.65,.18+row*.27),(.48,.37,.16),'webbing',r,n=16,rings=8)
    beam('Tall_barrier_post',(side*5,0,0),(side*5,0,4.3),.07,'steel',r,n=10)
    box('Guard_shack',(side*6.1,1,1.25),(1.8,1.6,2.5),'webbing',r,.04)
    box('Shack_dark_window',(side*6.1,.18,1.62),(1.2,.02,.62),'rubber',r,.01)
beam('Overhead_cable',(-5,0,4.3),(5,0,4.3),.025,'rubber',r,n=8);box('Quarantine_notice',(0,0,3.9),(2.7,.04,.50),'webbing',r,.015)
for x in [-.8,-.4,0,.4,.8]:box('Warning_marker',(x,-.03,3.90),(.14,.01,.24),'ivory',r,.002)
export('checkpoint')

r=register('camp')
for x,y in [(-2,0),(2,1.1)]:
    v=[(x-1.15,y-1.7,0),(x+1.15,y-1.7,0),(x,y-1.7,1.6),(x-1.15,y+1.7,0),(x+1.15,y+1.7,0),(x,y+1.7,1.6)]
    mesh('Weathered_tent',v,[(0,2,5,3),(2,1,4,5),(3,5,4)],'webbing',r,False)
    for py in [y-1.7,y+1.7]:beam('Tent_ridge_pole',(x,py,0),(x,py,1.6),.018,'steel',r,n=8)
    for sx in [-1,1]:beam('Guy_rope',(x+sx*.75,y-1.6,.8),(x+sx*1.7,y-2.2,0),.003,'leather',r,n=6)
    box('Camp_bed',(x,y,.18),(.75,1.7,.17),'leather',r,.035)
export('camp')

r=register('bridge')
for x in [-4.3,4.3]:
    for y in [-6,-3,0,3,6]:box('Damaged_bridge_post',(x,y,1.0),(.22,.25,2.0),'concrete',r,.03)
    for y in [-4.5,-1.5,1.5,4.5]:
        if not (x>0 and y==1.5):beam('Broken_guardrail',(x,y-1.2,1.05),(x,y+1.2,1.05),.09,'rust',r,n=8)
for y in [-4.8,-2.4,0,2.4,4.8]:box('Cracked_deck',(0,y,-.05),(8.5,2.2,.15),'concrete',r,.04)
export('bridge')
r=register('barrel')
loft('Dented_drum',[(0,0,0,.27,.27),(0,0,.08,.29,.29),(0,0,.32,.28,.28),(0,0,.60,.29,.29),(0,0,.72,.26,.26)],'rust',r,n=24,irregular=.012)
for z in [.12,.58]:loft('Drum_hoop',[(0,0,z,.296,.296),(0,0,z+.022,.296,.296)],'steel',r,n=24)
export('barrel')
# Original alpha particle atlas and cloud panorama authored here for browser effects.
import numpy as np
size=256;yy,xx=np.mgrid[0:size,0:size];u=(xx-size/2)/(size/2);v=(yy-size/2)/(size/2);rad=np.sqrt(u*u+v*v);gen=np.random.default_rng(5)
img=bpy.data.images.new('SR_Smoke_particle',width=size,height=size);a=np.ones((size,size,4),dtype=np.float32);a[:,:,:3]=.7;a[:,:,3]=np.maximum(0,1-rad)**2*(.65+gen.random((size,size))*.35);img.pixels.foreach_set(a.ravel());img.filepath_raw=ROOT+'/public/assets/particle-smoke.png';img.file_format='PNG';img.save();img.pack()
result={'vehicle_variants':3,'ruined_locations':6,'total_new_assets':len(assets)}
