# Original articulated survivors / infected. No external character meshes.
def human(name,role,cloth,skin,bulk=1):
    root=register(name); hip=empty(name+'_hips',root,(0,0,.91)); torso=empty(name+'_spine',hip)
    loft(name+'_tailored_jacket',[(0,0,0,.17*bulk,.12),(0,0,.13,.21*bulk,.14),(0,0,.37,.255*bulk,.145),(0,0,.5,.23*bulk,.13),(0,0,.55,.1,.09)],cloth,torso)
    box('waist_belt',(0,0,.04),(.37*bulk,.27,.055),'black',torso)
    box('belt_buckle',(0,-.145,.04),(.075,.025,.055),'steel',torso)
    rod('jacket_zip',(0,-.145,.1),(0,-.151,.48),.009,'steel',torso)
    for s in [-1,1]:
        box('chest_pocket',(s*.115,-.14,.34),(.13,.035,.13),cloth,torso)
        box('pocket_flap',(s*.115,-.165,.4),(.14,.02,.035),'canvas',torso)
        rod('shoulder_strap',(s*.14,-.16,.49),(s*.16,-.14,.11),.018,'black',torso)
    neck=rod('neck',(0,0,.51),(0,0,.65),.065,skin,torso)
    head=empty(name+'_head',torso,(0,0,.69))
    loft('shaped_face',[(0,0,-.09,.065,.07),(0,-.015,-.045,.088,.085),(0,0,.06,.10,.092),(0,.01,.13,.085,.08),(0,.01,.16,.04,.04)],skin,head,16)
    shape('nose',(0,-.098,.018),(.025,.037,.027),skin,head)
    for s in [-1,1]:
        shape('ear',(s*.1,.005,.025),(.023,.02,.04),skin,head)
        box('brow',(s*.045,-.087,.065),(.07,.023,.016),'black',head,bevel=.005)
        shape('eye',(s*.044,-.091,.04),(.018,.008,.012),'bone' if role=='survivor' else 'red',head)
        shape('pupil',(s*.044,-.098,.04),(.007,.005,.008),'black',head)
    box('mouth',(0,-.087,-.043),(.07,.01,.012),'black',head,bevel=.003)
    if role=='survivor':
        loft('wool_beanie',[(0,.01,.085,.106,.10),(0,.01,.16,.10,.095),(0,.01,.19,.07,.065),(0,.01,.205,.015,.015)],'black',head)
        box('backpack',(0,.19,.30),(.32,.2,.39),'canvas',torso,.06)
        box('pack_pouch',(0,.315,.23),(.25,.09,.18),'olive',torso,.03)
        for s in [-1,1]: rod('bedroll_strap',(s*.1,.21,.53),(s*.1,.21,.09),.018,'black',torso)
        rod('bedroll',(-.2,.22,.52),(.2,.22,.52),.07,'olive',torso,n=12)
    else:
        box('ragged_wound',(.13,-.151,.27),(.12,.013,.17),'blood',torso)
        for i in range(4): rod('exposed_rib',(.07,-.169,.20+i*.03),(.17,-.17,.21+i*.03),.009,'bone',torso)
        box('face_scarring',(-.055,-.083,-.005),(.045,.02,.08),'blood',head,.004)
    joints={'hips':hip,'spine':torso,'head':head}
    for s,side in [(-1,'L'),(1,'R')]:
        leg=empty(name+'_thigh'+side,hip,(s*.108*bulk,0,.015)); joints['thigh'+side]=leg
        loft('trouser_thigh',[(0,0,0,.105*bulk,.105),(0,0,-.17,.09*bulk,.095),(0,0,-.4,.067,.074)],'denim' if role=='survivor' else cloth,leg)
        knee=empty(name+'_shin'+side,leg,(0,0,-.4)); joints['shin'+side]=knee
        loft('trouser_shin',[(0,0,0,.069,.074),(0,.006,-.2,.062,.064),(0,0,-.35,.048,.05)],'denim',knee)
        shape('leather_boot',(0,-.053,-.405),(.075,.155,.09),'black',knee)
        box('boot_sole',(0,-.054,-.461),(.15,.28,.035),'black',knee,.01)
        box('kneepad',(0,-.073,-.015),(.12,.035,.12),'black',knee,.025)
        arm=empty(name+'_upperarm'+side,torso,(s*.255*bulk,0,.47)); joints['arm'+side]=arm
        loft('sleeve',[(0,0,.015,.093,.087),(s*.014,0,-.15,.078,.074),(0,0,-.28,.06,.06)],cloth,arm)
        fore=empty(name+'_forearm'+side,arm,(0,0,-.28)); joints['fore'+side]=fore
        loft('forearm',[(0,0,0,.06,.06),(0,0,-.18,.045,.046),(0,0,-.24,.039,.04)],skin,fore)
        shape('gloved_hand',(0,-.015,-.275),(.052,.045,.065),'black' if role=='survivor' else skin,fore)
        if role!='survivor':
            for finger in range(4): rod('fingers',(-.028+finger*.018,-.018,-.30),(-.028+finger*.018,-.04,-.36),.009,skin,fore)
    rigs[name]=joints
    root['asset_role']=role; root['height_mm']=1780
    return root

human('survivor_mara','survivor','olive','skin')
human('survivor_ellis','survivor','canvas','skin',1.08)
human('zombie_walker','zombie','gray','dead')
human('zombie_runner','zombie','red','pale',.85)
human('zombie_brute','zombie','olive','dead',1.42)

# Dog meshes are breed-specific with shaped ribcage/haunches, hocks, paws, jaw, ears and collar.
def dog(name,breed):
    root=register(name); body=empty(name+'_body',root,(0,0,.55)); joints={'body':body}
    coat='tan' if breed=='shepherd' else 'gray'
    shape('ribcage',(0,0,0),(.19,.43,.22),coat,body)
    shape('haunches',(0,.29,-.025),(.19,.19,.20),coat,body)
    shape('saddle',(0,.08,.14),(.17,.3,.09),'fur',body)
    head=empty(name+'_head',body,(0,-.36,.17)); joints['head']=head
    shape('neck',(0,.06,-.02),(.14,.17,.20),coat,head)
    shape('skull',(0,-.035,.11),(.135,.16,.14),coat,head)
    shape('muzzle',(0,-.21,.055),(.085,.16,.065),'fur',head)
    shape('nose',(0,-.34,.07),(.066,.035,.038),'black',head)
    jaw=empty(name+'_jaw',head,(0,-.13,.018)); joints['jaw']=jaw
    shape('lower_jaw',(0,-.09,-.01),(.069,.13,.025),coat,jaw)
    for s in [-1,1]:
        mesh('pointed_ear',[(s*.065,-.005,.19),(s*.14,.035,.17),(s*.125,.04,.39),(s*.1,-.035,.24)],[(0,1,2),(0,2,3),(3,2,1),(0,3,1)],coat,head,True)
        shape('eye',(s*.10,-.14,.15),(.022,.02,.018),'bone',head)
        shape('pupil',(s*.10,-.156,.15),(.012,.009,.014),'black',head)
        rod('fang',(s*.046,-.24,.03),(s*.046,-.24,-.015),.013,'bone',head,r2=.002)
    rod('collar',(-.145,-.32,.09),(.145,-.32,.09),.026,'red',body)
    box('dog_tag',(0,-.353,.02),(.055,.012,.07),'steel',body,.01)
    for s,side in [(-1,'L'),(1,'R')]:
        for y,label in [(-.27,'front'),(.29,'back')]:
            leg=empty(name+'_'+label+side,body,(s*.13,y,-.08)); joints[label+side]=leg
            loft('upper_leg',[(0,0,0,.073,.08),(0,.04,-.16,.04,.05),(0,.015,-.28,.028,.035)],coat,leg)
            rod('lower_leg',(0,.015,-.27),(0,-.012,-.4),.027,coat,leg,r2=.022)
            shape('paw',(0,-.045,-.41),(.052,.085,.035),'fur',leg)
    tail=empty(name+'_tail',body,(0,.42,.04)); joints['tail']=tail
    rod('tail',(0,0,0),(0,.3,-.18),.06,coat,tail,r2=.016)
    rigs[name]=joints
    root['breed']=breed
    return root

dog('dog_shepherd','shepherd'); dog('dog_husky','husky')
# A real NLA test/action; remaining library clips authored in the next workshop stage.
result={'assets':list(assets),'character_meshes':sum(len(r.children_recursive) for r in assets.values()),'rigs':len(rigs)}
