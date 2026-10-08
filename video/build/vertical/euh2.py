import numpy as np, wave, json, sys
w=wave.open(sys.argv[1]); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
hop=int(0.01*sr); win=int(0.03*sr); n=(len(x)-win)//hop
fr=np.stack([x[i*hop:i*hop+win] for i in range(n)])*np.hanning(win)
S=np.abs(np.fft.rfft(fr,axis=1))**2; f=np.fft.rfftfreq(win,1/sr)
edges=np.geomspace(80,7000,33); B=np.stack([S[:,(f>=edges[i])&(f<edges[i+1])].sum(1) for i in range(32)],1)
L=np.log(B+1e-9); E=10*np.log10(S.sum(1)+1e-12); Ln=L-L.mean(1,keepdims=True)
d=np.r_[np.linalg.norm(Ln[3:]-Ln[:-3],axis=1),np.full(3,99)]
dthr=np.percentile(d,40); ethr=np.percentile(E,30)
st=(d<dthr)&(E>ethr)
words=json.load(open(sys.argv[2]))['chunks']
np.save('E.npy',E)
for c in words:
    a,b=c['timestamp']; t=c['text'].strip(" ,.?'"); dur=b-a; exp=0.06*len(t)+0.12
    if dur>exp+0.3:
        i0,i1=int(a*100),int(b*100); best=(0,0)
        i=i0
        while i<i1:
            if st[i]:
                j=i
                while j<i1 and st[j]: j+=1
                if j-i>best[1]-best[0]: best=(i,j)
                i=j
            else: i+=1
        # energy sketch every 50ms
        sk=''.join(' .:-=+*#'[min(7,max(0,int((E[k]-ethr)/4)+1))] for k in range(i0,i1,5))
        print(f"{a:6.2f}-{b:6.2f} {c['text']:16} stable {best[0]/100:.2f}-{best[1]/100:.2f} ({(best[1]-best[0])/100:.2f}) |{sk}|")
