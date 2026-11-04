"""Scita v20 promo renders - procedural living room with a grey linen 3-seater sofa.

Run headless (does not touch any open Blender session):
  blender -b --factory-startup -P scene.py -- <outdir> <shot> [samples]
shots: room_wide | room_portrait | sofa_34 | sofa_front | sofa_side | coords
"""
import bpy, bmesh, math, random, sys, os, json
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "//"
SHOT = argv[1] if len(argv) > 1 else "room_wide"
SAMPLES = int(argv[2]) if len(argv) > 2 else 128
random.seed(7)

# ---------------------------------------------------------------- reset
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
col = scene.collection

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, 1.0)

def setin(node, names, val):
    for n in (names if isinstance(names, (list, tuple)) else [names]):
        if n in node.inputs:
            node.inputs[n].default_value = val
            return

# ---------------------------------------------------------------- materials
def mat_basic(name, color, rough=0.5, metal=0.0, coat=0.0, sheen=0.0, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    setin(b, "Base Color", srgb(color) if isinstance(color, str) else color)
    setin(b, "Roughness", rough); setin(b, "Metallic", metal)
    setin(b, ["Coat Weight", "Clearcoat"], coat)
    setin(b, ["Sheen Weight", "Sheen"], sheen)
    setin(b, ["Subsurface Weight", "Subsurface"], sss)
    return m, b

def add_bump(m, bsdf, scale=300.0, strength=0.15, detail=8.0, kind="noise"):
    nt = m.node_tree
    if kind == "noise":
        t = nt.nodes.new("ShaderNodeTexNoise"); setin(t, "Scale", scale); setin(t, "Detail", detail)
        out = t.outputs["Fac"]
    else:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        t = nt.nodes.new("ShaderNodeTexWave"); setin(t, "Scale", scale); setin(t, "Distortion", 1.0)
        nt.links.new(tc.outputs["Object"], t.inputs["Vector"]); out = t.outputs["Fac"]
    bump = nt.nodes.new("ShaderNodeBump"); setin(bump, "Strength", strength); setin(bump, "Distance", 0.02)
    nt.links.new(out, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

def fabric(name, color):
    m, b = mat_basic(name, color, rough=0.92, sheen=0.6)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # weave: two perpendicular waves multiplied
    w1 = nt.nodes.new("ShaderNodeTexWave"); w1.wave_type = 'BANDS'; w1.bands_direction = 'X'; setin(w1, "Scale", 220)
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.wave_type = 'BANDS'; w2.bands_direction = 'Y'; setin(w2, "Scale", 220)
    for w in (w1, w2): nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    nt.links.new(w1.outputs["Fac"], mul.inputs[0]); nt.links.new(w2.outputs["Fac"], mul.inputs[1])
    nz = nt.nodes.new("ShaderNodeTexNoise"); setin(nz, "Scale", 40); setin(nz, "Detail", 6)
    add = nt.nodes.new("ShaderNodeMath"); add.operation = 'ADD'
    nt.links.new(mul.outputs[0], add.inputs[0]); nt.links.new(nz.outputs["Fac"], add.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump"); setin(bump, "Strength", 0.25); setin(bump, "Distance", 0.01)
    nt.links.new(add.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    # subtle colour variation
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    c = srgb(color); dark = tuple(x * 0.82 for x in c[:3]) + (1,)
    ramp.color_ramp.elements[0].color = dark; ramp.color_ramp.elements[1].color = c
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m

M = {}
M["linen"] = fabric("Linen", "#8C8983")
M["pillow_teal"] = fabric("PillowTeal", "#1D6A6D")
M["pillow_sand"] = fabric("PillowSand", "#C9AE86")
M["metal"], _ = mat_basic("BlackMetal", "#1B1B1B", rough=0.35, metal=1.0)
M["brass"], _ = mat_basic("Brass", "#C59A5A", rough=0.25, metal=1.0)
m, b = mat_basic("Wall", "#DCD3C7", rough=0.95); add_bump(m, b, 25, 0.06); M["wall"] = m
m, b = mat_basic("Rug", "#D9D2C6", rough=1.0, sheen=0.5); add_bump(m, b, 220, 0.6); M["rug"] = m
m, b = mat_basic("Marble", "#F1EEE9", rough=0.12, coat=0.6)
nt = m.node_tree; tc = nt.nodes.new("ShaderNodeTexCoord")
wv = nt.nodes.new("ShaderNodeTexWave"); setin(wv, "Scale", 1.6); setin(wv, "Distortion", 14); setin(wv, "Detail", 10)
nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[1].position = 0.08
rp.color_ramp.elements[0].color = srgb("#9C968E"); rp.color_ramp.elements[1].color = srgb("#F3F0EB")
nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
M["marble"] = m
# oak floor - brick texture as planks
m, b = mat_basic("Oak", "#C9A57C", rough=0.45, coat=0.2); nt = m.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Scale"].default_value = (3.4, 0.42, 1)
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
br = nt.nodes.new("ShaderNodeTexBrick"); setin(br, "Scale", 2.2); setin(br, "Mortar Size", 0.004)
br.offset = 0.37
setin(br, "Color1", srgb("#C8A178")); setin(br, "Color2", srgb("#B88D63")); setin(br, "Mortar", srgb("#7A5A3C"))
nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
gr = nt.nodes.new("ShaderNodeTexWave"); setin(gr, "Scale", 9); setin(gr, "Distortion", 6); gr.bands_direction = 'X'
nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
mix.inputs["Factor"].default_value = 0.18
nt.links.new(br.outputs["Color"], mix.inputs[6]); nt.links.new(gr.outputs["Color"], mix.inputs[7])
nt.links.new(mix.outputs[2], b.inputs["Base Color"])
M["oak"] = m
M["leaf"], _ = mat_basic("Leaf", "#2E5530", rough=0.4, sss=0.1)
M["pot"], _ = mat_basic("Pot", "#E8E2D8", rough=0.6)
M["ceramic"], _ = mat_basic("Ceramic", "#0F5C61", rough=0.2, coat=0.5)
M["book1"], _ = mat_basic("Book1", "#D8CBB5", rough=0.7)
M["book2"], _ = mat_basic("Book2", "#2F4F4F", rough=0.7)
M["shade"], sb = mat_basic("Shade", "#F4EEE3", rough=0.8, sss=0.4)
M["frame"], _ = mat_basic("Frame", "#2A2622", rough=0.5)
# wall art: abstract teal / green / sand arcs
m, b = mat_basic("Art", "#EDE6DA", rough=0.85); nt = m.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord"); grd = nt.nodes.new("ShaderNodeTexGradient"); grd.gradient_type = 'SPHERICAL'
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (-0.15, 0.0, -0.25)
mp.inputs["Scale"].default_value = (2.2, 2.2, 2.2)
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], grd.inputs["Vector"])
rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = 'CONSTANT'
els = rp.color_ramp.elements; els[0].position = 0.0; els[0].color = srgb("#EDE6DA"); els[1].position = 0.35; els[1].color = srgb("#017E84")
e = els.new(0.55); e.color = srgb("#81C54C"); e = els.new(0.7); e.color = srgb("#D7C3A3"); e = els.new(0.85); e.color = srgb("#EDE6DA")
nt.links.new(grd.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
M["art"] = m

# ---------------------------------------------------------------- geometry helpers
def box(name, size, loc, mat, bevel=0.0, segs=4, rot=(0, 0, 0), subsurf=0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        md = o.modifiers.new("Bevel", 'BEVEL'); md.width = bevel; md.segments = segs; md.limit_method = 'NONE'
    if subsurf:
        md = o.modifiers.new("Sub", 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    if parent: o.parent = parent
    return o

def cyl(name, r, h, loc, mat, verts=48, r2=None, rot=(0, 0, 0), bevel=0.0, smooth=True, parent=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, location=loc, vertices=verts, rotation=rot)
    o = bpy.context.active_object; o.name = name
    if bevel:
        md = o.modifiers.new("Bevel", 'BEVEL'); md.width = bevel; md.segments = 3; md.limit_method = 'ANGLE'
    if smooth:
        try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        except Exception: bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    if parent: o.parent = parent
    return o

def cushion(name, size, loc, mat, rot=(0, 0, 0), puff=0.02, parent=None):
    """Soft cushion: beveled box + subsurf + slight inflation via displace."""
    o = box(name, size, loc, mat, bevel=min(size) * 0.38, segs=6, rot=rot, subsurf=1, parent=parent)
    tex = bpy.data.textures.new(name + "_puff", 'CLOUDS'); tex.noise_scale = 0.6
    d = o.modifiers.new("Puff", 'DISPLACE'); d.texture = tex; d.strength = puff; d.mid_level = 0.5
    return o

# ---------------------------------------------------------------- sofa (origin centre-floor, faces -Y)
bpy.ops.object.empty_add(location=(0, 0, 0)); SOFA = bpy.context.active_object; SOFA.name = "SOFA"
W, D = 2.24, 0.96
LEG_H = 0.13
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl("leg", 0.017, LEG_H, (sx * (W / 2 - 0.12), sy * (D / 2 - 0.12), LEG_H / 2), M["metal"], verts=24, r2=0.012, parent=SOFA)
base_z0 = LEG_H
box("plinth", (W - 0.04, D - 0.04, 0.2), (0, 0, base_z0 + 0.1), M["linen"], bevel=0.035, segs=5, parent=SOFA)
ARM_W = 0.22
for sx in (-1, 1):
    cushion("arm", (ARM_W, D, 0.5), (sx * (W / 2 - ARM_W / 2), 0, base_z0 + 0.25), M["linen"], puff=0.012, parent=SOFA)
inner = W - 2 * ARM_W
box("backframe", (inner, 0.2, 0.52), (0, D / 2 - 0.1, base_z0 + 0.2 + 0.26), M["linen"], bevel=0.05, segs=6, parent=SOFA)
seat_z = base_z0 + 0.2 + 0.085
cw = inner / 3
for i in range(3):
    x = -inner / 2 + cw * (i + 0.5)
    cushion(f"seat{i}", (cw - 0.012, D - 0.24, 0.17), (x, -0.1, seat_z), M["linen"], puff=0.015, parent=SOFA)
    cushion(f"back{i}", (cw - 0.02, 0.2, 0.46), (x, D / 2 - 0.25, seat_z + 0.3), M["linen"], rot=(math.radians(-11), 0, 0), puff=0.02, parent=SOFA)
cushion("pillowA", (0.44, 0.13, 0.42), (-inner / 2 + 0.32, D / 2 - 0.42, seat_z + 0.27), M["pillow_teal"], rot=(math.radians(-16), 0, math.radians(14)), puff=0.025, parent=SOFA)
cushion("pillowB", (0.42, 0.13, 0.40), (inner / 2 - 0.3, D / 2 - 0.42, seat_z + 0.26), M["pillow_sand"], rot=(math.radians(-16), 0, math.radians(-12)), puff=0.025, parent=SOFA)
SOFA_PARTS = [o for o in bpy.data.objects if o.parent == SOFA] + [SOFA]

# ---------------------------------------------------------------- room
ROOM = []
def R(o): ROOM.append(o); return o
R(box("floor", (14, 14, 0.02), (0, -3, -0.01), M["oak"]))
WALL_Y = D / 2 + 0.32
R(box("wall", (14, 0.1, 6), (0, WALL_Y + 0.05, 3), M["wall"]))
R(box("skirting", (14, 0.02, 0.09), (0, WALL_Y - 0.01, 0.045), M["wall"]))
R(box("rug", (3.2, 2.3, 0.012), (0, -0.55, 0.006), M["rug"], bevel=0.005, segs=2))
# coffee table: round marble on black pedestal
TBL = (0.15, -1.05)
R(cyl("table_top", 0.46, 0.035, (TBL[0], TBL[1], 0.40), M["marble"], verts=96, bevel=0.008))
R(cyl("table_base", 0.16, 0.36, (TBL[0], TBL[1], 0.20), M["metal"], verts=64, r2=0.09))
R(cyl("table_foot", 0.24, 0.02, (TBL[0], TBL[1], 0.01), M["metal"], verts=64, bevel=0.005))
# decor on table
R(box("book_a", (0.26, 0.19, 0.03), (TBL[0] - 0.12, TBL[1] + 0.05, 0.432), M["book1"], bevel=0.004, segs=2, rot=(0, 0, math.radians(12))))
R(box("book_b", (0.23, 0.17, 0.025), (TBL[0] - 0.12, TBL[1] + 0.05, 0.459), M["book2"], bevel=0.004, segs=2, rot=(0, 0, math.radians(4))))
vase = R(cyl("vase", 0.055, 0.2, (TBL[0] + 0.17, TBL[1] - 0.04, 0.518), M["ceramic"], verts=48, r2=0.035))
sm = vase.modifiers.new("Sub", 'SUBSURF'); sm.levels = 2; sm.render_levels = 2
# floor lamp (right)
LX = W / 2 + 0.45
R(cyl("lamp_base", 0.16, 0.025, (LX, 0.15, 0.0125), M["metal"], verts=64, bevel=0.006))
R(cyl("lamp_pole", 0.011, 1.5, (LX, 0.15, 0.76), M["brass"], verts=24))
shade = R(cyl("lamp_shade", 0.24, 0.3, (LX, 0.15, 1.6), M["shade"], verts=64, r2=0.17))
# side table + plant (left)
PX = -W / 2 - 0.5
R(cyl("planter", 0.2, 0.42, (PX, 0.05, 0.21), M["pot"], verts=64, r2=0.24, bevel=0.01))
for i in range(46):
    ang = random.uniform(0, 2 * math.pi); tilt = random.uniform(0.25, 1.05)
    h = random.uniform(0.55, 1.35); L = random.uniform(0.22, 0.34)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=24, ring_count=12)
    lf = bpy.context.active_object; lf.name = "leaf"
    lf.scale = (L * 0.5, L * 1.15, 0.008)
    bpy.ops.object.transform_apply(scale=True)
    # bend leaf
    bd = lf.modifiers.new("Bend", 'SIMPLE_DEFORM'); bd.deform_method = 'BEND'; bd.angle = math.radians(random.uniform(20, 45)); bd.deform_axis = 'X'
    r = 0.06 + math.sin(tilt) * L * 0.6
    lf.location = (PX + math.cos(ang) * r, 0.05 + math.sin(ang) * r, 0.42 + h * 0.7)
    lf.rotation_euler = Euler((tilt, 0, ang - math.pi / 2), 'XYZ')
    bpy.ops.object.shade_smooth(); lf.data.materials.append(M["leaf"]); R(lf)
    # stem
    bpy.ops.curve.primitive_bezier_curve_add()
    st = bpy.context.active_object; st.name = "stem"; st.data.bevel_depth = 0.004
    p = st.data.splines[0].bezier_points
    p[0].co = Vector((PX, 0.05, 0.4)); p[0].handle_left = p[0].co; p[0].handle_right = p[0].co + Vector((0, 0, 0.2))
    p[1].co = lf.location.copy(); p[1].handle_left = p[1].co - Vector((0, 0, 0.15)); p[1].handle_right = p[1].co
    st.data.materials.append(M["leaf"]); R(st)
# wall art
ART_Z = 1.62
R(box("art_frame", (1.0, 0.035, 0.72), (0.0, WALL_Y - 0.02, ART_Z), M["frame"], bevel=0.004, segs=2))
M["paper"], _ = mat_basic("Paper", "#EFE9DF", rough=0.9)
M["art_teal"], _ = mat_basic("ArtTeal", "#017E84", rough=0.8)
M["art_green"], _ = mat_basic("ArtGreen", "#81C54C", rough=0.8)
M["art_sand"], _ = mat_basic("ArtSand", "#D9B98C", rough=0.8)
M["art_ink"], _ = mat_basic("ArtInk", "#0F5C61", rough=0.8)
AY = WALL_Y - 0.04
R(box("art_paper", (0.94, 0.004, 0.66), (0.0, AY, ART_Z), M["paper"]))
def disc(name, r, x, z, mat, depth, half=False):
    o = cyl(name, r, 0.003, (x, AY - depth, z), mat, verts=96, rot=(math.radians(90), 0, 0), smooth=False)
    if half:
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.0001], context='VERTS')
        bm.to_mesh(o.data); bm.free()
    return R(o)
disc("a1", 0.2, -0.17, ART_Z - 0.06, M["art_teal"], 0.004)
disc("a2", 0.1, 0.12, ART_Z - 0.2, M["art_green"], 0.006)
R(box("a3", (0.22, 0.003, 0.30), (0.25, AY - 0.005, ART_Z + 0.08), M["art_sand"]))
disc("a4", 0.05, 0.05, ART_Z + 0.17, M["art_ink"], 0.008)

# ---------------------------------------------------------------- lighting / world
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes.get("Background"); bg.inputs[0].default_value = srgb("#DCE6EA"); bg.inputs[1].default_value = 0.38

def area(name, loc, rot, size, power, color="#FFF4E6", shape='RECTANGLE', sy=None):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.active_object; l.name = name; l.data.shape = shape
    l.data.size = size; l.data.size_y = sy or size; l.data.energy = power; l.data.color = srgb(color)[:3]
    return l
KEY = area("key", (-3.2, -2.6, 2.8), (math.radians(60), 0, math.radians(-50)), 2.4, 650, "#FFE9CF", sy=1.8)
KEY.data.energy = 420
FILL = area("fill", (3.5, -3.0, 2.0), (math.radians(70), 0, math.radians(48)), 3.0, 110, "#E6F0FF")
TOP = area("top", (0, -1.0, 4.2), (0, 0, 0), 3.0, 70, "#FFFFFF")
bpy.ops.object.light_add(type='POINT', location=(LX, 0.15, 1.6)); lb = bpy.context.active_object
lb.data.energy = 25; lb.data.color = srgb("#FFD9A0")[:3]; lb.data.shadow_soft_size = 0.08
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(52), math.radians(8), math.radians(-38)))
sun = bpy.context.active_object; sun.data.energy = 2.2; sun.data.angle = math.radians(3); sun.data.color = srgb("#FFE2BD")[:3]
ROOM_LIGHTS = [lb]

# ---------------------------------------------------------------- render settings
import addon_utils
try: addon_utils.enable("cycles", default_set=True)
except Exception as e: print("cycles enable", e)
scene.render.engine = 'CYCLES'
cy = scene.cycles
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    for dev in ('OPTIX', 'CUDA'):
        try:
            pr.compute_device_type = dev; pr.get_devices()
            for d in pr.devices: d.use = (d.type == dev)
            if any(d.use for d in pr.devices): break
        except Exception: pass
    cy.device = 'GPU'
except Exception as e:
    print("gpu", e)
cy.samples = SAMPLES; cy.use_denoising = True
try: cy.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
cy.max_bounces = 8
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# ---------------------------------------------------------------- cameras
def camera(loc, target, lens=35, res=(1800, 1100)):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.active_object
    d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens; scene.camera = c
    scene.render.resolution_x, scene.render.resolution_y = res; scene.render.resolution_percentage = 100
    c.data.dof.use_dof = False
    return c

def hide(objs, flag=True):
    for o in objs:
        o.hide_render = flag

def shadow_catcher():
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0)); p = bpy.context.active_object
    p.is_shadow_catcher = True; return p

if SHOT in ("room_wide", "coords"):
    cam = camera((0.55, -4.35, 1.28), (-0.05, 0.0, 0.62), lens=33, res=(1800, 1100))
elif SHOT == "tile_ai":
    cam = camera((0.3, -3.55, 1.3), (0.0, -0.3, 0.98), lens=33, res=(900, 1480))
    cam.data.sensor_fit = 'HORIZONTAL'
elif SHOT == "room_portrait":
    cam = camera((-1.15, -3.0, 1.15), (0.25, 0.0, 0.55), lens=26, res=(1000, 1700))
else:
    hide([o for o in bpy.data.objects if o not in SOFA_PARTS and o.type != 'LIGHT'])
    hide(ROOM_LIGHTS)
    shadow_catcher(); scene.render.film_transparent = True
    world.node_tree.nodes.get("Background").inputs[1].default_value = 0.9
    pos = {"sofa_34": (-2.9, -3.6, 1.55), "sofa_front": (0.0, -4.4, 1.25), "sofa_side": (3.1, -3.4, 1.5)}[SHOT]
    cam = camera(pos, (0, 0, 0.42), lens=42, res=(1400, 900))

# ---------------------------------------------------------------- hotspot coordinates (for HTML overlay)
if SHOT in ("room_wide", "room_portrait", "coords", "tile_ai"):
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    pts = {"sofa": (0.0, -0.15, seat_z + 0.1), "pillow": (-inner / 2 + 0.32, D / 2 - 0.45, seat_z + 0.3),
           "table": (TBL[0], TBL[1], 0.42), "sofa_l": (-W / 2, -D / 2, base_z0 + 0.62), "sofa_r": (W / 2, -D / 2, base_z0 + 0.62), "sofa_floor": (0, -0.1, 0.0), "lamp": (LX, 0.15, 1.6), "plant": (PX, 0.05, 1.0), "art": (0.0, WALL_Y, ART_Z)}
    out = {}
    for k, p in pts.items():
        v = world_to_camera_view(scene, scene.camera, Vector(p))
        out[k] = [round(v.x * 100, 2), round((1 - v.y) * 100, 2)]
    print("HOTSPOTS", SHOT, json.dumps(out))
    with open(os.path.join(OUT, f"{SHOT}_hotspots.json"), "w") as f: json.dump(out, f)

if SHOT != "coords":
    scene.render.filepath = os.path.join(OUT, SHOT + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)
