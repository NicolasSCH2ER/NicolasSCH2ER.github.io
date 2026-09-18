import bpy
import sys
import os
import math
import bmesh
import mathutils

HYPERFORGE_DIR = r"C:\Users\nicol\Code\hyperforge"
sys.path.insert(0, HYPERFORGE_DIR)
import polytopes
import math4d
import slicing

argv = sys.argv[sys.argv.index("--") + 1:]
out_path = argv[0]
primitive = argv[1] if len(argv) > 1 else "cell8"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

verts4, edges = polytopes.get(primitive)
print(f"[info] {primitive}: {len(verts4)} verts, {len(edges)} edges", flush=True)

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

# maillage volontairement leger (viewer web temps reel, pas un rendu figure)
bm = bmesh.new()
radius_edge = 0.02
radius_vert = 0.035
EDGE_SEGMENTS = 10
VERT_SEGMENTS = 10
VERT_RINGS = 6

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
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new("HyperMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.85, 0.35, 0.08, 1.0)
if "Metallic" in bsdf.inputs:
    bsdf.inputs["Metallic"].default_value = 0.15
if "Roughness" in bsdf.inputs:
    bsdf.inputs["Roughness"].default_value = 0.35
obj.data.materials.append(mat)

print(f"[info] mesh: {len(mesh.vertices)} verts, {len(mesh.polygons)} polys", flush=True)

bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_yup=True,
)
print(f"[done] exported to {out_path}", flush=True)
