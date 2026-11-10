# Correct the particle export's missing alpha: the browser requires a soft RGBA mask,
# not an RGB image that turns every smoke/flash point into a visible square.
import numpy as np
size=256;yy,xx=np.mgrid[0:size,0:size];u=(xx-size/2)/(size/2);v=(yy-size/2)/(size/2);rad=np.sqrt(u*u+v*v);gen=np.random.default_rng(5)
a=np.ones((size,size,4),dtype=np.float32);a[:,:,:3]=.7;a[:,:,3]=np.maximum(0,1-rad)**2*(.65+gen.random((size,size))*.35)
image=bpy.data.images.new('SR_Smoke_particle_RGBA',width=size,height=size,alpha=True);image.alpha_mode='STRAIGHT';image.pixels.foreach_set(a.ravel());image.update()
settings=scene.render.image_settings;old=(settings.file_format,settings.color_mode);settings.file_format='PNG';settings.color_mode='RGBA'
image.save_render(ROOT+'/public/assets/particle-smoke.png',scene=scene)
settings.file_format,settings.color_mode=old;image.pack()
bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/survivor-runs-production.blend')
result={'particle_channels':image.channels,'alpha':'soft radial mask','texture':ROOT+'/public/assets/particle-smoke.png'}
