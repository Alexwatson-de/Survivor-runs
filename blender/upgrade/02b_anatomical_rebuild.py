"""Replace OUR first-pass human prototypes with CC0 anatomical topology.
The downloaded MakeHuman hm08 base explicitly declares CC0 (see reference-base/).
Original surface sculpting, outfits, damage, equipment, weights and animations are ours.
No MakeHuman application code or commercial game assets are used.
"""
from collections import defaultdict
raw=[];vt=[];faces=[];groups=defaultdict(set);group=None
for line in open(ROOT+'/blender/upgrade/reference-base/makehuman-base.obj'):
    if line.startswith('v '):raw.append(Vector(tuple(map(float,line[2:].split()))))
    elif line.startswith('vt '):vt.append(tuple(map(float,line[3:].split()[:2])))
    elif line.startswith('g '):group=line[2:].strip()
    elif line.startswith('f '):
        parts=[p.split('/') for p in line[2:].split()];vi=[int(p[0])-1 for p in parts];ti=[int(p[1])-1 if len(p)>1 and p[1] else 0 for p in parts]
        groups[group].update(vi)
        if group=='body':faces.append((vi,ti))
lo=min(raw[i].y for i in groups['body']);hi=max(raw[i].y for i in groups['body']);scale=1.82/(hi-lo)
base=[Vector((v.x*scale,-v.z*scale,(v.y-lo)*scale)) for v in raw]
def center(g):return sum((base[i] for i in groups[g]),Vector())/len(groups[g])
# Preserve earlier user scenes. Remove only prototypes created by our own stage 02.
for name in list(assets):
    if name.startswith(('survivor_','zombie_')):
        for o in list(assets[name].children_recursive)[::-1]+[assets[name]]:bpy.data.objects.remove(o,do_unlink=True)
        del assets[name];rigs.pop(name,None);skinparts.pop(name,None)

def makehuman(name,kind='survivor',bulk=1,coat='jacket',skin='skin',female=False):
    root=register(name);infected=kind!='survivor'
    def deform(v):
        x,y,z=v;side=1 if x>=0 else -1
        # Narrow the neutral spread stance, add distinct builds and worn clothing volume.
        if z<.95:x-=side*.12*max(0,min(1,(.95-z)/.87))
        x*=bulk
        if not female and 1.20<z<1.44 and abs(x)<.18 and y<-.09:y+=.023*math.sin((z-1.2)/.24*math.pi)
        if infected and z>1.56:
            y+=.012*math.exp(-((z-1.66)/.06)**2)*math.exp(-((abs(x)-.05)/.035)**2)
            if abs(x)<.055 and z<1.66:z-=.024*math.exp(-((z-1.62)/.045)**2)
        return Vector((x,y,z))
    points=[deform(v) for v in base]
    def j(label):return deform(center(label))
    bone_defs=[('hips',(0,0,.94),(0,0,1.05),None),('spine',(0,0,1.05),(0,-.015,1.29),'hips'),('chest',(0,-.015,1.29),(0,0,1.49),'spine'),('neck',(0,0,1.49),(0,-.012,1.57),'chest'),('head',(0,-.012,1.57),(0,0,1.81),'neck'),('pack',(0,.13,1.20),(0,.14,1.46),'chest')]
    bone_defs.append(('weapon_socket',(.12,-.49,1.31),(.12,-.75,1.31),'chest'))
    for side,source in [('R','l'),('L','r')]:
        sh=j('joint-'+source+'-shoulder');el=j('joint-'+source+'-elbow');wr=j('joint-'+source+'-hand');th=j('joint-'+source+'-upper-leg');kn=j('joint-'+source+'-knee');an=j('joint-'+source+'-ankle');ft=j('joint-'+source+'-foot-2')
        bone_defs.extend([('upper'+side,sh,el,'chest'),('fore'+side,el,wr,'upper'+side),('hand'+side,wr,wr+(wr-el).normalized()*.1,'fore'+side),('thigh'+side,th,kn,'hips'),('shin'+side,kn,an,'thigh'+side),('foot'+side,an,ft,'shin'+side)])
    rig=armature(name,bone_defs,root);segments={bn:(Vector(h),Vector(t)) for bn,h,t,p in bone_defs if bn not in ['pack','weapon_socket']}
    def weights(p):
        x,y,z=p
        if z>1.575:return {'head':1}
        if z>1.49 and abs(x)<.09:return {'neck':.65,'head':.35}
        dist=[]
        for bn,(a,b) in segments.items():
            if bn in ['head','neck']:continue
            if z>.91 and bn.startswith(('thigh','shin','foot')):continue
            if z<.86 and not bn.startswith(('thigh','shin','foot')):continue
            d=b-a;t=max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-8)));distance=(p-(a+d*t)).length
            if bn.startswith(('upper','fore','hand')) and abs(x)<.17*bulk:distance+=.2
            dist.append((distance,bn))
        nearest=sorted(dist)[:3];w=[1/(d+.025)**5 for d,bn in nearest];total=sum(w);return {bn:a/total for (d,bn),a in zip(nearest,w)}
    normals=[Vector() for _ in points]
    for indices,texids in faces:
        a,b,c=[points[i] for i in indices[:3]];normal=(b-a).cross(c-a)
        for i in indices:normals[i]+=normal
    for normal in normals:
        if normal.length:normal.normalize()
    # Expanded loop vertices retain authored anatomical UV seams/material zones and skin weights.
    vs=[];uv=[];ws=[];fs=[];matids=[];palette=[skin,coat,'denim','leather','blood','webbing']
    for indices,texids in faces:
        ps=[points[i] for i in indices];c=sum(ps,Vector())/len(ps);x,y,z=c
        if z<.115:continue # boots replace exposed anatomical feet
        if infected and -.08<x<-.03 and 1.63<z<1.69 and y<-.13:continue # cheek wound opening
        part='skin' if z>1.56 or z>1.49 and abs(x)<.07 else 'pants' if z<.99 else 'coat'
        # Hands and wrists are defined by proximity to native hand joints, not just height.
        if abs(x)>.38*bulk and z<1.24:part='glove' if not infected else 'skin'
        mat=skin if part=='skin' else 'leather' if part=='glove' else 'denim' if part=='pants' else coat
        normal=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized()
        start=len(vs)
        for idx,p in enumerate(ps):
            co=p.copy()
            if part in ['coat','pants']:
                cloth=.019 if part=='coat' else .007
                cloth+=.0035*math.sin(co.z*110+co.x*12)*math.sin(co.z*43+co.y*15)
                co+=normals[indices[idx]]*cloth
                if part=='coat' and 1.18<co.z<1.47 and abs(co.x)<.18*bulk:co.y=max(co.y,-.145)
            vs.append(co);uv.append(vt[texids[idx]]);ws.append(weights(p))
        fs.append(tuple(range(start,start+len(ps))));matids.append(palette.index(mat))
    obj=mesh('Anatomical_clothed_surface',vs,fs,skin,root,True,uv,ws,name)
    obj.data.materials.clear()
    for mat in palette:obj.data.materials.append(M[mat])
    for poly,mi in zip(obj.data.polygons,matids):poly.material_index=mi
    # Weld loop seam vertices is deliberately omitted; UV/material seams remain valid for glTF.
    # Eye spheres fit real anatomical sockets rather than protruding cartoon eyes.
    for source in ['l','r']:
        eye=j('joint-'+source+'-eye');eye.y-=.001
        ellipsoid('Eye_globe',eye,(.011,.010,.010),'ivory',root,'head',name,n=20,rings=10)
        ellipsoid('Iris',eye+Vector((0,-.009,0)),(.0045,.002,.0047),'leather' if not infected else 'bone',root,'head',name,n=16,rings=6)
        ellipsoid('Pupil',eye+Vector((0,-.011,0)),(.002,.001,.003),'rubber',root,'head',name,n=12,rings=6)
    if infected:
        ellipsoid('Mouth_cavity',(0,-.15,1.612),(.035,.01,.019),'blood',root,'head',name,n=20)
        ellipsoid('Cheek_damage',(-.052,-.125,1.66),(.028,.008,.027),'blood',root,'head',name,n=20)
        for row in [-1,1]:
            for k in range(7):box('Exposed_broken_teeth',(-.025+k*.008,-.16,1.612+row*.010),(.006,.006,.009),'bone',root,.001,'head',name)
        for k in range(3):
            beam('Neck_tendon',(-.022+k*.022,-.075,1.51),(-.025+k*.025,-.08,1.57),.003,'blood',root,'neck',name,n=8)
    else:
        # Scalp/fitted cap/hair with strands; short styles expose the face naturally.
        if female:
            loft('Short_swept_hair',[(0,-.035,1.75,.087,.119),(0,-.030,1.79,.085,.117),(0,-.025,1.82,.055,.075),(0,-.025,1.835,.014,.02)],'leather',root,n=36,bone='head',root=name,irregular=.035)
            ellipsoid('Tied_hair',(0,.10,1.74),(.031,.045,.052),'leather',root,'head',name,n=20)
        else:
            loft('Worn_field_cap',[(0,-.038,1.75,.096,.125),(0,-.035,1.795,.092,.12),(0,-.028,1.827,.069,.077),(0,-.025,1.84,.02,.023)],coat,root,n=36,bone='head',root=name)
            ellipsoid('Cap_brim',(0,-.124,1.758),(.085,.071,.006),coat,root,'head',name,n=24)
    # Authored clothing seams, equipment and authentic scale fastening details.
    for s,side in [(-1,'L'),(1,'R')]:
        foot=segments['foot'+side][0];fx=foot.x
        ellipsoid('Laced_combat_boot',(fx,-.086,.10),(.067,.153,.09),'leather',root,'foot'+side,name,n=24)
        box('Treaded_sole',(fx,-.09,.035),(.135,.28,.026),'rubber',root,.009,'foot'+side,name)
        for k in range(5):beam('Boot_laces',(fx-.025,-.11+k*.022,.167),(fx+.025,-.095+k*.022,.167),.0025,'webbing',root,'foot'+side,name,n=6)
        # Flattened sewn pockets, not spherical pads.
        box('Cargo_pocket',(s*.17*bulk,-.015,.72),(.045,.12,.16),coat,root,.014,'thigh'+side,name)
        box('Chest_patch_pocket',(s*.095,-.128,1.34),(.105,.022,.12),coat,root,.012,'chest',name)
        if not infected or kind=='military':
            beam('Harness',(s*.13,.065,1.49),(s*.15,-.14,1.33),.012,'webbing',root,'chest',name,n=10)
            beam('Front_strap',(s*.15,-.14,1.33),(s*.13,-.12,1.04),.011,'webbing',root,'spine',name,n=10)
            box('Steel_buckle',(s*.14,-.145,1.19),(.026,.008,.035),'steel',root,.003,'spine',name)
    box('Woven_belt',(0,-.005,.99),(.33*bulk,.235,.030),'leather',root,.014,'hips',name)
    box('Belt_buckle',(0,-.13,.99),(.04,.008,.029),'steel',root,.003,'hips',name)
    if not infected:
        ellipsoid('Contoured_backpack',(0,.155,1.30),(.151,.098,.215),'webbing',root,'pack',name,n=28)
        box('Sewn_pack_pocket',(0,.237,1.24),(.23,.055,.145),coat,root,.025,'pack',name)
        for s in [-1,1]:
            beam('Pack_binding',(s*.10,.245,1.14),(s*.10,.24,1.47),.008,'leather',root,'pack',name,n=8)
            ellipsoid('Side_bottle',(s*.15,.14,1.22),(.031,.038,.10),'webbing',root,'pack',name,n=16)
        beam('Jacket_zip',(0,-.126,1.03),(0,-.133,1.46),.0025,'steel',root,'spine',name,n=6)
        box('Radio',(-.15,-.145,1.39),(.035,.027,.063),'rubber',root,.004,'chest',name)
        beam('Radio_antenna',(-.15,-.145,1.42),(-.15,-.145,1.51),.002,'steel',root,'chest',name,n=6)
    else:
        for k in range(6):
            z=1.12+k*.033;beam('Torn_cloth_edges',(-.03,-.132,z),(.08,-.14,z+.016),.004,'blood',root,'spine',name,n=8)
        if kind=='military':
            loft('Dented_ballistic_helmet',[(0,-.035,1.725,.108,.135),(0,-.035,1.77,.108,.13),(0,-.025,1.825,.08,.10),(0,-.02,1.852,.025,.03)],'jacket',root,n=32,bone='head',root=name,irregular=.01)
            for s in [-1,1]:
                for k in range(3):box('Vest_ammo_pouch',(s*.09,-.155,1.15+k*.09),(.07,.037,.073),'webbing',root,.012,'spine',name)
    sk=bind_join(name)
    # Collapse duplicate positions while retaining per-loop UV seams and deform weights.
    import bmesh
    bm=bmesh.new();bm.from_mesh(sk.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.to_mesh(sk.data);bm.free();sk.data.update()
    bpy.ops.object.select_all(action='DESELECT');sk.select_set(True);bpy.context.view_layer.objects.active=sk
    # Native decimation before skin preserves weights and reduces far-actor cost.
    dec=sk.modifiers.new('Game topology budget','DECIMATE');dec.ratio=.62 if infected else .78
    bpy.ops.object.modifier_move_up(modifier=dec.name);bpy.ops.object.modifier_apply(modifier=dec.name)
    root['kind']=kind;root['base_mesh_license']='CC0 MakeHuman hm08';root['revision']='0.2';root['height_mm']=1840
    if kind=='brute':root.scale=(1.12,1.12,1.08)
    return root
makehuman('survivor_mara',female=True)
makehuman('survivor_ellis',bulk=1.06,coat='parka')
makehuman('zombie_walker','regular',.94,'parka','infected')
makehuman('zombie_runner','fast',.86,'red','ashskin')
makehuman('zombie_brute','brute',1.22,'denim','infected')
makehuman('zombie_military','military',1.04,'jacket','ashskin')
makehuman('zombie_stalker','stalker',.81,'leather','infected')
result={'anatomical_characters':7,'skinned_meshes':len([o for o in scene.objects if o.type=='MESH']),'cc0_base_verified':True,'survivor_vertices':len(next(o for o in assets['survivor_mara'].children_recursive if o.type=='MESH').data.vertices)}
