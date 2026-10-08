# Interview ESCP (montage 16:9)

`interview-escp-16x9.mp4` : 1920×1080, 30 fps, 88 s, sans sous-titres.

- **Blancs coupés** : `build/cut.py` (silencedetect −33 dB / 0,25 s, marge 90 ms) → 27 plans conservés (`build/keep.txt`), 91 s → 82 s.
- **Dynamisme** : zooms alternés 1,0 / 1,12 entre les plans (`build/graph.py`), intro et outro HyperFrames (`build/intro`, `build/outro`) avec zoom traversant sur le logo, flash blanc et whooshes.
- **Musique** : composition originale synthétisée par `build/music.py` (aucun sample externe, donc libre de droits), 100 BPM, La mineur (Am–F–C–G). Elle est mise en avant sur l'intro et l'outro, puis baissée et compressée en sidechain sous la voix.
