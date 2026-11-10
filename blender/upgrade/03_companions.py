# Friendly companions only: anatomical quadruped surfaces, weighted legs/hocks/jaw/tail.
# Rook: German Shepherd saddle; Ghost: Husky with facial mask and heavier tail.
def make_dog(name,breed):
    root=register(name);husky=breed=='husky';coat='fur_grey' if husky else 'fur_tan'
    bones=[('hips',(0,.27,.57),(0,.02,.58),None),('spine',(0,.02,.58),(0,-.28,.62),'hips'),('neck',(0,-.28,.62),(0,-.45,.78),'spine'),('head',(0,-.45,.78),(0,-.67,.83),'neck'),('jaw',(0,-.53,.74),(0,-.78,.72),'head'),('tail',(0,.40,.56),(0,.64,.43),'hips'),('tailtip',(0,.64,.43),(0,.80,.31),'tail')]
    for s,side in [(-1,'L'),(1,'R')]:
        bones.extend([('front'+side,(s*.13,-.27,.57),(s*.145,-.23,.31),'spine'),('frontlower'+side,(s*.145,-.23,.31),(s*.14,-.32,.10),'front'+side),('frontpaw'+side,(s*.14,-.32,.1),(s*.14,-.43,.065),'frontlower'+side),('back'+side,(s*.14,.27,.55),(s*.15,.14,.34),'hips'),('backlower'+side,(s*.15,.14,.34),(s*.14,.36,.16),'back'+side),('backpaw'+side,(s*.14,.36,.16),(s*.14,.28,.055),'backlower'+side)])
    rig=armature(name,bones,root)
    # Rib cage cross sections follow the spine rather than an ellipsoid object.
    vs=[];uv=[];ws=[];fs=[];sections=[(.43,.54,.08,.10),(.35,.56,.15,.17),(.21,.57,.18,.20),(.05,.57,.16,.20),(-.10,.59,.18,.22),(-.25,.62,.19,.23),(-.34,.66,.14,.18)]
    n=32
    for i,(y,z,rx,rz) in enumerate(sections):
        for j in range(n):
            a=j*math.tau/n;vs.append((rx*math.cos(a),y,z+rz*math.sin(a)));uv.append((j/n,i/(len(sections)-1)));t=max(0,min(1,(.22-y)/.43));ws.append({'hips':1-t,'spine':t})
    fs=[tuple(reversed(range(n)))]
    for i in range(len(sections)-1):
        for j in range(n):fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    fs.append(tuple(range((len(sections)-1)*n,len(sections)*n)))
    body=mesh('Tapered_ribcage_and_flanks',vs,fs,coat,root,True,uv,ws,name)
    body.data.materials.append(M['fur_dark'])
    for p in body.data.polygons:
        c=p.center
        if c.z>.67 or not husky and c.z>.53 and c.y>.04:p.material_index=1
    ellipsoid('Shoulder_ruff',(0,-.32,.69),(.15,.15,.20),coat,root,'neck',name,n=28,rings=16)
    ellipsoid('Cranium',(0,-.49,.84),(.105,.135,.12),coat,root,'head',name,n=32,rings=18)
    # Long wedge-shaped muzzle, not a sphere or capsule.
    v=[];w=[];u=[];f=[]
    for i,(y,z,rx,rz) in enumerate([(-.53,.80,.088,.068),(-.61,.795,.075,.057),(-.72,.776,.050,.041),(-.785,.772,.039,.032)]):
        for j in range(24):a=j*math.tau/24;v.append((rx*math.cos(a),y,z+rz*math.sin(a)));w.append({'head':1});u.append((j/24,i/3))
    for i in range(3):
        for j in range(24):f.append((i*24+j,i*24+(j+1)%24,(i+1)*24+(j+1)%24,(i+1)*24+j))
    f.append(tuple(range(72,96)));mesh('Sculpted_muzzle',v,f,'fur_dark' if not husky else 'fur_cream',root,True,u,w,name)
    ellipsoid('Nose',(0,-.792,.778),(.041,.018,.027),'rubber',root,'head',name,n=24,rings=10)
    ellipsoid('Lower_jaw',(0,-.656,.738),(.061,.12,.028),coat,root,'jaw',name,n=24)
    for s in [-1,1]:
        ellipsoid('Eye_socket',(s*.078,-.571,.873),(.019,.012,.016),'fur_dark',root,'head',name,n=20)
        ellipsoid('Amber_eye',(s*.080,-.581,.874),(.010,.006,.009),'bone',root,'head',name,n=16)
        ellipsoid('Pupil',(s*.080,-.586,.874),(.004,.002,.006),'rubber',root,'head',name,n=12,rings=6)
        # Thick upright ears with visible inner ear and multiple contour rings.
        er=[(s*.065,-.455,.91,.044,.045),(s*.085,-.44,1.00,.035,.031),(s*.103,-.425,1.10 if husky else 1.12,.005,.007)]
        loft('Upright_ear',er,coat,root,n=16,bone='head',root=name)
        mesh('Inner_ear',[(s*.064,-.497,.94),(s*.105,-.471,.98),(s*.103,-.433,1.08)],[(0,1,2)],'leather',root,True,weights=[{'head':1}]*3,root=name)
        if husky:ellipsoid('Cream_cheek',(s*.069,-.54,.802),(.044,.06,.056),'fur_cream',root,'head',name,n=20)
        beam('Canine_tooth',(s*.034,-.701,.75),(s*.034,-.70,.724),.009,'bone',root,'head',name,r2=.002,n=10)
        for front,y in [(True,-.27),(False,.27)]:
            prefix='front' if front else 'back';side='L' if s<0 else 'R';upper=prefix+side;lower=prefix+'lower'+side;paw=prefix+'paw'+side
            if front:rs=[(s*.14,-.32,.09,.025,.028),(s*.145,-.27,.20,.026,.032),(s*.145,-.23,.31,.037,.04),(s*.14,-.26,.43,.048,.055),(s*.13,-.27,.58,.072,.09)]
            else:rs=[(s*.14,.32,.08,.027,.033),(s*.14,.36,.16,.027,.034),(s*.145,.27,.25,.036,.038),(s*.15,.14,.34,.06,.067),(s*.14,.23,.45,.084,.10),(s*.14,.27,.56,.09,.11)]
            def weight(co,upper=upper,lower=lower,paw=paw,front=front):
                z=co[2]
                if z<.13:return {paw:1}
                t=max(0,min(1,(z-.26)/.14));return {upper:t,lower:1-t}
            loft('Muscular_leg_and_hock',rs,coat,root,n=20,weightfn=weight,root=name)
            py=-.36 if front else .28
            ellipsoid('Paw',(s*.14,py,.055),(.045,.073,.037),coat,root,paw,name,n=20)
            for k in range(4):
                ellipsoid('Toe',(s*.14-.025+k*.017,py-.035,.045),(.012,.027,.02),'fur_dark' if not husky else 'fur_cream',root,paw,name,n=10,rings=6)
    # Tapered, weighted bushy tail with separate tip.
    beam('Tail_base',(0,.40,.56),(0,.64,.43),.055 if not husky else .075,coat,root,'tail',name,r2=.043,n=20)
    beam('Tail_tip',(0,.64,.43),(0,.80,.31),.043 if not husky else .064,'fur_dark' if not husky else 'fur_cream',root,'tailtip',name,r2=.012,n=20)
    beam('Collar',(-.13,-.33,.73),(.13,-.33,.73),.017,'red',root,'neck',name,n=12)
    box('ID_tag',(0,-.422,.68),(.025,.009,.036),'steel',root,.004,'neck',name)
    # Coat detail is carried by mapped fur normals, not upright spiky geometry.
    sk=bind_join(name);root['breed']=breed;root['friendly']=True;root['revision']='0.2';return root
make_dog('dog_shepherd','shepherd');make_dog('dog_husky','husky')
result={'friendly_skinned_dogs':2,'dog_bones':len(rigs['dog_shepherd'].data.bones),'dog_mesh_vertices':len(next(o for o in assets['dog_shepherd'].children_recursive if o.type=='MESH').data.vertices)}
