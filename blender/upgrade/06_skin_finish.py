# CC0 hm08-compatible authored skin, credited in SOURCES.md; original infected treatment.
# Source: OnlyTheGhosts / MakeHuman Community skins01_cc0 pack. No game art is used.
import numpy as np
source=ROOT+'/blender/upgrade/reference-base/middleage_eurasian_female_diffuse.png'
image=bpy.data.images.load(source,check_existing=True);image.name='SR_Anatomical_skin_source';image.scale(1024,1024);image.pack()
data=np.array(image.pixels[:],dtype=np.float32).reshape((1024,1024,4))
for key in ['skin','infected','ashskin']:
    im=bpy.data.images.new('SR_'+key+'_Anatomical_1024',width=1024,height=1024);a=data.copy()
    if key!='skin':
        lum=a[:,:,:3].mean(axis=2);a[:,:,:3]=a[:,:,:3]*.32+lum[:,:,None]*.68
        a[:,:,:3]*=np.array([.79,.86,.73]) if key=='infected' else np.array([.85,.81,.73])
        gen=np.random.default_rng(65 if key=='infected' else 91);yy,xx=np.mgrid[0:1024,0:1024]
        for i in range(24):
            x,y=gen.integers(0,1024,2);rx,ry=gen.uniform(6,23,2);mask=np.exp(-((xx-x)/rx)**2-((yy-y)/ry)**2)*gen.uniform(.15,.55)
            a[:,:,:3]=a[:,:,:3]*(1-mask[:,:,None])+np.array([.15,.025,.018])*mask[:,:,None]
    else:a[:,:,:3]*=np.array([.9,.91,.91])
    im.pixels.foreach_set(a.ravel());im.pack()
    mat=M[key];tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'Albedo' in n.image.name);tex.image=im
# Export updated material maps without changing the already verified skeleton hierarchy.
for name in assets:
    if name.startswith(('survivor_','zombie_')):export(name)
result={'skin_resolution':1024,'cc0_skin_author':'OnlyTheGhosts','original_infected_treatments':2}
