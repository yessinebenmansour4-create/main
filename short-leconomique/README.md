# Short L'Économique : « Où sont les bulles ? »

Short vertical 9:16 (1080×1920, 30 i/s, environ 42 s) monté à partir de l'extrait du podcast. Il n'y a **ni musique
ni sous-titres** : ils sont ajoutés ensuite.

Rendu final : `renders/short-leconomique-9x16.mp4`

## Ce qui a été fait

- **Coupes** : les 5 premières et les 24 dernières secondes de l'extrait sont retirées. Le short démarre sur la
  question « Quels sont les principaux risques… » et se termine sur « …ça dépend un peu des pays », juste avant la
  question suivante de l'animateur.
- **Blancs et hésitations** : le « heu… » de 1,4 s, les faux départs (« c'est toujours di- », « je pense que dans
  les… », « les crypt-… ») et une répétition (« des signaux, à des signaux ») sont coupés, ainsi que les silences.
  Au total, 16 morceaux (voir `edl.json`).
- **Vitesse** : ×1,15, avec la hauteur de la voix conservée (`atempo`). Le niveau est normalisé à -16 LUFS.
- **Restauration de l'image** : Real-ESRGAN (realesr-general-x4v3, débruitage 0,25) nettoie les artefacts de
  compression et reconstruit les détails de la zone affichée à l'écran, image par image. Le résultat est une vidéo
  intermédiaire en 3840×2160. Elle est précédée d'un léger débruitage temporel.
- **Caméra virtuelle** : le 16:9 est recadré en 9:16 sur le visage de l'intervenant.
  - Chaque jump cut alterne plan serré et plan plus large.
  - Des travellings avant lents animent tous les plans.
  - Des punch-ins soulignent « survalorisés », « très spéculatifs », « une bulle » et « survalorisation ».
  - Sur le plan large, la caméra fait un travelling latéral de l'animateur vers l'invité.
  - Partie 2 (à partir de 19,8 s), plus nerveuse : à-coup de zoom à chaque coupe, zooms rapides avec léger
    rebond sur les mots clés, et tremblement d'impact sur « une bulle » et « survalorisation ».
- **Hook** (0 à 2,9 s) : « IA · crypto · immobilier — Où sont les bulles ? » en Tinos (style Times New Roman), sur un
  cartouche vert émeraude, placé en haut de l'écran pour laisser la zone des sous-titres libre.
- **Outro** (3,8 s) : la façade ESCP teintée en vert avec un zoom lent. Le cadre se trace, puis le « E » apparaît,
  suivi du wordmark « L'ÉCONOMIQUE » et du call-to-action « Épisode complet en bio ».

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `edl.json` | Liste des morceaux gardés (temps source) et vitesse |
| `scripts/build_master.py` | Construit le master natif sans perte : coupes, ×1,15, loudness et débruitage temporel |
| `scripts/export_camera.mjs` | Exporte la position de la caméra virtuelle à chaque image |
| `scripts/esrgan_onnx.py` | Convertit les poids Real-ESRGAN en ONNX, sans PyTorch |
| `scripts/enhance_master.py` | Restauration IA et `assets/master.mp4` en 3840×2160 (OpenVINO, CPU) |
| `scripts/extract_logo.py` | Sépare le visuel en deux calques : fond sans logo et « E » détouré |
| `index.html` | Vidéo et caméra virtuelle (plan de cadrage dans `SHOTS`) |
| `compositions/hook.html` | Accroche du début |
| `compositions/outro.html` | Animation du logo |
| `DESIGN.md` | Couleurs, polices et zones de sécurité |

## Re-générer

`assets/master.mp4` (4K, plusieurs centaines de Mo) n'est pas versionné. Pour le recréer à partir de l'extrait
source (pré-requis : `pip install onnx openvino opencv-python-headless`) :

```bash
python3 scripts/build_master.py <extrait_source.mp4> master-native.mkv
# poids : github.com/xinntao/Real-ESRGAN/releases (v0.2.5.0) realesr-general-x4v3.pth + realesr-general-wdn-x4v3.pth
python3 scripts/esrgan_onnx.py realesr-general-x4v3.pth realesr-general-wdn-x4v3.pth 0.25 srvgg.onnx
node scripts/export_camera.mjs <dossier puppeteer-core> <chrome> camera.json
python3 scripts/enhance_master.py master-native.mkv camera.json srvgg.onnx assets/master.mp4
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render -o renders/short-leconomique-9x16.mp4 --fps 30 --crf 14 --video-frame-format jpg
```

Pour retoucher un texte, il suffit de modifier `compositions/hook.html` ou `compositions/outro.html`. Les cadrages et
zooms se règlent dans le tableau `SHOTS` de `index.html`.
