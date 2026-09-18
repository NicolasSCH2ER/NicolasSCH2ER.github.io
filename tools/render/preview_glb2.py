import bpy
import sys
import math
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
glb_path = argv[0]
out_path = argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb_path)

for obj in scene.objects:
    print("OBJ", obj.name, obj.type, obj.dimensions, obj.location)

# domaine connu = [0,1]^3, camera fixe manuelle (pas d'auto-fit, peu fiable)
center = mathutils.Vector((0.5, 0.25, 0.5))
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 40
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = center + mathutils.Vector((1.1, 0.9, 1.4))
direction = center - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

sun_data = bpy.data.lights.new("Sun", type="SUN")
sun_data.energy = 3.5
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(50), math.radians(10), math.radians(60))
scene.collection.objects.link(sun_obj)

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.05, 0.06, 1.0)
bg.inputs[1].default_value = 1.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.filepath = out_path
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print(f"[done] {out_path}")
