# Portfolio — Nicolas Scheer

Site Astro (statique) pour candidatures VFX / R&D.

## Démarrer sur une nouvelle machine

Prérequis : Node ≥ 22.12.

```sh
git clone <url-du-repo> portfolio && cd portfolio
npm install
npm run dev        # http://localhost:4321
npm run build      # sortie statique dans dist/
```

Après avoir ajouté des fichiers dans `public/` pendant que le serveur tourne, le relancer
(`npx astro dev stop && npx astro dev --background`) sinon ils renvoient 404.

## Déploiement

Publié sur GitHub Pages par `.github/workflows/deploy.yml` à chaque push sur `main`.
Le dépôt est un *user site* (`NicolasSCH2ER.github.io`), donc le site est servi à la
racine : `astro.config.mjs` ne définit que `site`, sans `base`, et tous les liens du
site restent des chemins absolus (`/projets`, `/media/...`).

Prérequis côté GitHub : **Settings → Pages → Source: GitHub Actions**.

## Structure

- `src/data/content.ts` — source unique du contenu (projets, rendus, `videos`, `model`).
- `src/components/ProjectMedia.astro` — média d'un projet (vidéo/image).
- `src/components/ModelViewport.astro` — viewport 3D interactif (Three.js + OrbitControls, GLB).
- `public/media/` — vidéos, rendus, modèles GLB (~55 Mo).

## Médias des rendus (`public/media/renders/`)

Chaque rendu existe en trois fichiers, pour que la galerie ne coûte que ses posters :

| fichier | rôle | chargement |
|---|---|---|
| `<slug>-poster.jpg` | image de tuile et `poster` du lecteur | immédiat (~70 Ko) |
| `<slug>-preview.mp4` | 720p muet, boucle de survol | `preload="none"`, au survol |
| `<slug>.mp4` | master 1080p CRF 23, avec son | `preload="none"`, au clic |

Pour ajouter un rendu, produire les trois fichiers avec ffmpeg (`<src>` = master d'origine) :

```sh
ffmpeg -i <src> -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p        -c:a aac -b:a 128k -movflags +faststart <slug>.mp4
ffmpeg -i <src> -an -vf scale=1280:-2 -c:v libx264 -crf 30 -preset slow        -pix_fmt yuv420p -movflags +faststart <slug>-preview.mp4
ffmpeg -ss <25% de la durée> -i <src> -frames:v 1 -vf scale=1600:-2 -q:v 4 <slug>-poster.jpg
```

Même principe pour les médias de projet (`public/media/projects/`) : chaque `.mp4` a un
`<slug>-poster.jpg` à côté de lui, que la page de projet utilise en `poster`. Les clips ne
sont ni préchargés ni lus au chargement — la vignette d'une liste démarre au survol, et
une boucle de galerie démarre quand elle entre dans le champ.

Le CRF du master se cale au VMAF contre la source (`libvmaf`), en visant ≥ 90 ;
un plafond `-maxrate` a été essayé puis écarté, il faisait chuter la qualité sans
gain utile puisque les masters ne se téléchargent qu'à la demande.

## Régénérer les médias (`tools/render/`)

Scripts utilisés pour produire les rendus. Ils ne servent que si on refait des médias : ils ont des
**chemins absolus Windows** (`C:\Users\nicol\Code\hyperforge`, `bourrasque_v2\build_hires`, `C:\tmp`)
à adapter, et demandent Blender 5.x, une carte NVIDIA et FFmpeg.

| Script | Rôle |
|---|---|
| `hyperforge_render.py` | rendu Cycles d'un polytope 4D (`CELL5`…`CELL600`) |
| `compute_julia.py` + `julia_render.py` | isosurface Julia quaternionique (marching cubes) puis rendu |
| `export_hyperforge_glb.py` | polytope → GLB léger pour le viewport |
| `sim_scene.py` | simulation bourrasque (eau/gelée/sable/collider) via ctypes → `.npz` par frame |
| `render_fluid_sequence.py` | rendu Blender de la séquence `.npz` |
| `export_bourrasque_glb.py` | une frame de sim, décimée → GLB pour le viewport |
| `preview_glb2.py` | aperçu rapide d'un GLB |
