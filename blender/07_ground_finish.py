# Final authored terrain polish: non-periodic 512px earth albedo, planar puddles and UVs.
# Only our ASHFALL terrain prototype is changed; user's original scene remains untouched.
import bpy, random, math
bpy.context.window.scene=workshop
r=assets['terrain']
for ob in list(r.children):
    if ob.name.startswith('rain_puddle'): bpy.data.objects.remove(ob,do_unlink=True)
rand=random.Random(156)
# Multiscale interpolated noise avoids the earlier repeating sinusoidal pattern.
fields={n:[[rand.random() for _ in range(n+1)] for _ in range(n+1)] for n in [3,7,19,57]}
def noise(n,u,v):
    x=u*n;y=v*n;i=min(n-1,int(x));j=min(n-1,int(y));a=x-i;b=y-j;a=a*a*(3-2*a);b=b*b*(3-2*b);f=fields[n]
    return (f[j][i]*(1-a)+f[j][i+1]*a)*(1-b)+(f[j+1][i]*(1-a)+f[j+1][i+1]*a)*b
im=bpy.data.images.new('AF_Earth_nonperiodic_512',width=512,height=512);pixels=[]
for y in range(512):
    for x in range(512):
        u=x/511;v=y/511;value=.65+.38*noise(3,u,v)+.18*noise(7,u,v)+.09*noise(19,u,v)+.055*noise(57,u,v)+rand.random()*.025
        pixels.extend([.18*value,.146*value,.102*value,1])
im.pixels=pixels;im.pack();tex=next(n for n in M['mud'].node_tree.nodes if n.type=='TEX_IMAGE');tex.image=im
for ob in r.children:
    if ob.name.startswith('earth_tile'):
        for loop in ob.data.loops:
            co=ob.data.vertices[loop.vertex_index].co;ob.data.uv_layers.active.data[loop.index].uv=((co.x+24)/48,-co.y/48)
rand=random.Random(17)
for y in [-4,-12,-21,-32,-43]:
    for x in [-1.4,1.5]:
        cx=x+rand.uniform(-.4,.4);length=rand.uniform(.8,1.7);verts=[(cx,y,-.031)]
        for j in range(24):
            a=j*math.tau/24;rr=rand.uniform(.90,1.08);verts.append((cx+math.cos(a)*.48*rr,y+math.sin(a)*length*rr,-.031))
        mesh('rainwater_surface',verts,[(0,j+1,(j+1)%24+1) for j in range(24)],'glass',r)
export_asset('terrain')
bpy.context.window.scene=review
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/ashfall-asset-workshop.blend')
result={'terrain_exported':True,'earth_texture_px':512,'puddle_surfaces':10}
