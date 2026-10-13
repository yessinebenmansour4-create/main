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
- **Caméra virtuelle** : le 16:9 est recadré en 9:16 sur le visage de l'intervenant.
  - Chaque jump cut alterne plan serré et plan plus large.
  - Des travellings avant lents animent tous les plans.
  - Des punch-ins soulignent « survalorisés », « très spéculatifs », « une bulle » et « survalorisation ».
  - Sur le plan large, la caméra fait un travelling latéral de l'animateur vers l'invité.
- **Hook** (0 à 2,9 s) : « IA · crypto · immobilier — Où sont les bulles ? », placé en haut de l'écran pour laisser
  la zone des sous-titres libre.
- **Outro** (3,8 s) : la façade ESCP teintée en vert avec un zoom lent. Le cadre se trace, puis le « E » apparaît,
  suivi du wordmark « L'ÉCONOMIQUE » et du call-to-action « Épisode complet en bio ».

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `edl.json` | Liste des morceaux gardés (temps source) et vitesse |
| `scripts/build_master.py` | Construit `assets/master.mp4` : coupes, ×1,15 et loudness |
| `scripts/extract_logo.py` | Sépare le visuel en deux calques : fond sans logo et « E » détouré |
| `index.html` | Vidéo et caméra virtuelle (plan de cadrage dans `SHOTS`) |
| `compositions/hook.html` | Accroche du début |
| `compositions/outro.html` | Animation du logo |
| `DESIGN.md` | Couleurs, polices et zones de sécurité |

## Re-générer

`assets/master.mp4` (51 Mo) n'est pas versionné. Pour le recréer à partir de l'extrait source :

```bash
python3 scripts/build_master.py <extrait_source.mp4> assets/master.mp4
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render -o renders/short-leconomique-9x16.mp4 --fps 30 --crf 16
```

Pour retoucher un texte, il suffit de modifier `compositions/hook.html` ou `compositions/outro.html`. Les cadrages et
zooms se règlent dans le tableau `SHOTS` de `index.html`.
