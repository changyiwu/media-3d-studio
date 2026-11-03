"""在 Blender 裡建場景、把動畫逐格烘成 F-Curve、算透明背景的逐格 PNG。

    blender -b --factory-startup -P shots.py -- --out <輸出資料夾> [--scale 0.25 --samples 8 --step 6]

預覽：--scale 0.25 --samples 8 --step 6（每 6 格算一張、關動態模糊）
正式：--scale 1 --samples 64 --step 1 --motion-blur
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R))
import timeline as T  # noqa: E402


# ---------- 緩動函式 ----------

def clamp01(t):
    return max(0.0, min(1.0, t))


def ease_io(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def ease_out_bounce(t):
    t = clamp01(t)
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


def lerp(a, b, t):
    return a + (b - a) * t


# ---------- 格數 → 數值 ----------

def camera_at(f):
    """回傳 (位置, 尤拉角, 焦距)。"""
    keys = T.CAMERA
    for (f0, p0, l0, z0), (f1, p1, l1, z1) in zip(keys, keys[1:]):
        if f0 <= f <= f1:
            t = ease_io((f - f0) / (f1 - f0))
            break
    else:
        (f0, p0, l0, z0) = (f1, p1, l1, z1) = keys[-1]
        t = 0.0
    pos = Vector(p0).lerp(Vector(p1), t)
    look = Vector(l0).lerp(Vector(l1), t)
    rot = (look - pos).to_track_quat("-Z", "Y").to_euler()
    return pos, rot, lerp(z0, z1, t)


SIZE = 1.6  # 方塊邊長


def body_at(f):
    """回傳 (高度 z, 縮放 (x, y, z), 繞 z 旋轉)。z 是方塊底面的高度。"""
    a, b = T.seg("開場")
    if f < b:
        # 從 6 m 高落下、彈跳後站穩，前 2/3 小節落地
        t = (f - a) / ((b - a) * 2 / 3)
        z = 6.0 * (1 - ease_out_bounce(t))
        return z, (1, 1, 1), 0.0

    rz = 0.0
    z = 0.0
    sq = 0.0  # >0 壓扁、<0 拉長
    for i, h in enumerate(T.HOPS):
        if h <= f < h + T.HOP_LEN:
            t = (f - h) / T.HOP_LEN
            z = T.HOP_HEIGHT * 4 * t * (1 - t)          # 拋物線
            sq = -0.12 * math.sin(math.pi * t)           # 空中拉長
            if i == len(T.HOPS) - 1:
                rz = 2 * math.pi * ease_io(t)            # 最後一跳轉一圈
        elif h + T.HOP_LEN <= f < h + T.HOP_LEN + 4:
            sq = 0.18 * (1 - (f - h - T.HOP_LEN) / 4)    # 落地壓扁

    a, b = T.seg("標題")
    if a <= f < b:
        # 跟著拍子點頭：每拍開頭壓一下
        sq = 0.1 * math.exp(-((f - a) % T.BEAT) / 3)

    sx = 1 + sq * 0.5
    return z, (sx, sx, 1 - sq), rz


def blink_at(f):
    return 0.1 if any(b <= f < b + 3 for b in T.BLINKS) else 1.0


# ---------- 建場景 ----------

def material(name, rgb, rough=0.4):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return m


def floor_material():
    """地板依距離漸變成透明，避免透明背景＋不透明地板造成硬地平線。"""
    m = material("floor", (0.02, 0.02, 0.03), 0.5)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    length = nt.nodes.new("ShaderNodeVectorMath")
    length.operation = "LENGTH"
    fade = nt.nodes.new("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 2.5
    fade.inputs["From Max"].default_value = 7.0
    fade.inputs["To Min"].default_value = 1.0
    fade.inputs["To Max"].default_value = 0.0
    nt.links.new(coord.outputs["Object"], length.inputs[0])
    nt.links.new(length.outputs["Value"], fade.inputs["Value"])
    nt.links.new(fade.outputs["Result"], bsdf.inputs["Alpha"])
    return m


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, T.FRAMES - 1
    sc.render.fps = T.FPS

    world = bpy.data.worlds.new("world")
    world.color = (0.05, 0.05, 0.07)
    sc.world = world

    bpy.ops.mesh.primitive_plane_add(size=40)
    floor = bpy.context.object
    floor.name = "floor"
    floor.data.materials.append(floor_material())

    bpy.ops.mesh.primitive_cube_add(size=SIZE)
    body = bpy.context.object
    body.name = "body"
    # 原點移到底面中心：縮放（壓扁）時腳底不離地
    body.data.transform(Matrix.Translation((0, 0, SIZE / 2)))
    bev = body.modifiers.new("bevel", "BEVEL")
    bev.width, bev.segments = 0.18, 4
    body.data.materials.append(material("candy", (1.0, 0.45, 0.15)))
    bpy.ops.object.shade_smooth()

    eye_mat = material("eye", (0.02, 0.02, 0.02), 0.2)
    eyes = []
    for x in (-0.35, 0.35):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(x, -SIZE / 2, SIZE * 0.62))
        e = bpy.context.object
        e.name = f"eye_{'L' if x < 0 else 'R'}"
        e.data.materials.append(eye_mat)
        bpy.ops.object.shade_smooth()
        e.parent = body
        eyes.append(e)

    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    key = bpy.data.objects.new("key", bpy.data.lights.new("key", "AREA"))
    key.data.energy, key.data.size = 800, 4
    key.location = (-4, -4, 6)
    key.rotation_euler = (math.radians(45), 0, math.radians(-45))
    key.visible_camera = False  # 面光預設會入鏡
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    for o in (sun, key, cam):
        sc.collection.objects.link(o)
    sc.camera = cam
    return sc, body, eyes, cam


# ---------- 逐格烘焙 ----------

def bake(target, path, values):
    """把逐格數值寫成線性關鍵格。values: 每格一個 tuple（各分量一條 F-Curve）。"""
    ad = target.animation_data or target.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(f"{target.name}_bake")
    n = len(values)
    for i in range(len(values[0])):
        fc = ad.action.fcurve_ensure_for_datablock(target, path, index=i)
        fc.keyframe_points.add(n)
        co = []
        for f, v in enumerate(values):
            co += (f, v[i])
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.update()


def animate(body, eyes, cam):
    frames = range(T.FRAMES)
    cams = [camera_at(f) for f in frames]
    bake(cam, "location", [tuple(c[0]) for c in cams])
    bake(cam, "rotation_euler", [tuple(c[1]) for c in cams])
    bake(cam.data, "lens", [(c[2],) for c in cams])

    bodies = [body_at(f) for f in frames]
    bake(body, "location", [(0, 0, b[0]) for b in bodies])
    bake(body, "scale", [b[1] for b in bodies])
    bake(body, "rotation_euler", [(0, 0, b[2]) for b in bodies])

    for e in eyes:
        bake(e, "scale", [(1, 1, blink_at(f)) for f in frames])


# ---------- 算圖 ----------

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="輸出資料夾（絕對路徑；逐格 PNG 建議放本機暫存）")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--step", type=int, default=6)
    ap.add_argument("--motion-blur", action="store_true")
    ap.add_argument("--no-render", action="store_true", help="只建場景存 scene.blend")
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    (out / "frames").mkdir(parents=True, exist_ok=True)

    sc, body, eyes, cam = build()
    animate(body, eyes, cam)

    r = sc.render
    r.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = a.samples
    r.resolution_x, r.resolution_y = T.WIDTH, T.HEIGHT
    r.resolution_percentage = round(a.scale * 100)
    sc.view_settings.view_transform = "Standard"  # AgX 會把糖果色洗淡
    r.film_transparent = True  # 3D 只算主體，背景在合成階段畫
    r.use_motion_blur = a.motion_blur
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    r.filepath = str(out / "frames" / "f_")
    sc.frame_step = a.step

    bpy.ops.wm.save_as_mainfile(filepath=str(out / "scene.blend"))
    if not a.no_render:
        bpy.ops.render.render(animation=True)


main()
