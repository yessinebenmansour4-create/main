# Original synthesized track (no samples) -> royalty-free by construction.
import numpy as np, wave, sys
SR=48000; BPM=100; beat=60/BPM; bar=4*beat
DUR=float(sys.argv[2]); N=int(DUR*SR)+SR
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def mtof(m): return 440*2**((m-69)/12)
def add(sig,t0,gl=1.0,gr=1.0):
    i=int(t0*SR); j=min(N,i+len(sig))
    if i>=N: return
    L[i:j]+=sig[:j-i]*gl; R[i:j]+=sig[:j-i]*gr
def env(n,a,d_rel):
    t=np.arange(n)/SR; e=np.minimum(t/a,1.0) if a>0 else np.ones(n)
    return e*np.exp(-t/d_rel)
# progression Am F C G (MIDI chords)
prog=[[57,60,64,69],[53,57,60,65],[48,55,60,64],[55,59,62,67]]
roots=[45,41,48,43]
nbars=int(DUR/bar)+2
def drums_on(b): return 4<=b<nbars-3
for b in range(nbars):
    t0=b*bar; ch=prog[b%4]; rt=roots[b%4]
    # pad: soft additive saw, slow attack/release
    n=int(bar*SR*1.15); t=np.arange(n)/SR
    pad=np.zeros(n)
    for m in ch:
        for det in (-0.08,0.08):
            f=mtof(m+det)
            for h in range(1,7): pad+=np.sin(2*np.pi*f*h*t+h)/h**1.6
    shape=np.minimum(t/0.6,1)*np.clip((bar*1.15-t)/0.5,0,1)
    add(pad*shape*0.022,t0,1.0,0.9)
    # bass
    for k in range(4):
        if k in (0,2,3) or drums_on(b):
            n=int(beat*0.9*SR); t=np.arange(n)/SR; f=mtof(rt-12 if k!=3 else rt)
            s=(np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t))*env(n,0.005,0.35)
            add(s*0.16,t0+k*beat)
    # arpeggio pluck (8ths) with ping-pong echo
    pat=[0,2,1,3,2,1,3,2]
    for k in range(8):
        m=ch[pat[k]]+12; n=int(0.9*SR); t=np.arange(n)/SR; f=mtof(m)
        mod=np.sin(2*np.pi*f*2*t)*2.0*np.exp(-t/0.15)
        s=np.sin(2*np.pi*f*t+mod)*env(n,0.002,0.22)
        acc=1.0 if k%2==0 else 0.75
        tt=t0+k*beat/2
        add(s*0.05*acc,tt,1.0,0.8)
        add(s*0.022*acc,tt+beat*0.75,0.3,1.0); add(s*0.012*acc,tt+beat*1.5,1.0,0.3)
    if drums_on(b):
        for k in range(4):
            tt=t0+k*beat
            if k in (0,2) or (k==3 and b%2==1):
                n=int(0.4*SR); t=np.arange(n)/SR
                ph=2*np.pi*np.cumsum(50+90*np.exp(-t/0.04))/SR
                add(np.sin(ph)*env(n,0.001,0.12)*0.42, tt if k!=3 else tt+beat/2)
            if k in (1,3):
                n=int(0.3*SR); nz=rng.standard_normal(n); nz=nz-np.convolve(nz,np.ones(6)/6,'same')
                add(nz*env(n,0.001,0.05)*0.04,tt)
        for k in range(8):
            n=int(0.08*SR); nz=rng.standard_normal(n); nz=np.diff(nz,prepend=0)
            add(nz*env(n,0.0005,0.018)*(0.014 if k%2 else 0.008),t0+k*beat/2,0.7,1.0)
# riser into drums (bar 4)
n=int(bar*SR); t=np.arange(n)/SR; nz=rng.standard_normal(n); nz=np.diff(nz,prepend=0)
add(nz*(t/bar)**3*0.05,3*bar)
# reverb: fft convolution with decaying noise IR
def rev(x):
    ir=rng.standard_normal(int(2.2*SR))*np.exp(-np.arange(int(2.2*SR))/SR/0.6)
    ir[:int(0.02*SR)]=0; m=len(x)+len(ir); F=1<<(m-1).bit_length()
    y=np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
    return y/np.max(np.abs(y))*np.max(np.abs(x))*0.35
L=L+rev(L); R=R+rev(R)
L=L[:int(DUR*SR)]; R=R[:int(DUR*SR)]
t=np.arange(len(L))/SR; fade=np.clip((DUR-t)/3.0,0,1)*np.clip(t/0.5,0,1)
L*=fade; R*=fade
pk=max(np.abs(L).max(),np.abs(R).max()); L=np.tanh(L/pk*1.2)*0.85; R=np.tanh(R/pk*1.2)*0.85
d=(np.stack([L,R],1)*32767).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
