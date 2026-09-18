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

## Structure

- `src/data/content.ts` — source unique du contenu (projets, rendus, `videos`, `model`).
- `src/components/ProjectMedia.astro` — média d'un projet (vidéo/image).
- `src/components/ModelViewport.astro` — viewport 3D interactif (Three.js + OrbitControls, GLB).
- `public/media/` — vidéos, rendus, modèles GLB (~77 Mo).

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
