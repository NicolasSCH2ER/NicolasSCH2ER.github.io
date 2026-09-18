import bpy
import sys
import math
import numpy as np
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
npz_path = argv[0]
out_path = argv[1]
# teinte de base (h, s adapte via HSV) pour differencier les 3 sets
hue = float(argv[2]) if len(argv) > 2 else 0.08

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

data = np.load(npz_path)
verts = data["verts"]
faces = data["faces"]
print(f"[info] {npz_path}: {len(verts)} verts, {len(faces)} faces", flush=True)

mesh = bpy.data.meshes.new("Julia")
mesh.vertices.add(len(verts))
mesh.vertices.foreach_set("co", verts.ravel())
loop_start = np.arange(0, len(faces) * 3, 3, dtype=np.int64)
loop_total = np.full(len(faces), 3, dtype=np.int64)
mesh.loops.add(len(faces) * 3)
mesh.loops.foreach_set("vertex_index", faces.ravel())
mesh.polygons.add(len(faces))
mesh.polygons.foreach_set("loop_start", loop_start)
mesh.polygons.foreach_set("loop_total", loop_total)
mesh.update()
mesh.validate()

obj = bpy.data.objects.new("Julia", mesh)
scene.collection.objects.link(obj)

# recentre l'objet sur son centre de masse (les fractales ne sont pas toujours centrees a l'origine)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new("JuliaMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
c = mathutils.Color()
c.hsv = (hue, 0.65, 0.85)
bsdf.inputs["Base Color"].default_value = (c.r, c.g, c.b, 1.0)
if "Metallic" in bsdf.inputs:
    bsdf.inputs["Metallic"].default_value = 0.25
if "Roughness" in bsdf.inputs:
    bsdf.inputs["Roughness"].default_value = 0.28
obj.data.materials.append(mat)

min_co = mathutils.Vector((1e9,) * 3)
max_co = mathutils.Vector((-1e9,) * 3)
for v in verts:
    for i in range(3):
        min_co[i] = min(min_co[i], v[i])
        max_co[i] = max(max_co[i], v[i])
center = (min_co + max_co) / 2
size = max_co - min_co
radius = max(size.x, size.y, size.z, 0.5)

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
dist = radius * 2.4
cam_obj.location = center + mathutils.Vector((dist * 0.9, -dist * 1.1, dist * 0.5))
direction = center - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

sun_data = bpy.data.lights.new("Sun", type="SUN")
sun_data.energy = 3.5
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(55))
scene.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new("Fill", type="AREA")
fill_data.energy = 90.0
fill_data.size = radius * 2
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.location = center + mathutils.Vector((-dist, -dist * 0.3, dist * 0.4))
scene.collection.objects.link(fill_obj)

rim_data = bpy.data.lights.new("Rim", type="AREA")
rim_data.energy = 60.0
rim_data.size = radius * 1.5
rim_obj = bpy.data.objects.new("Rim", rim_data)
rim_obj.location = center + mathutils.Vector((dist * 0.2, dist * 1.3, dist * 0.6))
scene.collection.objects.link(rim_obj)

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.03, 0.03, 0.035, 1.0)
bg.inputs[1].default_value = 1.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'
scene.render.resolution_x = 2560
scene.render.resolution_y = 1600
scene.render.filepath = out_path
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(write_still=True)
print(f"[done] rendered to {out_path}", flush=True)
