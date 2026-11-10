# Selection images are renders of the actual authored models, not painted placeholders.
import os
bpy.context.window.scene=scene;os.makedirs(ROOT+'/public/assets/ui',exist_ok=True)
cam=review_cam;scene.camera=cam;scene.render.film_transparent=True;scene.render.resolution_percentage=100
names=['survivor_mara','survivor_ellis','dog_shepherd','dog_husky']+['weapon_'+k for k in ['pistol','revolver','shotgun','rifle','smg','hunting']]
for name in names:
    human=name.startswith('survivor_');dog=name.startswith('dog_');show={name,'weapon_pistol'} if human else {name}
    for n,r in assets.items():
        for ob in [r]+list(r.children_recursive):ob.hide_render=n not in show
        r.location=(0,0,0)
        if n in rigs:
            for tr in rigs[n].animation_data.nla_tracks:tr.mute=not (n==name and tr.name=='idle')
    if human:assets['weapon_pistol'].location=(.12,-.49,1.31)
    if human:target=Vector((0,0,1.0));cam.location=(2.5,-5,2.1);cam.data.ortho_scale=2.10;scene.render.resolution_x=320;scene.render.resolution_y=380
    elif dog:target=Vector((0,-.15,.52));cam.location=(2,-3,1.2);cam.data.ortho_scale=1.50;scene.render.resolution_x=380;scene.render.resolution_y=280
    else:target=Vector((0,-.13,-.015));cam.location=(2.2,-.75,.65);cam.data.ortho_scale=1.25;scene.render.resolution_x=480;scene.render.resolution_y=230
    cam.data.type='ORTHO';cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.frame_set(4);scene.render.filepath=ROOT+'/public/assets/ui/'+name+'.png';bpy.ops.render.render(write_still=True)
for name,root in assets.items():
    root.location=(0,0,0)
    for ob in [root]+list(root.children_recursive):ob.hide_render=False
    if name in rigs:
        for tr in rigs[name].animation_data.nla_tracks:tr.mute=True
scene.frame_set(0);scene.render.film_transparent=False;bpy.context.window.scene=review
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
result={'model_selection_renders':len(names),'directory':ROOT+'/public/assets/ui'}
