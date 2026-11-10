# Reusable environment kit. Static geometry is merged by material by the game loader.
# A 48000 mm long terrain tile has perfectly aligned, flat path boundaries.
r=register('terrain')
verts=[]; faces=[]; nx=32; ny=32
for j in range(ny+1):
    y=-48*j/ny
    for i in range(nx+1):
        x=-24+48*i/nx
        z=0 if abs(x)<5 else .18*math.sin(x*.8)*math.sin(y*.35)**2
        verts.append((x,y,z-.035))
for j in range(ny):
    for i in range(nx):
        k=j*(nx+1)+i; faces.append((k,k+nx+1,k+nx+2,k+1))  # upward-facing earth normals
mesh('earth_tile',verts,faces,'mud',r,True)
# grass on verge, combined triangles rather than thousands of objects
v=[]; f=[]
for i in range(1800):
    x=random.choice([-1,1])*random.uniform(4.8,23); y=random.uniform(-48,0); h=random.uniform(.13,.6); w=.035
    z=.18*math.sin(x*.8)*math.sin(y*.35)**2
    b=len(v); v.extend([(x-w,y,z),(x+w,y,z),(x+.10,y+.04,z+h)]); f.append((b,b+1,b+2))
mesh('verge_grass',v,f,'grass',r)
# Ruts and puddles sit above the mud, with broken irregular outlines.
for y in [-4,-12,-21,-32,-43]:
    for x in [-1.4,1.5]:
        shape('rain_puddle',(x+random.uniform(-.4,.4),y,-.022),(.5,random.uniform(1,2.2),.018),'glass',r)
export_asset('terrain')

for name,alive in [('tree_dead',False),('tree_pine',True)]:
    r=register(name)
    loft('tapered_trunk',[(0,0,0,.3,.27),(.1,0,1.6,.19,.18),(-.08,.05,3.5,.115,.10),(.1,.07,5.7,.035,.035)],'bark',r,n=9)
    for i in range(11):
        a=i*2.4; z=1.9+i*.29; reach=1.7-i*.07
        end=(math.cos(a)*reach,math.sin(a)*reach,z+.6)
        rod('branch',(0,0,z),end,.08,'bark',r,r2=.015)
        rod('twig',end,(end[0]*1.18,end[1]*1.18,end[2]+.7),.02,'bark',r,r2=.004)
        if alive:
            loft('ragged_pine_tier',[(0,0,z,reach*.85,reach*.85),(.05,0,z+.7,.4,.4),(0,0,z+1.2,.02,.02)],'grass',r,n=9)
    export_asset(name)

r=register('rock'); loft('fractured_stone',[(0,0,0,.6,.42),(.1,0,.28,.7,.4),(-.03,.02,.66,.4,.3),(0,0,.8,.1,.12)],'concrete',r,n=7); export_asset('rock')
r=register('fence')
for x in [-2,0,2]:
    box('split_post',(x,0,.65),(.14,.14,1.3),'wood',r,.01)
for z in [.42,.95]:
    box('weathered_rail',(0,0,z),(4.3,.1,.16),'wood',r,.01)
for i in range(7): rod('barbed_wire',(-2.1,-.035,1.1+i*.015),(2.1,.015,1.14+i*.015),.008,'rust',r)
export_asset('fence')
r=register('barricade')
for x in [-.9,.9]:
    for s in [-1,1]: rod('trestle',(x,s*.4,0),(x,0,1.2),.06,'wood',r)
for z in [.58,.95]:
    box('plank',(0,0,z),(2.3,.14,.26),'wood',r,.02)
    for x in [-.88,.88]: shape('nail',(x,-.075,z),(.017,.008,.017),'steel',r)
export_asset('barricade')
r=register('low_log'); rod('fallen_trunk',(-1.25,0,.33),(1.25,0,.33),.31,'bark',r,r2=.25,n=12)
for x in [-.6,.4]: rod('broken_bough',(x,0,.33),(x+.2,.34,.7),.1,'bark',r,r2=.03)
export_asset('low_log')
r=register('overhead')
for x in [-1.1,1.1]: box('gantry_upright',(x,0,1.25),(.13,.28,2.5),'rust',r)
box('low_beam',(0,0,1.64),(2.4,.4,.65),'rust',r)
box('warning_panel',(0,-.23,1.68),(1.2,.025,.29),'canvas',r)
export_asset('overhead')

for name,med in [('supply_crate',False),('med_crate',True)]:
    r=register(name)
    box('reinforced_container',(0,0,.32),(.8,.56,.59),'olive',r,.06)
    box('lid',(0,0,.65),(.84,.6,.09),'olive',r,.025)
    for x in [-.28,.28]:
        box('steel_latch',(x,-.3,.55),(.07,.035,.15),'steel',r)
        for y in [-.25,.25]: box('corner_reinforcement',(x,y,.33),(.065,.07,.6),'black',r,.01)
    box('handle',(0,-.33,.37),(.23,.025,.06),'steel',r)
    if med:
        box('med_cross',(0,-.29,.30),(.28,.016,.07),'bone',r)
        box('med_cross',(0,-.30,.30),(.07,.016,.28),'bone',r)
    else:
        for x in [-.14,0,.14]: box('ammo_mark',(x,-.293,.28),(.065,.02,.2),'bone',r,.004)
    export_asset(name)

r=register('car_wreck')
# Shaped station-wagon shell, inset windows, battered hood and visible wheel hubs.
loft('bodywork',[(0,0,.32,.88,1.95),(0,0,.65,.94,2.1),(0,0,.91,.85,1.88),(0,.1,1.0,.73,1.65)],'rust',r,n=12)
box('cabin',(0,.15,1.15),(1.55,2.2,.58),'black',r,.18)
box('roof',(0,.25,1.5),(1.5,1.95,.08),'olive',r,.06)
for x in [-.79,.79]:
    for y in [-.47,.5]: box('broken_window',(x,y,1.2),(.025,.74,.36),'glass',r,.02)
    for y in [-1.25,1.23]:
        rod('tire',(x-.14,y,.40),(x+.14,y,.4),.37,'black',r,n=12)
        rod('hub',(x-.15,y,.4),(x+.15,y,.4),.19,'steel',r,n=10)
    box('door_handle',(x,.1,.97),(.04,.19,.035),'steel',r)
box('hood',(0,-1.34,.96),(1.55,1.04,.08),'olive',r,.035).rotation_euler.x=.13
for x in [-.62,.62]: box('headlamp',(x,-2,.7),(.3,.05,.18),'bone',r)
box('bumper',(0,-2.05,.4),(1.85,.13,.13),'steel',r)
for x in [-.4,-.2,0,.2,.4]: box('grille',(x,-2.02,.64),(.055,.035,.22),'black',r,.004)
export_asset('car_wreck')

r=register('farm_ruin')
for x in [-3,3]:
    for y in [-2,2]: box('timber_frame',(x,y,1.65),(.2,.2,3.3),'wood',r)
for x in [-3,3]:
    for y in range(10):
        h=random.uniform(1.7,2.8)
        box('broken_board',(x,-2+y*.43,h/2),(.12,.38,h),'wood',r,.01)
for side in [-1,1]:
    for i in range(5):
        y=-2+i*1.0
        rod('roof_rafter',(side*3.2,y,3.2),(0,y,4.6),.08,'wood',r)
for y in [-1.8,-.6,.6]:
    ob=box('remaining_roof',(1.45,y,3.95),(3.5,.9,.08),'rust',r,.01); ob.rotation_euler.y=.42
export_asset('farm_ruin')
r=register('checkpoint')
for x in [-3,3]:
    for z in [.2,.55,.9]:
        for y in [-1,-.3,.4,1.1]: shape('sandbag',(x,y,z),(.48,.4,.21),'canvas',r)
    rod('watchtower_leg',(x,0,0),(x,0,5),.09,'steel',r)
box('overpass',(0,0,4.9),(7,.28,.33),'steel',r)
box('checkpoint_sign',(0,-.2,4.5),(3,.07,.5),'olive',r)
export_asset('checkpoint')
r=register('settlement_ruin')
for x in [-2.4,2.4]:
    box('ruined_wall',(x,0,1.2),(.26,4,2.4),'concrete',r,.05)
for i in range(8):
    h=random.uniform(.4,2.6); box('broken_end',(-2+i*.56,2,h/2),(.53,.26,h),'concrete',r,.03)
for i in range(9):
    ob=box('rubble',(random.uniform(-2,2),random.uniform(-2,1),.2),(.7,.6,.4),'concrete',r,.04); ob.rotation_euler.z=random.random()*6
export_asset('settlement_ruin')
# Asset-side FX meshes exported before engine implementation.
for name,mat in [('fx_flash','bone'),('fx_smoke','gray'),('fx_blood','blood'),('fx_dust','canvas'),('fx_impact','rust'),('fx_explosion','red')]:
    r=register(name)
    if name=='fx_flash':
        mesh('starburst',[(0,0,0)]+[(math.cos(i*math.pi/6)*(.23 if i%2==0 else .07),0,math.sin(i*math.pi/6)*(.23 if i%2==0 else .07)) for i in range(12)],[(0,i+1,(i+1)%12+1) for i in range(12)],mat,r)
    else: shape(name,(0,0,0),(.08,.08,.08),mat,r)
    export_asset(name)
result={'asset_count':len(assets),'scene_objects':len(scene.objects),'environment_exports':len(assets)-10}
