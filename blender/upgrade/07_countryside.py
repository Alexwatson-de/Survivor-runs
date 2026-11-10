# Organic forest kit and irregular terrain: no stacked cone trees or paired fence rows.
# Geometry and materials are authored in Blender and exported for instancing/pooling.
def foliage(name,parent,centers,mat='leaf',count=34,size=.38):
    vs=[];fs=[];uv=[];gen=random.Random(name)
    for c,spread in centers:
        for _ in range(count):
            p=Vector(c)+Vector((gen.uniform(-spread,spread),gen.uniform(-spread,spread),gen.uniform(-spread*.6,spread*.6)))
            axis=Vector((gen.uniform(-1,1),gen.uniform(-1,1),gen.uniform(-.2,1))).normalized();side=axis.cross(Vector((0,0,1)))
            if side.length<.1:side=Vector((1,0,0))
            side.normalize();length=size*gen.uniform(.55,1.4);width=length*.28;b=len(vs)
            vs.extend([p-axis*length*.5,p-side*width,p+Vector((0,0,.025)),p+side*width,p+axis*length*.5]);uv.extend([(0,.5),(.5,0),(.5,.5),(.5,1),(1,.5)])
            fs.extend([(b,b+1,b+2),(b+1,b+4,b+2),(b+4,b+3,b+2),(b+3,b,b+2)])
    return mesh(name,vs,fs,mat,parent,True,uv)

for name,leafy in [('tree_oak',True),('tree_dead',False)]:
    r=register(name);gen=random.Random(82 if leafy else 89);height=gen.uniform(7.5,9)
    rings=[]
    for i in range(12):
        z=height*i/11;rad=.34*(1-i/12)**1.3+.015;rings.append((math.sin(i*.5)*.12,math.cos(i*.4)*.10,z,rad,rad*.86))
    loft('Twisted_bark_trunk',rings,'bark',r,n=16,irregular=.10)
    crowns=[]
    for i in range(14):
        a=i*2.39;z=2.3+i*.31;reach=gen.uniform(1.4,2.8)*(1-i*.025);end=Vector((math.cos(a)*reach,math.sin(a)*reach,z+gen.uniform(.7,1.5)))
        mid=Vector((end.x*.54,end.y*.54,z+.2));beam('Main_branch',(0,0,z),mid,.095*(1-i*.035),'bark',r,r2=.055,n=12);beam('Bent_branch',mid,end,.055,'bark',r,r2=.015,n=10)
        for j in range(3):
            twig=end+Vector((gen.uniform(-.7,.7),gen.uniform(-.7,.7),gen.uniform(.3,.9)));beam('Forked_twig',end,twig,.015,'bark',r,r2=.003,n=7)
            if leafy:crowns.append((twig,.68))
        if not leafy and i%3==0:crowns.append((end,.20))
    foliage('Leaf_canopy' if leafy else 'Dead_remaining_leaves',r,crowns,'leaf' if leafy else 'leaf_dead',count=16 if leafy else 5,size=.36 if leafy else .18)
    for i in range(5):
        a=i*math.tau/5;beam('Surface_roots',(0,0,.11),(math.cos(a)*.8,math.sin(a)*.8,.015),.12,'bark',r,r2=.015,n=10)
    export(name)
    # A real simplified export for distant canopy silhouettes.
    lodname=name+'_lod';lod=register(lodname)
    for ob in list(r.children):
        dup=ob.copy();dup.data=ob.data.copy();dup.parent=lod;scene.collection.objects.link(dup);mod=dup.modifiers.new('Distance budget','DECIMATE');mod.ratio=.30
    export(lodname)

r=register('bush')
for i in range(7):
    a=i*2.4;end=(math.cos(a)*.6,math.sin(a)*.6,random.uniform(.5,1.1));beam('Shrub_stem',(0,0,0),end,.018,'bark',r,r2=.004,n=7)
foliage('Shrub_leaves',r,[((0,0,.7),.65)],'leaf',count=115,size=.27);export('bush')
r=register('grass_clump');vs=[];fs=[];uv=[]
for i in range(48):
    a=random.random()*math.tau;x=random.uniform(-.35,.35);y=random.uniform(-.35,.35);h=random.uniform(.18,.65);w=random.uniform(.008,.022);dx=math.cos(a)*w;dy=math.sin(a)*w;b=len(vs)
    vs.extend([(x-dx,y-dy,0),(x+dx,y+dy,0),(x+.07+dx,y+.03+dy,h*.65),(x+.07-dx,y+.03-dy,h*.65),(x+.10,y+.04,h)]);uv.extend([(0,0),(1,0),(1,.6),(0,.6),(.5,1)]);fs.extend([(b,b+1,b+2,b+3),(b+3,b+2,b+4)])
mesh('Bent_grass_blades',vs,fs,'leaf_dead',r,True,uv);export('grass_clump')

r=register('terrain');vs=[];fs=[];uv=[];nx=40;ny=40
for j in range(ny+1):
    s=48*j/ny
    for i in range(nx+1):
        x=-30+60*i/nx;outside=max(0,min(1,(abs(x)-5.8)/7));z=outside*(.45*math.sin(x*.32)*math.sin(s*math.tau/48)**2+.19*math.cos(s*math.tau/48+x*.2))
        # Shallow interrupted ruts lie in the usable track, never a clean flat running strip.
        if abs(x)<5.8:z-=.022*math.sin(s*math.tau/48*3)**2*(math.exp(-((x-1.2)/.28)**2)+math.exp(-((x+1.4)/.32)**2))
        vs.append((x,-s,z-.035));uv.append(((x+30)/60,s/48))
for j in range(ny):
    for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+nx+1,k+nx+2,k+1))
mesh('Irregular_earth',vs,fs,'earth',r,True,uv)
for k in range(7):
    x=random.uniform(-4.8,4.8);y=random.uniform(-46,-2);rx=random.uniform(.35,1.0);ry=random.uniform(.4,1.6);v=[(x,y,-.029)];n=19
    for i in range(n):a=i*math.tau/n;rad=random.uniform(.85,1.12);v.append((x+rx*math.cos(a)*rad,y+ry*math.sin(a)*rad,-.029))
    mesh('Puddle',v,[(0,i+1,(i+1)%n+1) for i in range(n)],'glass',r,True)
export('terrain')

r=register('rock')
loft('Weathered_rock',[(0,0,0,.42,.33),(.06,0,.15,.52,.38),(-.02,.03,.43,.36,.28),(.04,.02,.64,.12,.15),(.05,.03,.67,.02,.02)],'concrete',r,n=13,irregular=.17);export('rock')
r=register('low_log');beam('Fallen_bark',(-1.4,0,.29),(1.4,.1,.29),.28,'bark',r,r2=.23,n=20)
for x in [-.6,.25,.8]:beam('Snapped_limb',(x,0,.3),(x+.14,.36,.63),.07,'bark',r,r2=.018,n=10)
export('low_log')
r=register('barricade')
for x in [-1.0,1.0]:
    for side in [-1,1]:beam('Trestle',(x,side*.45,.02),(x,0,1.22),.045,'wood',r,n=10)
for z in [.61,.97]:
    box('Splintered_plank',(0,0,z),(2.35,.10,.22),'wood',r,.009)
    for x in [-.98,.98]:ellipsoid('Nail_head',(x,-.055,z),(.009,.003,.009),'steel',r,n=8,rings=6)
export('barricade')
r=register('overhead')
for x in [-1.2,1.2]:beam('Bent_metal_upright',(x,0,0),(x,0,2.35),.055,'rust',r,n=12)
box('Collapsed_beam',(0,0,1.70),(2.5,.35,.55),'rust',r,.025);export('overhead')
r=register('fence')
for x in [-1.8,0,1.8]:
    box('Broken_fence_post',(x,0,.65),(.09,.10,1.3),'wood',r,.008)
for z in [.42,.90]:box('Faded_rail',(0,0,z),(3.8,.06,.13),'wood',r,.008)
export('fence')
# Storytelling ground clutter: rubble, scattered belongings and bandaged remains.
r=register('rubble')
for i in range(15):
    ob=box('Fractured_masonry',(random.uniform(-.8,.8),random.uniform(-.7,.7),random.uniform(.02,.18)),(random.uniform(.15,.4),random.uniform(.12,.35),random.uniform(.10,.24)),'concrete',r,.025,rot=(random.uniform(-.2,.2),random.uniform(-.2,.2),random.random()*6))
export('rubble')
r=register('body_bag');ellipsoid('Covered_remains',(0,0,.13),(.28,.85,.16),'leather',r,n=28)
beam('Zipped_seam',(0,-.8,.2),(0,.8,.2),.004,'steel',r,n=8);export('body_bag')
r=register('warning_sign');beam('Steel_post',(0,0,0),(0,0,1.75),.025,'rust',r,n=10);box('Sign_panel',(0,0,1.48),(1.1,.045,.53),'webbing',r,.012)
# Original warning glyph: diagonal stripes + quarantine cross, readable without copyrighted art.
for x in [-.35,-.18,0,.18,.35]:box('Hazard_stripe',(x,-.026,1.29),(.08,.005,.12),'ivory',r,.001,rot=(0,.35,0))
box('Warning_cross',(0,-.027,1.53),(.26,.008,.045),'ivory',r,.001);box('Warning_cross',(0,-.027,1.53),(.045,.008,.25),'ivory',r,.001);export('warning_sign')
for name,med in [('supply_crate',False),('med_crate',True)]:
    r=register(name);box('Ribbed_supply_case',(0,0,.24),(.65,.42,.46),'webbing',r,.04);box('Sealed_lid',(0,0,.49),(.69,.46,.065),'webbing',r,.016)
    for x in [-.24,.24]:
        box('Latch',(x,-.235,.40),(.055,.025,.11),'steel',r,.006)
        for y in [-.2,.2]:box('Corner_rib',(x,y,.25),(.034,.04,.45),'leather',r,.008)
    beam('Carry_handle',(-.09,-.242,.25),(.09,-.242,.25),.012,'steel',r,n=10)
    if med:
        box('Medical_cross',(0,-.217,.25),(.23,.009,.055),'ivory',r,.002);box('Medical_cross',(0,-.222,.25),(.055,.009,.23),'ivory',r,.002)
    else:
        for x in [-.1,0,.1]:box('Ammunition_stencil',(x,-.217,.25),(.038,.009,.16),'ivory',r,.002)
    export(name)
result={'natural_tree_variants':4,'static_kit_count':len([n for n in assets if not n.startswith(('survivor','zombie','dog','weapon'))])}
