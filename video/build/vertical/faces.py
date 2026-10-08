import cv2, sys, json
cap=cv2.VideoCapture(sys.argv[1]); fps=cap.get(cv2.CAP_PROP_FPS)
cf=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_alt2.xml')
cp=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_profileface.xml')
out=[]; i=0; step=int(fps/4)
while True:
    ok=cap.grab()
    if not ok: break
    if i%step==0:
        _,f=cap.retrieve(); g=cv2.cvtColor(cv2.resize(f,(960,540)),cv2.COLOR_BGR2GRAY)
        fs=list(cf.detectMultiScale(g,1.1,5,minSize=(40,40)))
        if not fs:
            fs=list(cp.detectMultiScale(g,1.1,5,minSize=(40,40)))+[(960-x-w,y,w,h) for x,y,w,h in cp.detectMultiScale(cv2.flip(g,1),1.1,5,minSize=(40,40))]
        out.append([round(i/fps,2),[[int(2*(x+w/2)),int(2*(y+h/2)),int(2*w)] for x,y,w,h in fs]])
    i+=1
json.dump(out,open(sys.argv[2],'w'))
