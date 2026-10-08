import sys
segs=[tuple(map(float,l.split())) for l in open(sys.argv[1])]
f=[];z=False;n=0
for i,(a,b) in enumerate(segs):
    if b-a>=1.5: z=not z
    v=f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS"
    if z: v+=",crop=1714:964:103:30,scale=1920:1080:flags=lanczos"
    v+=f",setsar=1[v{i}]"
    d=b-a
    f.append(v)
    f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
f.append("".join(f"[v{i}][a{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=1:a=1[v][a]")
print(";\n".join(f))
