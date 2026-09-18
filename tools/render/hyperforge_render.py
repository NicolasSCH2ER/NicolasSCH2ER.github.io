import bpy
import sys
import os
import math
import bmesh
import numpy as np
import mathutils

HYPERFORGE_DIR = r"C:\Users\nicol\Code\hyperforge"
sys.path.insert(0, HYPERFORGE_DIR)

import polytopes
import math4d
import slicing

argv = sys.argv[sys.argv.index("--") + 1:]
out_path = argv[0]
primitive = argv[1] if len(argv) > 1 else "cell120"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

verts4, edges = polytopes.get(primitive)
print(f"[info] {primitive}: {len(verts4)} verts, {len(edges)} edges", flush=True)

# Rotation "sommet en premier" pour un morphing/angle visuellement riche
angles = {
    "a_xw": math.radians(35.0),
    "a_yw": math.atan(1.0 / math.sqrt(2.0)),
    "a_zw": math.atan(1.0 / math.sqrt(3.0)),
    "a_xy": math.radians(20.0),
}
matrix = math4d.compose({
    "XY": angles.get("a_xy", 0.0), "XZ": 0.0, "YZ": 0.0,
    "XW": angles.get("a_xw", 0.0), "YW": angles.get("a_yw", 0.0), "ZW": angles.get("a_zw", 0.0),
})
v4 = math4d.transform(verts4, matrix)
v3 = slicing.project_perspective(v4, dist=3.0)

# construit un mesh "tube" en dur (sans Geometry Nodes) : chaque arete -> cylindre, chaque sommet -> sphere
bm = bmesh.new()
radius_edge = 0.02
radius_vert = 0.035
EDGE_SEGMENTS = 24
VERT_SEGMENTS = 20
VERT_RINGS = 12

def add_cylinder(bm, p1, p2, r, segments=EDGE_SEGMENTS):
    v1 = mathutils.Vector(p1)
    v2 = mathutils.Vector(p2)
    axis = v2 - v1
    length = axis.length
    if length < 1e-9:
        return
    mesh = bpy.data.meshes.new("tmp_cyl")
    bm_tmp = bmesh.new()
    bmesh.ops.create_cone(bm_tmp, cap_ends=True, cap_tris=False, segments=segments,
                           radius1=r, radius2=r, depth=length)
    rot = axis.to_track_quat('Z', 'Y')
    for v in bm_tmp.verts:
        v.co = rot @ v.co
        v.co += (v1 + v2) / 2
    bm_tmp.to_mesh(mesh)
    bm_tmp.free()
    bm.from_mesh(mesh)
    bpy.data.meshes.remove(mesh)

def add_sphere(bm, center, r, segments=VERT_SEGMENTS, rings=VERT_RINGS):
    mesh = bpy.data.meshes.new("tmp_sph")
    bm_tmp = bmesh.new()
    bmesh.ops.create_uvsphere(bm_tmp, u_segments=segments, v_segments=rings, radius=r)
    for v in bm_tmp.verts:
        v.co += mathutils.Vector(center)
    bm_tmp.to_mesh(mesh)
    bm_tmp.free()
    bm.from_mesh(mesh)
    bpy.data.meshes.remove(mesh)

for a, b in edges:
    add_cylinder(bm, v3[a], v3[b], radius_edge)
for p in v3:
    add_sphere(bm, p, radius_vert)

mesh = bpy.data.meshes.new("Hyperforge")
bm.to_mesh(mesh)
bm.free()
mesh.update()

obj = bpy.data.objects.new("Hyperforge", mesh)
scene.collection.objects.link(obj)

mat = bpy.data.materials.new("HyperMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.85, 0.35, 0.08, 1.0)
if "Metallic" in bsdf.inputs:
    bsdf.inputs["Metallic"].default_value = 0.15
if "Roughness" in bsdf.inputs:
    bsdf.inputs["Roughness"].default_value = 0.35
obj.data.materials.append(mat)

# camera framing
min_co = mathutils.Vector((1e9,) * 3)
max_co = mathutils.Vector((-1e9,) * 3)
for v in v3:
    for i in range(3):
        min_co[i] = min(min_co[i], v[i])
        max_co[i] = max(max_co[i], v[i])
center = (min_co + max_co) / 2
size = max_co - min_co
radius = max(size.x, size.y, size.z, 1.0)

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
dist = radius * 2.6
cam_obj.location = center + mathutils.Vector((dist * 0.85, -dist * 1.2, dist * 0.55))
direction = center - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

sun_data = bpy.data.lights.new("Sun", type="SUN")
sun_data.energy = 4.0
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(60))
scene.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new("Fill", type="AREA")
fill_data.energy = 80.0
fill_data.size = radius * 2
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.location = center + mathutils.Vector((-dist, -dist * 0.3, dist * 0.4))
scene.collection.objects.link(fill_obj)

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
