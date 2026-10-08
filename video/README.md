# Interview ESCP (montage 16:9)

`interview-escp-16x9.mp4` : 1920×1080, 30 fps, 88 s, sans sous-titres.

- **Blancs coupés** : `build/cut.py` (silencedetect −33 dB / 0,25 s, marge 90 ms) → 27 plans conservés (`build/keep.txt`), 91 s → 82 s.
- **Dynamisme** : zooms alternés 1,0 / 1,12 entre les plans (`build/graph.py`), intro et outro HyperFrames (`build/intro`, `build/outro`) avec zoom traversant sur le logo, flash blanc et whooshes.
- **Musique** : composition originale synthétisée par `build/music.py` (aucun sample externe, donc libre de droits), 100 BPM, La mineur (Am–F–C–G). Elle est mise en avant sur l'intro et l'outro, puis baissée et compressée en sidechain sous la voix.

---

# Version verticale 9:16 (v2)

`interview-escp-9x16.mp4` : 1080×1920, 30 fps, 46,6 s, accélérée ×1,5 (voix sans changement de hauteur), sans musique ni sous-titres.

- **Coupes** (`build/vertical/edl.py`) : silences, 8 « euh » et 4 faux départs (« Bon, je pense que dans les… », « Il y a des… », « dans le m… », « C'est toujours. »), un bégaiement (« il y a quand même une bulle »), des tics (« hein », « on va dire », « si vous voulez », « Bon ») et la fin hésitante. Les « euh » ont été repérés avec Whisper small (paquet npm `sts-whisper-small`), puis confirmés en retranscrivant chaque passage avec et sans la coupe.
- **Cadrage** (`build/vertical/render_v.py`) : suivi du visage (OpenCV, `faces.py`) de la personne qui parle, lissé sur environ 1 s. Sur les plans larges, le cadre suit la personne qui parle.
- **Dynamisme modéré** : lente poussée continue (environ 1,6 %/s), zoom de 1,13 alterné aux coupes dans un même plan, léger travelling latéral, zoom d'accentuation sur « survalorisés », « très spéculatifs », « bulles », « Moyen-Orient » et « boost ».
- **Outro** : `build/vertical/outro_v` (HyperFrames), transition par flash blanc, fondu au noir.
