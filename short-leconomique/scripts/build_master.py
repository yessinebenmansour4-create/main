"""Build the edited 16:9 master (cuts + speed-up + loudness) from edl.json, at source resolution.

Usage: python3 scripts/build_master.py <source.mp4> <out.mkv>
The output is lossless (FFV1 + FLAC) and feeds scripts/enhance_master.py, which produces the
restored 3840x2160 assets/master.mp4 used by the composition.
Writes assets/master-timing.json with each segment's start/end on the output timeline.
"""
import json, subprocess, sys, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30

edl = json.load(open(os.path.join(HERE, "edl.json")))
src, out = sys.argv[1], sys.argv[2]
speed = edl["speed"]
snap = lambda t: round(t * FPS) / FPS  # frame-aligned cuts keep A/V in sync

parts, labels, timing, t_out = [], [], [], 0.0
for i, s in enumerate(edl["segments"]):
    a, b = snap(s["in"]), snap(s["out"])
    d = b - a
    parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]")
    # 12 ms fades at every join avoid clicks
    parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
    labels.append(f"[v{i}][a{i}]")
    timing.append({"i": i, "src_in": a, "src_out": b, "start": round(t_out, 4), "end": round(t_out + d / speed, 4), "text": s["text"]})
    t_out += d / speed

n = len(edl["segments"])
parts.append("".join(labels) + f"concat=n={n}:v=1:a=1[vc][ac]")
# Mild temporal denoise calms the source's compression shimmer before AI restoration
parts.append(f"[vc]setpts=PTS/{speed},fps={FPS},hqdn3d=0:0:3:3,format=yuv444p[vo]")
parts.append(f"[ac]atempo={speed},highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[ao]")

cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", ";".join(parts),
       "-map", "[vo]", "-map", "[ao]", "-c:v", "ffv1", "-level", "3", "-c:a", "flac", out]
subprocess.run(cmd, check=True)
json.dump({"speed": speed, "duration": round(t_out, 4), "segments": timing},
          open(os.path.join(HERE, "assets", "master-timing.json"), "w"), ensure_ascii=False, indent=1)
print(f"master: {out}  duration={t_out:.3f}s  segments={n}")
