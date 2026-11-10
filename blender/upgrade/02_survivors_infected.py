# Anatomical skinned survivors / infected. Clothing, skin, fingers, face and equipment
# deform on an actual armature; no exposed ball-joint mannequin parts.
def human(name,kind='survivor',bulk=1,coat='jacket',face='skin',female=False):
    root=register(name);zombie=kind!='survivor'
    bones=[('hips',(0,0,.91),(0,0,1.07),None),('spine',(0,0,1.07),(0,0,1.31),'hips'),('chest',(0,0,1.31),(0,0,1.51),'spine'),('neck',(0,0,1.51),(0,0,1.61),'chest'),('head',(0,0,1.61),(0,0,1.83),'neck'),('pack',(0,.14,1.18),(0,.14,1.46),'chest')]
    for s,side in [(-1,'L'),(1,'R')]:
        bones += [('thigh'+side,(s*.105,0,.94),(s*.11,-.012,.51),'hips'),('shin'+side,(s*.11,-.012,.51),(s*.105,0,.115),'thigh'+side),('foot'+side,(s*.105,0,.115),(s*.105,-.19,.07),'shin'+side),('upper'+side,(s*.205*bulk,0,1.49),(s*.32*bulk,-.005,1.20),'chest'),('fore'+side,(s*.32*bulk,-.005,1.20),(s*.36*bulk,-.01,.91),'upper'+side),('hand'+side,(s*.36*bulk,-.01,.91),(s*.37*bulk,-.035,.81),'fore'+side)]
    rig=armature(name,bones,root)
    def body_weights(co):
        z=co[2]
        if z<1.06:return {'hips':1}
        if z<1.30:
            t=(z-1.06)/.24;return {'hips':(1-t)*.5,'spine':.5,'chest':t*.5}
        return {'chest':1}
    # One continuous clothed torso, with waist, rib cage, shoulder, neckline and cloth folds.
    rs=[]
    base=[(.82,.15,.105),(.90,.18,.125),(1.0,.166,.119),(1.10,.163,.128),(1.20,.184,.142),(1.31,.212,.146),(1.40,.224,.139),(1.47,.215,.125),(1.51,.17,.105),(1.54,.082,.073)]
    if female:base=[(z,rx*(.90 if z>1.12 else 1.03),ry) for z,rx,ry in base]
    for z,rx,ry in base:
        rs.append((0,0,z,rx*bulk,ry));
        if z<1.47:rs.append((0,-.002,z+.012,rx*bulk*1.025,ry*1.025))
    loft('Tailored_cloth_torso',sorted(rs,key=lambda x:x[2]),coat,root,n=32,root=name,weightfn=body_weights,irregular=.013)
    # Pelvis and trousers transition continuously through knee into shin; seam/fold rings.
    for s,side in [(-1,'L'),(1,'R')]:
        leg=[]
        for z,rad,dep,cy in [(.10,.052,.055,0),(.18,.060,.065,.006),(.29,.064,.068,.004),(.39,.069,.073,0),(.47,.073,.077,-.012),(.51,.074,.075,-.015),(.54,.075,.076,0),(.62,.086,.092,.008),(.76,.105,.112,.005),(.91,.107,.115,0),(.98,.098,.105,0)]:
            leg.append((s*.108,cy,z,rad*(bulk if z>.6 else 1),dep))
            if z in [.29,.47,.62]:leg.append((s*.108,cy+.003,z+.017,rad*1.055,dep*1.05))
        def lw(co,side=side):
            z=co[2];t=max(0,min(1,(z-.45)/.12));return {'thigh'+side:t,'shin'+side:1-t}
        loft('Worn_cargo_trousers',sorted(leg,key=lambda x:x[2]),'denim' if not zombie else coat,root,n=24,weightfn=lw,root=name,irregular=.018)
        # Boots: shaped toe box, heel, ankle cuff, sole and actual lacing.
        ellipsoid('Boot_upper',(s*.105,-.068,.092),(.068,.145,.074),'leather',root,'foot'+side,name,n=24)
        box('Boot_sole',(s*.105,-.072,.043),(.14,.285,.034),'rubber',root,.013,'foot'+side,name)
        for k in range(5):
            y=-.12+k*.025
            beam('Boot_lacing',(s*.105-.03,y,.139),(s*.105+.03,y+.015,.143),.004,'webbing',root,'foot'+side,name,n=6)
        # Stitched cargo pockets and knee reinforcement, not rectangular limb segments.
        ellipsoid('Cargo_pocket',(s*.18,.012,.70),(.054,.08,.105),coat,root,'thigh'+side,name,n=16)
        ellipsoid('Knee_reinforcement',(s*.108,-.074,.50),(.067,.016,.085),'leather',root,'shin'+side,name,n=16)
        # Continuous sleeve/forearm silhouette in an A-pose, softly weighted at elbow.
        sleeve=[(s*.36*bulk,-.01,.90,.038,.039),(s*.355*bulk,-.008,.98,.047,.047),(s*.347*bulk,-.006,1.08,.058,.057),(s*.32*bulk,-.005,1.19,.066,.066),(s*.31*bulk,0,1.23,.070,.071),(s*.273*bulk,0,1.35,.081,.08),(s*.205*bulk,0,1.48,.092,.086)]
        def aw(co,side=side):
            t=max(0,min(1,(co[2]-1.15)/.13));return {'upper'+side:t,'fore'+side:1-t}
        loft('Fitted_wrinkled_sleeves',sleeve,coat,root,n=24,weightfn=aw,root=name,irregular=.018)
        loft('Cuff',[(s*.359*bulk,-.01,.905,.045,.044),(s*.358*bulk,-.01,.945,.048,.047)],'leather',root,n=20,bone='fore'+side,root=name)
        ellipsoid('Palm',(s*.369*bulk,-.019,.864),(.042,.029,.055),'leather' if not zombie else face,root,'hand'+side,name,n=20)
        # Individual tapering fingers, with knuckles and bent fingertips.
        for i in range(4):
            x=s*.369*bulk-.027+i*.018;length=[.057,.067,.064,.047][i]
            loft('Finger',[(x,-.018,.847,.010,.012),(x,-.023,.825,.010,.011),(x,-.04,.847-length,.008,.009)],'leather' if not zombie else face,root,n=8,bone='hand'+side,root=name)
        beam('Thumb',(s*.369*bulk-s*.038,-.02,.88),(s*.369*bulk-s*.059,-.055,.84),.014,'leather' if not zombie else face,root,'hand'+side,name,r2=.010,n=10)
    # Neck is a real tapered transition, and the face is a sculpted continuous surface.
    loft('Neck',[(0,0,1.50,.065,.061),(0,0,1.58,.055,.055),(0,0,1.64,.059,.057)],face,root,n=24,bone='neck',root=name)
    vs=[];uv=[];weights=[];nr=24;n=48
    shape=[(1.59,.038,.042),(1.61,.059,.057),(1.64,.071,.067),(1.68,.080,.075),(1.72,.086,.080),(1.76,.083,.081),(1.80,.071,.070),(1.83,.039,.041),(1.845,.006,.008)]
    def interpolate(z):
        for i in range(len(shape)-1):
            a,b=shape[i:i+2]
            if a[0]<=z<=b[0]:t=(z-a[0])/(b[0]-a[0]);return a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t
        return shape[-1][1:]
    for i in range(nr+1):
        z=1.59+(1.845-1.59)*i/nr;rx,ry=interpolate(z)
        for j in range(n):
            a=j*math.tau/n;x=rx*math.cos(a);y=.007+ry*math.sin(a)
            if math.sin(a)<-.4:
                gauss=lambda cx,cz,sx,sz:math.exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
                y-=.026*gauss(0,1.711,.018,.036)+.009*gauss(0,1.739,.015,.032)
                y+=.012*(gauss(-.038,1.737,.024,.015)+gauss(.038,1.737,.024,.015))
                y-=.011*(gauss(-.041,1.757,.033,.012)+gauss(.041,1.757,.033,.012))
                y+=.006*gauss(0,1.655,.037,.012)
                if zombie:y+=.011*gauss(-.047,1.681,.025,.029)
            vs.append((x,y,z));uv.append((j/n,i/nr));weights.append({'head':1})
    fs=[]
    for i in range(nr):
        for j in range(n):
            # An actual missing cheek patch reveals teeth/underlying wound on infected.
            if zombie and 7<i<12 and 29<j<34:continue
            fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    fs.extend([tuple(reversed(range(n))),tuple(range(nr*n,(nr+1)*n))]);mesh('Anatomical_sculpted_face',vs,fs,face,root,True,uv,weights,name)
    for s in [-1,1]:
        ellipsoid('Ear',(s*.086,.005,1.714),(.018,.012,.032),face,root,'head',name,n=16)
        ellipsoid('Ear_concha',(s*.095,-.003,1.713),(.007,.006,.019),'red' if zombie else 'parka',root,'head',name,n=12)
        ellipsoid('Recessed_eye',(s*.035,-.066,1.738),(.016,.008,.009),'ivory',root,'head',name,n=16,rings=6)
        ellipsoid('Iris',(s*.035,-.073,1.738),(.006,.002,.006),'blood' if zombie else 'leather',root,'head',name,n=12,rings=6)
        beam('Eyebrow',(s*.016,-.076,1.758),(s*.058,-.065,1.758),.004,'leather',root,'head',name,n=8)
        ellipsoid('Nostril',(s*.009,-.105,1.702),(.005,.004,.003),'blood' if zombie else 'leather',root,'head',name,n=10,rings=6)
    ellipsoid('Lip_line',(0,-.068,1.663),(.027,.004,.006),'blood' if zombie else 'red',root,'head',name,n=20,rings=6)
    if not zombie:
        # Hair cap has layered silhouette, sideburns and material variation.
        loft('Hair_cap',[(0,.018,1.752,.085,.074),(0,.012,1.795,.078,.077),(0,.012,1.835,.051,.051),(0,.012,1.85,.006,.007)],'leather',root,n=32,bone='head',root=name,irregular=.07)
        if female:
            ellipsoid('Tied_hair',(0,.095,1.75),(.034,.06,.045),'leather',root,'head',name)
        else:
            loft('Field_cap',[(0,.006,1.788,.090,.081),(0,.01,1.835,.085,.078),(0,.01,1.855,.060,.056)],coat,root,n=32,bone='head',root=name)
            ellipsoid('Cap_visor',(0,-.097,1.794),(.085,.062,.009),coat,root,'head',name)
        # Backpack: shaped sewn panels, straps, bedroll, buckles, canteen and radio.
        ellipsoid('Backpack_main',(0,.19,1.29),(.163,.102,.224),'webbing',root,'pack',name,n=28)
        ellipsoid('Backpack_lower_pocket',(0,.276,1.20),(.126,.042,.093),coat,root,'pack',name,n=24)
        for s in [-1,1]:
            beam('Shoulder_strap',(s*.13,.13,1.50),(s*.15,-.145,1.34),.018,'leather',root,'chest',name,n=10)
            beam('Front_webbing',(s*.15,-.145,1.34),(s*.13,-.126,1.04),.015,'webbing',root,'spine',name,n=10)
            box('Strap_buckle',(s*.14,-.146,1.19),(.034,.012,.041),'steel',root,.004,'spine',name)
            ellipsoid('Pack_side_pouch',(s*.16,.19,1.23),(.041,.071,.11),coat,root,'pack',name)
            ellipsoid('Chest_pocket',(s*.10,-.136,1.34),(.064,.018,.067),coat,root,'chest',name)
            beam('Pocket_stitch',(s*.04,-.154,1.39),(s*.16,-.154,1.39),.002,'webbing',root,'chest',name,n=6)
        beam('Jacket_zipper',(0,-.132,1.03),(0,-.15,1.48),.004,'steel',root,'spine',name,n=8)
        box('Radio',(-.17,-.15,1.37),(.045,.035,.075),'rubber',root,.006,'chest',name)
        beam('Radio_antenna',(-.17,-.15,1.40),(-.17,-.15,1.51),.003,'steel',root,'chest',name,n=6)
        ellipsoid('Canteen',(.19,.07,.96),(.049,.031,.078),'webbing',root,'hips',name)
    else:
        ellipsoid('Torn_cheek_wound',(-.048,-.062,1.683),(.029,.008,.028),'blood',root,'head',name)
        for i in range(6):
            box('Broken_exposed_teeth',(-.055+i*.008,-.074,1.68),(.006,.009,.012),'bone',root,.002,'head',name)
        for i in range(5):
            z=1.18+i*.028;beam('Rib_wound',(0.03,-.151,z),(.14,-.155,z+.015),.008,'blood',root,'spine',name,n=8)
        for s in [-1,1]:
            for k in range(5):
                z=.86+k*.105
                beam('Ripped_fabric_threads',(s*.17,-.13,z),(s*.18,-.14,z-.035),.002,'webbing',root,'hips' if z<1.08 else 'spine',name,n=6)
        if kind=='military':
            loft('Battered_helmet',[(0,.01,1.748,.104,.099),(0,.01,1.79,.103,.097),(0,.01,1.84,.079,.076),(0,.01,1.87,.025,.027)],'jacket',root,n=32,bone='head',root=name,irregular=.018)
            for s in [-1,1]:
                for k in range(3):box('Magazine_pouch',(s*.11,-.16,1.21+k*.085),(.075,.055,.065),'webbing',root,.014,'spine',name)
        if kind=='stalker':
            for s in [-1,1]:beam('Exposed_arm_tendon',(s*.35,-.05,1.12),(s*.37,-.065,.92),.009,'blood',root,'fore'+('L' if s<0 else 'R'),name,n=8)
    box('Utility_belt',(0,0,.975),(.35*bulk,.248,.035),'leather',root,.02,'hips',name)
    box('Belt_clasp',(0,-.13,.975),(.047,.014,.033),'steel',root,.004,'hips',name)
    sk=bind_join(name);root['kind']=kind;root['height_mm']=1845
    if kind=='brute':root.scale=(1.14,1.14,1.10)
    return root
human('survivor_mara',female=True)
human('survivor_ellis',coat='parka',bulk=1.04)
human('zombie_walker','regular',.93,'parka','infected')
human('zombie_runner','fast',.84,'red','ashskin')
human('zombie_brute','brute',1.30,'denim','infected')
human('zombie_military','military',1.05,'jacket','ashskin')
human('zombie_stalker','stalker',.78,'leather','infected')
result={'skinned_humans':7,'meshes':[o.name for o in scene.objects if o.type=='MESH'],'bone_count':len(rigs['survivor_mara'].data.bones)}
