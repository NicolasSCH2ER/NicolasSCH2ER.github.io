import bpy
import sys
import os
import math
import glob
import numpy as np
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
frames_dir = argv[0]
out_dir = argv[1]
start = int(argv[2]) if len(argv) > 2 else 0
end = int(argv[3]) if len(argv) > 3 else -1
samples = int(argv[4]) if len(argv) > 4 else 64
res_x = int(argv[5]) if len(argv) > 5 else 1280
material = argv[6] if len(argv) > 6 else "water"
show_collider = argv[7] == "1" if len(argv) > 7 else False

os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.npz")))
if end < 0:
    end = len(files) - 1
print(f"[info] {len(files)} frames found, rendering {start}..{end}", flush=True)

# domaine connu (dam scene) pour un cadrage camera stable sur toutes les frames
DOM_LO = np.array([0.0, 0.0, 0.0])
DOM_HI = np.array([1.0, 1.0, 1.0])
center = mathutils.Vector(((DOM_LO + DOM_HI) / 2)[[0, 2, 1]])
radius_scene = 0.75

mesh = bpy.data.meshes.new("Fluid")
obj = bpy.data.objects.new("Fluid", mesh)
scene.collection.objects.link(obj)

mat = bpy.data.materials.new("Fluid")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]

def set_transmission(bsdf, v):
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = v
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = v

if material == "water":
    bsdf.inputs["Base Color"].default_value = (0.04, 0.32, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.04
    set_transmission(bsdf, 0.9)
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.33
elif material == "jelly":
    bsdf.inputs["Base Color"].default_value = (0.85, 0.32, 0.06, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.15
    set_transmission(bsdf, 0.55)
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.4
elif material == "sand":
    bsdf.inputs["Base Color"].default_value = (0.72, 0.58, 0.36, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
    set_transmission(bsdf, 0.0)
obj.data.materials.append(mat)

dist = radius_scene * 2.5
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = center + mathutils.Vector((dist * 0.95, -dist * 1.35, dist * 0.5))
direction = center - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

bpy.ops.mesh.primitive_plane_add(size=radius_scene * 6, location=(center.x, center.y, DOM_LO[1]))
ground = bpy.context.active_object
gmat = bpy.data.materials.new("Ground")
gmat.use_nodes = True
gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1.0)
gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.4
ground.data.materials.append(gmat)

if show_collider:
    # meme rampe que sim_scene.py (scene "collider"), Y-up -> Z-up
    cx, cz = 0.5, 0.5
    y0, y1 = 0.15, 0.42
    hw = 0.42
    p1 = np.array([cx - hw, cz - hw, y0])
    p2 = np.array([cx + hw, cz - hw, y1])
    p3 = np.array([cx + hw, cz + hw, y1])
    p4 = np.array([cx - hw, cz + hw, y0])
    ramp_mesh = bpy.data.meshes.new("Ramp")
    ramp_mesh.from_pydata([tuple(p1), tuple(p2), tuple(p3), tuple(p4)], [], [(0, 1, 2), (0, 2, 3)])
    ramp_mesh.update()
    ramp_obj = bpy.data.objects.new("Ramp", ramp_mesh)
    scene.collection.objects.link(ramp_obj)
    rmat = bpy.data.materials.new("Ramp")
    rmat.use_nodes = True
    rmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.52, 1.0)
    rmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3
    rmat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
    ramp_obj.data.materials.append(rmat)

sun_data = bpy.data.lights.new("Sun", type="SUN")
sun_data.energy = 2.0
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(50), math.radians(8), math.radians(50))
scene.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new("Fill", type="AREA")
fill_data.energy = 25.0
fill_data.size = radius_scene * 2
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.location = center + mathutils.Vector((-dist, -dist * 0.3, dist * 0.5))
scene.collection.objects.link(fill_obj)

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)
bg.inputs[1].default_value = 1.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = samples
scene.cycles.device = 'GPU'
scene.cycles.use_denoising = True
scene.render.resolution_x = res_x
scene.render.resolution_y = int(res_x * 0.625)
scene.render.image_settings.file_format = 'PNG'

import time
t0 = time.time()
for i in range(start, end + 1):
    path = files[i]
    data = np.load(path)
    verts = data["verts"]
    tris = data["tris"]
    if len(verts) == 0 or len(tris) == 0:
        continue
    # Y-up (solveur) -> Z-up (Blender)
    verts_blender = verts[:, [0, 2, 1]]

    mesh.clear_geometry()
    mesh.vertices.add(len(verts_blender))
    mesh.vertices.foreach_set("co", verts_blender.ravel())
    mesh.loops.add(len(tris) * 3)
    mesh.loops.foreach_set("vertex_index", tris.ravel())
    mesh.polygons.add(len(tris))
    mesh.polygons.foreach_set("loop_start", np.arange(0, len(tris) * 3, 3))
    mesh.polygons.foreach_set("loop_total", np.full(len(tris), 3))
    mesh.update(calc_edges=True)
    mesh.shade_smooth()

    scene.render.filepath = os.path.join(out_dir, f"render_{i:04d}.png")
    bpy.ops.render.render(write_still=True)
    elapsed = time.time() - t0
    print(f"[render {i:4d}] {len(verts)} verts {len(tris)} tris  ({elapsed:.1f}s ecoule)", flush=True)

print(f"[done] rendered {end - start + 1} frames in {time.time()-t0:.1f}s", flush=True)
