"""Curled-paper laptop: a demo homepage flows out of the screen, over the keyboard, onto the table and into a scroll.

  blender -b --factory-startup -P paper_laptop.py -- <outdir> <name> <texture.png> <yaw_degrees> [samples]
Renders <outdir>/laptop_<name>.png with a transparent background and a soft contact shadow.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, NAME, TEX, YAW = argv[0], argv[1], argv[2], float(argv[3])
SAMPLES = int(argv[4]) if len(argv) > 4 else 48

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple([x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0])

def mat(name, col, rough=0.4, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = srgb(col); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m

ALU = mat("Alu", "#C9CED1", 0.32, 1.0)
ALU_DARK = mat("AluDark", "#8C9497", 0.4, 1.0)
BEZEL = mat("Bezel", "#121718", 0.25, 0.0, 0.6)
KEYS = mat("Keys", "#2A3033", 0.6)
ROLL = mat("Roll", "#F4F6F6", 0.35, 0.0, 0.5)

# page material: texture on the front, plain white on the back
PAGE = bpy.data.materials.new("Page"); PAGE.use_nodes = True
nt = PAGE.node_tree; b = nt.nodes["Principled BSDF"]
tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(TEX); tx.interpolation = 'Cubic'
tx.extension = 'EXTEND'
nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 0.38
if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.25
em = "Emission Color" if "Emission Color" in b.inputs else "Emission"
nt.links.new(tx.outputs["Color"], b.inputs[em])
if "Emission Strength" in b.inputs: b.inputs["Emission Strength"].default_value = 0.12
# backface white
geo = nt.nodes.new("ShaderNodeNewGeometry"); mix = nt.nodes.new("ShaderNodeMixShader")
wb = nt.nodes.new("ShaderNodeBsdfPrincipled"); wb.inputs["Base Color"].default_value = srgb("#F2F4F4"); wb.inputs["Roughness"].default_value = 0.5
out = nt.nodes["Material Output"]
nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"]); nt.links.new(b.outputs["BSDF"], mix.inputs[1]); nt.links.new(wb.outputs["BSDF"], mix.inputs[2])
nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
iw, ih = tx.image.size

# ------------------------------------------------------------ laptop
ROOT = bpy.data.objects.new("LAPTOP", None); scene.collection.objects.link(ROOT)
def rbox(name, size, loc, m, bevel, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.active_object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    md = o.modifiers.new("b", 'BEVEL'); md.width = bevel; md.segments = 6; md.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); o.parent = ROOT; return o

BW, BD, BH = 3.3, 2.3, 0.11            # base
rbox("base", (BW, BD, BH), (0, 0, BH / 2), ALU, 0.05)
rbox("deck", (BW - 0.5, BD - 0.9, 0.012), (0, 0.2, BH), KEYS, 0.004)        # keyboard well
rbox("pad", (1.1, 0.62, 0.008), (0, -0.78, BH), ALU_DARK, 0.004)           # trackpad
HINGE = Vector((0, BD / 2 - 0.06, BH + 0.02))
LID_H, LID_T, TILT = 2.15, 0.07, math.radians(18)                       # lid leans back 18 deg
up = Vector((0, math.sin(TILT), math.cos(TILT)))
lid_c = HINGE + up * (LID_H / 2) + Vector((0, math.cos(TILT), -math.sin(TILT))) * (LID_T / 2)
rbox("lid", (BW, LID_T, LID_H), lid_c, BEZEL, 0.04, rot=(-TILT, 0, 0))

# ------------------------------------------------------------ paper path (in the YZ plane)
SW = BW - 0.34                                   # sheet width = screen width
L_TOTAL = SW * ih / iw                           # keep the texture's aspect
top = HINGE + up * (LID_H - 0.12) + Vector((0, -math.cos(TILT), math.sin(TILT))) * 0.004
# smooth Catmull-Rom path through control points (y, z)
fwd = Vector((0, -math.cos(TILT), math.sin(TILT))) * 0.006     # just in front of the screen surface
front_y = -BD / 2
ctrl = [
    top + up * 0.5,                                  # phantom (keeps the screen part straight)
    top,
    HINGE + up * (LID_H * 0.5) + fwd,
    HINGE + up * 0.16 + fwd,                         # bottom of the screen
    Vector((0, HINGE.y - 0.42, BH + 0.42)),          # page billows up over the keyboard
    Vector((0, HINGE.y - 1.25, BH + 0.16)),
    Vector((0, front_y + 0.05, BH + 0.06)),          # front edge of the base
    Vector((0, front_y - 0.30, 0.05)),               # drops to the table
    Vector((0, front_y - 0.75, 0.006)),
    Vector((0, front_y - 3.0, 0.006)),
    Vector((0, front_y - 14.0, 0.006)),
    Vector((0, front_y - 20.0, 0.006)),              # phantom
]
def cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
pts = []
for k in range(1, len(ctrl) - 2):
    for i in range(160):
        pts.append(cr(ctrl[k - 1], ctrl[k], ctrl[k + 1], ctrl[k + 2], i / 160))
pts.append(ctrl[-2])
# resample by arc length up to L_TOTAL
cum = [0.0]
for i in range(1, len(pts)): cum.append(cum[-1] + (pts[i] - pts[i - 1]).length)
N = 900; samp = []
j = 0
for k in range(N + 1):
    s = L_TOTAL * k / N
    while j < len(cum) - 2 and cum[j + 1] < s: j += 1
    t = (s - cum[j]) / max(1e-9, cum[j + 1] - cum[j]); samp.append(pts[j].lerp(pts[j + 1], t))
end = samp[-1]

verts, faces, uvs = [], [], []
for k, P in enumerate(samp):
    for xi in (0, 1):
        verts.append((-SW / 2 + SW * xi, P.y, P.z))
for k in range(N):
    a, b2 = 2 * k, 2 * (k + 1); faces.append((a, a + 1, b2 + 1, b2))
me = bpy.data.meshes.new("page"); me.from_pydata(verts, [], faces); me.update()
uvl = me.uv_layers.new()
for poly in me.polygons:
    for li in poly.loop_indices:
        vi = me.loops[li].vertex_index; k, xi = divmod(vi, 2)
        uvl.data[li].uv = (xi, 1 - k / N)
for poly in me.polygons: poly.use_smooth = True
page = bpy.data.objects.new("page", me); scene.collection.objects.link(page); page.parent = ROOT
page.data.materials.append(PAGE)
sol = page.modifiers.new("t", 'SOLIDIFY'); sol.thickness = 0.006; sol.offset = 1

# scroll at the end of the sheet
bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=SW + 0.16, location=(0, end.y - 0.12, 0.17), rotation=(0, math.radians(90), 0), vertices=96)
rl = bpy.context.active_object; rl.data.materials.append(ROLL); rl.parent = ROOT
md = rl.modifiers.new("b", 'BEVEL'); md.width = 0.03; md.segments = 4; md.limit_method = 'ANGLE'
bpy.ops.object.shade_smooth()

ROOT.rotation_euler = (0, 0, math.radians(YAW))

# ------------------------------------------------------------ studio
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); sc = bpy.context.active_object; sc.is_shadow_catcher = True
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = srgb("#EAF2F2"); world.node_tree.nodes["Background"].inputs[1].default_value = 0.55
def area(loc, rot, size, e):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.active_object; l.data.size = size; l.data.energy = e
area((-6, -6, 9), (math.radians(40), 0, math.radians(-40)), 8, 900)
area((7, -4, 6), (math.radians(55), 0, math.radians(55)), 6, 380)
area((0, 6, 7), (math.radians(-40), 0, 0), 6, 300)

bpy.ops.object.camera_add(location=(0, -10.8, 6.4)); cam = bpy.context.active_object
tgt = Vector((0, -1.75, 0.75)); cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50; scene.camera = cam

import addon_utils
try: addon_utils.enable("cycles", default_set=True)
except Exception: pass
scene.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    for dev in ('OPTIX', 'CUDA'):
        try:
            pr.compute_device_type = dev; pr.get_devices()
            for d in pr.devices: d.use = (d.type == dev)
            if any(d.use for d in pr.devices): break
        except Exception: pass
    scene.cycles.device = 'GPU'
except Exception: pass
scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Standard'
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = (int(argv[5]) if len(argv) > 5 else 1400), 1500
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = os.path.join(OUT, f"laptop_{NAME}.png")
bpy.ops.render.render(write_still=True)
print("RENDERED", scene.render.filepath, "sheet length", round(L_TOTAL, 2))
