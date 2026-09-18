import bpy
import sys
import numpy as np
import bmesh

argv = sys.argv[sys.argv.index("--") + 1:]
npz_path = argv[0]
out_path = argv[1]
target_tris = int(argv[2]) if len(argv) > 2 else 30000

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

data = np.load(npz_path)
verts = data["verts"].astype(np.float64)
tris = data["tris"].astype(np.int64)
print(f"[info] source: {len(verts)} verts, {len(tris)} tris", flush=True)

mesh = bpy.data.meshes.new("Fluid")
mesh.vertices.add(len(verts))
mesh.vertices.foreach_set("co", verts.ravel())
mesh.loops.add(len(tris) * 3)
mesh.loops.foreach_set("vertex_index", tris.ravel())
mesh.polygons.add(len(tris))
mesh.polygons.foreach_set("loop_start", np.arange(0, len(tris) * 3, 3, dtype=np.int64))
mesh.polygons.foreach_set("loop_total", np.full(len(tris), 3, dtype=np.int64))
mesh.update()
mesh.validate()

obj = bpy.data.objects.new("Fluid", mesh)
scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# decimation : le maillage source (marching cubes du mailleur natif) est bien
# trop lourd pour un viewer web temps reel -> collapse vers ~target_tris
ratio = min(1.0, target_tris / max(1, len(tris)))
dec = obj.modifiers.new("Decimate", "DECIMATE")
dec.ratio = ratio
bpy.ops.object.modifier_apply(modifier=dec.name)
print(f"[info] decimated: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys", flush=True)

bpy.ops.object.shade_smooth()

# rampe collider : coordonnees EXACTES de sim_scene.py (--scene collider),
# domaine [0,1]^3, sinon echelle/position ne correspondent plus au maillage fluide
cx, cz = 0.5, 0.5
y0, y1 = 0.15, 0.42
hw = 0.42
th = 0.03
t1 = (cx - hw, y0, cz - hw)
t2 = (cx + hw, y1, cz - hw)
t3 = (cx + hw, y1, cz + hw)
t4 = (cx - hw, y0, cz + hw)
b1, b2, b3, b4 = ((p[0], p[1] - th, p[2]) for p in (t1, t2, t3, t4))
ramp_verts = [t1, t2, t3, t4, b1, b2, b3, b4]
ramp_faces = [
    (0, 2, 1), (0, 3, 2),        # dessus
    (7, 5, 4), (7, 6, 5),        # dessous
    (0, 1, 5), (0, 5, 4),        # cote z-
    (1, 2, 6), (1, 6, 5),        # cote x+
    (2, 3, 7), (2, 7, 6),        # cote z+
    (3, 0, 4), (3, 4, 7),        # cote x-
]
ramp_mesh = bpy.data.meshes.new("Ramp")
ramp_mesh.from_pydata(ramp_verts, [], ramp_faces)
ramp_mesh.update()
ramp_obj = bpy.data.objects.new("Ramp", ramp_mesh)
scene.collection.objects.link(ramp_obj)

fluid_mat = bpy.data.materials.new("FluidMat")
fluid_mat.use_nodes = True
bsdf = fluid_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.15, 0.45, 0.75, 1.0)
if "Roughness" in bsdf.inputs:
    bsdf.inputs["Roughness"].default_value = 0.15
if "Transmission Weight" in bsdf.inputs:
    bsdf.inputs["Transmission Weight"].default_value = 0.55
elif "Transmission" in bsdf.inputs:
    bsdf.inputs["Transmission"].default_value = 0.55
obj.data.materials.append(fluid_mat)

ramp_mat = bpy.data.materials.new("RampMat")
ramp_mat.use_nodes = True
bsdf2 = ramp_mat.node_tree.nodes["Principled BSDF"]
bsdf2.inputs["Base Color"].default_value = (0.55, 0.52, 0.48, 1.0)
if "Roughness" in bsdf2.inputs:
    bsdf2.inputs["Roughness"].default_value = 0.6
if "Metallic" in bsdf2.inputs:
    bsdf2.inputs["Metallic"].default_value = 0.1
ramp_obj.data.materials.append(ramp_mat)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_yup=True,
)
print(f"[done] exported to {out_path}", flush=True)
