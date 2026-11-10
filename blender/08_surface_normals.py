# Repair the initial ground winding in the existing authored prototype.
# Stage 04 now creates upward normals directly; this stage is idempotent for old workshops.
import bpy
bpy.context.window.scene=workshop
corrected=0
for ob in assets['terrain'].children:
    if ob.type=='MESH' and ob.name.startswith('earth_tile'):
        for face in ob.data.polygons:
            if face.normal.z<0: face.flip();corrected+=1
        ob.data.update()
export_asset('terrain')
bpy.context.window.scene=review
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/ashfall-asset-workshop.blend')
result={'earth_faces_corrected':corrected,'surface_normal':'upward'}
