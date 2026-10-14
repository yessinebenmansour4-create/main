"""AI restoration of the edited master: Real-ESRGAN (realesr-general-x4v3) on what the camera shows.

For every frame, the part of the 16:9 image that the virtual 9:16 camera actually shows (from
export_camera.mjs, plus a safety margin) is restored with Real-ESRGAN x4 at source resolution and
downsampled to 2x; the rest of the frame (never on screen) is a plain Lanczos 2x upscale.
Runs on CPU with OpenVINO (bf16 on AMX-capable Xeons: about 1 s per frame).

Usage: python3 scripts/enhance_master.py <master-native.mkv> <camera.json> <model.onnx> <out.mp4> [frames]
"""
import json, subprocess, sys, time
import numpy as np
import cv2
import openvino as ov

SRC_W, SRC_H, OUT_SCALE = 1920, 1080, 2
SCREEN_W, SCREEN_H = 1080, 1920
MARGIN = 48  # source px kept around the visible area (camera shake, later framing tweaks)
BUCKET = 64  # pad crops to a few fixed shapes so compiled models are reused
BLEND = 0.12  # share of the plain upscale mixed back in, keeps natural skin texture

src, cam_path, model_path, out = sys.argv[1:5]
only = [int(n) for n in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
cams = {c[0]: c[1:] for c in json.load(open(cam_path))}

core = ov.Core()
model = core.read_model(model_path)
compiled = {}


def sr(img):
    """Real-ESRGAN x4 on a BGR uint8 crop (reflect-padded to a bucketed shape)."""
    h, w = img.shape[:2]
    H, W = -(-h // BUCKET) * BUCKET, -(-w // BUCKET) * BUCKET
    if (H, W) not in compiled:
        m = model.clone()
        m.reshape([1, 3, H, W])
        compiled[(H, W)] = core.compile_model(m, "CPU", {"INFERENCE_PRECISION_HINT": "bf16"})
    pad = cv2.copyMakeBorder(img, 0, H - h, 0, W - w, cv2.BORDER_REFLECT_101)
    x = cv2.cvtColor(pad, cv2.COLOR_BGR2RGB).astype(np.float32).transpose(2, 0, 1)[None] / 255.0
    y = compiled[(H, W)]({0: x})[0][0].transpose(1, 2, 0)[: h * 4, : w * 4]
    return cv2.cvtColor((np.clip(y, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)


def visible_rect(n):
    """Source-pixel rectangle shown on screen at frame n (camera transform-origin is 0 0)."""
    x, y, s, sx, sy = cams[min(n, max(cams))]
    k = OUT_SCALE  # master px per source px
    x0, x1 = (-sx - x) / s / k, (SCREEN_W - sx - x) / s / k
    y0, y1 = (-sy - y) / s / k, (SCREEN_H - sy - y) / s / k
    x0, y0 = max(0, int(x0 - MARGIN) // 4 * 4), max(0, int(y0 - MARGIN) // 4 * 4)
    x1, y1 = min(SRC_W, -(-int(x1 + MARGIN) // 4) * 4), min(SRC_H, -(-int(y1 + MARGIN) // 4) * 4)
    return x0, y0, x1, y1


def enhance(frame, n):
    base = cv2.resize(frame, (SRC_W * OUT_SCALE, SRC_H * OUT_SCALE), interpolation=cv2.INTER_LANCZOS4)
    x0, y0, x1, y1 = visible_rect(n)
    up = sr(frame[y0:y1, x0:x1])
    up = cv2.resize(up, ((x1 - x0) * OUT_SCALE, (y1 - y0) * OUT_SCALE), interpolation=cv2.INTER_AREA)
    region = base[y0 * OUT_SCALE : y1 * OUT_SCALE, x0 * OUT_SCALE : x1 * OUT_SCALE]
    up = cv2.addWeighted(up, 1 - BLEND, region, BLEND, 0)
    base[y0 * OUT_SCALE : y1 * OUT_SCALE, x0 * OUT_SCALE : x1 * OUT_SCALE] = up
    return base


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
W, H = SRC_W * OUT_SCALE, SRC_H * OUT_SCALE
enc = None
if only is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30",
                            "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "12", "-pix_fmt", "yuv420p", "-g", "30", "-c:a", "aac", "-b:a", "256k",
                            "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
n, t0 = 0, time.time()
while True:
    buf = dec.stdout.read(SRC_W * SRC_H * 3)
    if len(buf) < SRC_W * SRC_H * 3:
        break
    frame = np.frombuffer(buf, np.uint8).reshape(SRC_H, SRC_W, 3)
    if only is None:
        enc.stdin.write(enhance(frame, n).tobytes())
        if n % 50 == 0:
            el = time.time() - t0
            print(f"frame {n}  {el / max(n, 1):.2f}s/frame  elapsed {el / 60:.1f} min", flush=True)
    elif n in only:
        cv2.imwrite(f"{out}_{n:04d}.png", enhance(frame, n))
        print(f"wrote {out}_{n:04d}.png  rect={visible_rect(n)}", flush=True)
    n += 1
if enc:
    enc.stdin.close()
    enc.wait()
print(f"done: {n} frames in {(time.time() - t0) / 60:.1f} min")
