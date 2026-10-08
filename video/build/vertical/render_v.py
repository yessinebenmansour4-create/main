# Vertical 9:16 reframe: speaker-centred crop, slow push-ins, jump-cut punch-ins, 1.5x speed.
import json, subprocess, sys, numpy as np, cv2, math
S=sys.argv[1]; SPEED=1.5; FPS=30; OW,OH=1080,1920; SW,SH=1920,1080
keep=json.load(open(S+'/keep2.json')); faces=json.load(open(S+'/faces.json'))
cuts=[0,0.7,2.3,10.2,31.7,39.8,64.93,67.5,72.43,999]
anchor=[(899,450),(341,340),(855,390),(895,430),(1525,445),(900,430),(310,375),(838,380),(1000,390)]
emph=[25.76,38.84,51.0,81.64,85.26]   # survalorisés, très spéculatifs, bulles, Moyen-Orient, boost
def shot(t): return max(i for i in range(len(cuts)-1) if cuts[i]<=t)
# per-shot face track of the speaker
tracks={}
for i in range(len(cuts)-1):
    ax,ay=anchor[i]; pts=[]
    for t,fs in faces:
        if cuts[i]+0.15<=t<cuts[i+1]-0.15:
            c=[f for f in fs if abs(f[0]-ax)<260 and f[2]>120]
            if c:
                f=min(c,key=lambda f:abs(f[0]-ax)); pts.append((t,f[0],f[1]))
    tracks[i]=np.array(pts) if len(pts)>=3 else None
def center(t):
    i=shot(t); ax,ay=anchor[i]; tr=tracks[i]
    if tr is None: return ax,ay
    w=np.exp(-0.5*((tr[:,0]-t)/0.9)**2)+1e-6
    x=float((w*tr[:,1]).sum()/w.sum()); y=float((w*tr[:,2]).sum()/w.sum())
    return 0.35*ax+0.65*x, 0.35*ay+0.65*y   # pull towards anchor to damp detector noise
# per-segment zoom plan
plan=[]; prevshot=None; zb=1.0
for k,(a,b) in enumerate(keep):
    sh=shot(a+0.01)
    if sh!=prevshot: zb=1.0
    else: zb=1.13 if zb<1.05 else 1.0
    plan.append((zb, 1 if k%2 else -1)); prevshot=sh
U=np.cumsum([0]+[b-a for a,b in keep]); total=U[-1]
nout=int(total/SPEED*FPS)
def ease(x): x=min(max(x,0),1); return 1-(1-x)**3
jobs=[]
for k in range(nout):
    u=k*SPEED/FPS; si=int(np.searchsorted(U,u,side='right')-1); si=min(si,len(keep)-1)
    a,b=keep[si]; el=u-U[si]; t=a+el
    zb,dr=plan[si]; z=zb*(1+0.016*el)
    for te in emph:
        if a<=te<b and t>=te-0.08: z*=1+0.14*ease((t-te+0.08)/0.18)
    cx,cy=center(t); cx+=dr*min(el,3)*7
    fi=min(max(round(t*FPS),math.ceil(a*FPS)),math.floor(b*FPS)-1)
    jobs.append((fi,z,cx,cy))
dec=subprocess.Popen(['ffmpeg','-v','error','-i',S+'/src.mp4','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',S+'/vert_video.mp4'],stdin=subprocess.PIPE)
j=0; fi=-1; fsz=SW*SH*3
while j<len(jobs):
    buf=dec.stdout.read(fsz)
    if len(buf)<fsz: break
    fi+=1
    if fi<jobs[j][0]: continue
    frame=np.frombuffer(buf,np.uint8).reshape(SH,SW,3)
    while j<len(jobs) and jobs[j][0]==fi:
        _,z,cx,cy=jobs[j]; wv=SH*9/16/z; hv=SH/z
        left=min(max(cx-wv/2,0),SW-wv); top=min(max(cy-0.40*hv,0),SH-hv); s=OH/hv
        M=np.float32([[s,0,-left*s],[0,s,-top*s]])
        enc.stdin.write(cv2.warpAffine(frame,M,(OW,OH),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE).tobytes()); j+=1
enc.stdin.close(); enc.wait(); dec.kill()
print('frames',j,'of',len(jobs), 'dur', len(jobs)/FPS)
