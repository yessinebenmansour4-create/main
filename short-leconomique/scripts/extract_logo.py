"""Split the association artwork (ESCP facade + framed blackletter E) into layers for the outro.

Usage: python3 scripts/extract_logo.py <artwork.jpg> <preview_dir>
Writes assets/escp-bg-clean.jpg (logo removed) and assets/logo-e.png (white E, alpha, 4x).
"""
import cv2, numpy as np, os, sys
S=sys.argv[2]; os.makedirs(S+"/logo",exist_ok=True)
P=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"assets")
im=cv2.imread(sys.argv[1]).astype(np.float32)
H,W=im.shape[:2]
L=im.max(2)
x0,y0,x1,y1=678,327,923,572
# mask: box lines + bright E inside box
m=np.zeros((H,W),np.uint8)
m[y0-3:y0+5,x0-3:x1+5]=255; m[y1-3:y1+5,x0-3:x1+5]=255
m[y0-3:y1+5,x0-3:x0+5]=255; m[y0-3:y1+5,x1-3:x1+5]=255
inner=np.zeros((H,W),bool); inner[y0+5:y1-3,x0+5:x1-3]=True
bright=(L>205)&inner
mE=cv2.dilate(bright.astype(np.uint8)*255,np.ones((7,7),np.uint8))
m=np.maximum(m,mE)
bg=cv2.inpaint(im.astype(np.uint8),m,9,cv2.INPAINT_TELEA); bgT=bg.copy()
# Facade rows (roof line, plants, cornice) are horizontally repetitive: fill them by copying the
# texture beside the logo instead of Telea's smear, then feather the seam.
src=im.astype(np.uint8); fill=bg.copy(); Y0,Y1=486,600
for y in range(Y0,Y1):
    xs=np.where(m[y]>0)[0]
    for x in xs:
        for dx in ((-250,-500) if x<800 else (250,500)):
            if 0<=x+dx<W and m[y,x+dx]==0: fill[y,x]=src[y,x+dx]; break
w=np.zeros((H,W),np.float32); w[Y0:Y1]=1.0
w=cv2.GaussianBlur(w,(0,0),3)[...,None]   # soft vertical blend with the Telea sky
mm=np.clip(cv2.GaussianBlur(cv2.dilate(m,np.ones((9,9),np.uint8)).astype(np.float32)/255,(0,0),2)*1.6,0,1)[...,None]
patched=(fill*w+bg*(1-w))
bg=(patched*mm+src*(1-mm)).astype(np.uint8)
cv2.imwrite(P+"/escp-bg-clean.jpg",bg,[cv2.IMWRITE_JPEG_QUALITY,95])
# alpha of white glyph: I = a*255 + (1-a)*B
B=bgT.astype(np.float32)  # smooth Telea estimate gives the cleanest alpha
a=((im-B)/np.maximum(255-B,1)).min(2)   # conservative across channels
a=np.clip(a,0,1); a[~inner]=0
a[mE==0]=0
# crop glyph bbox
ys,xs=np.where(a>0.08); gx0,gx1,gy0,gy1=xs.min()-4,xs.max()+5,ys.min()-4,ys.max()+5
print("glyph bbox",gx0,gy0,gx1,gy1)
crop=a[gy0:gy1,gx0:gx1]
k=4
up=cv2.resize(crop,None,fx=k,fy=k,interpolation=cv2.INTER_CUBIC)
up=cv2.GaussianBlur(up,(0,0),1.6)
# sharpen edge: smoothstep around 0.5
t=np.clip((up-0.30)/(0.45),0,1); up=t*t*(3-2*t)
rgba=np.dstack([np.full_like(up,255)]*3+[up*255]).astype(np.uint8)
cv2.imwrite(P+"/logo-e.png",rgba)
open(S+"/logo/glyph.txt","w").write(f"{gx0} {gy0} {gx1} {gy1} {k}\n")
# preview on dark green
prev=np.zeros_like(rgba[:,:,:3]); prev[:]=(40,60,30)
al=up[...,None]; prev=(prev*(1-al)+255*al).astype(np.uint8)
cv2.imwrite(S+"/logo/e_preview.png",prev)
cv2.imwrite(S+"/logo/bg_preview.png",bg[250:650,550:1050])
