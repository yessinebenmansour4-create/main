import sys
D=90.816; PAD=0.09
sil=[tuple(map(float,l.split())) for l in open(sys.argv[1]) if l.strip()]
keep=[]; cur=0.0
for s,e in sil:
    a=cur; b=s+PAD
    if b-a>0.15: keep.append((round(a,3),round(b,3)))
    cur=max(e-PAD,0)
if D-cur>0.15: keep.append((round(cur,3),D))
# merge tiny gaps
m=[]
for a,b in keep:
    if m and a-m[-1][1]<0.05: m[-1]=(m[-1][0],b)
    else: m.append((a,b))
print(sum(b-a for a,b in m), len(m), file=sys.stderr)
for a,b in m: print(a,b)
