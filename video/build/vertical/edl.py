import numpy as np, json, sys
S=sys.argv[1]
E=np.load(S+'/asr/E.npy')  # 10ms frame energy dB
D=90.8
sil=[tuple(map(float,l.split())) for l in open(S+'/sil.txt') if l.strip()]
sil=[(a,b if b else D) for a,b in [(x[0],x[1] if len(x)>1 else D) for x in sil]]
# manual removals (source seconds)
manual=[(0.0,1.78,'D accord'),(4.26,5.86,'on va dire'),(12.00,12.62,'hein'),(15.55,16.86,'euh'),(18.30,18.75,'euh'),
 (22.38,23.16,'faux depart: Bon je pense que dans les'),(26.54,26.92,'Bon'),(34.95,35.88,'faux depart: Il y a des'),
 (44.45,46.72,'faux depart: dans le m...'),(48.97,50.45,'begaiement: il y a quand meme une bulle'),(52.45,52.85,'euh'),(55.40,55.95,'euh'),(61.10,61.45,'euh'),
 (73.06,73.52,'faux depart: C est toujours'),(75.45,75.95,'euh'),(76.92,77.98,'si vous voulez'),(84.40,84.85,'euh'),(88.70,D,'fin hesitante')]
def snap(t,r=0.06):
    i0=max(0,int((t-r)*100)); i1=min(len(E)-1,int((t+r)*100))
    if i1<=i0: return t
    return (i0+int(np.argmin(E[i0:i1+1])))/100
PAD=0.07
rem=[(snap(a) if a>0 else 0, snap(b) if b<D else D) for a,b,_ in manual]
rem+=[(a+PAD,b-PAD) for a,b in sil if b-a>2*PAD+0.05]
rem.sort(); m=[]
for a,b in rem:
    if m and a<=m[-1][1]+0.04: m[-1]=(m[-1][0],max(m[-1][1],b))
    else: m.append((a,b))
keep=[];cur=0
for a,b in m:
    if a-cur>=0.12: keep.append((round(cur,3),round(a,3)))
    cur=max(cur,b)
if D-cur>=0.12: keep.append((round(cur,3),D))
json.dump(keep,open(S+'/keep2.json','w'))
print(len(keep),'segments, kept',round(sum(b-a for a,b in keep),2),'s ->',round(sum(b-a for a,b in keep)/1.5,2),'s at 1.5x')
