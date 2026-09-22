/* Traductions anglaises. Ne redéfinit que les champs textuels (résumé,
   description, libellés, statut) ; les champs non-textuels (assets, hue,
   github, stack) sont repris tels quels depuis `content.ts` pour ne jamais
   diverger entre les deux langues. */
import { PROJECTS, RENDERS, type Project, type Render } from "./content";

/* Statut affiché librement en anglais : pas de contrainte de l'union FR de
   `Project["status"]`, qui ne sert qu'a construire un nom de classe CSS —
   voir la logique .replace(/\s+/g, "-") reprise telle quelle par ProjectRow. */
type ProjectText = {
  tag?: string;
  status?: string;
  summary?: string;
  problem?: string;
  approach?: string;
  results?: string;
  videoLabels?: string[];
  mediaLabel?: string;
};

const PROJECT_TRANSLATIONS: Record<string, Partial<ProjectText>> = {
  bourrasque: {
    tag: "Fluid simulation",
    status: "active",
    summary: "GPU-accelerated fluid and material solver (water, elastic, sand) with a Blender extension for artist integration.",
    problem: "Mantaflow, Blender's native solver, is CPU-only and slow to iterate on; commercial GPU solvers (Hurricane, FLIP Fluids) are closed and proprietary.",
    approach: "MLS-MPM (Material Point Method) solver with APIC transfers in pure CUDA: each material — corotational elastic, water, sand in progress (Drucker-Prager plasticity) — is just a stress function plugged into the same particle-to-grid pipeline. Every change to the algorithm is first prototyped and validated against a NumPy reference before being ported to CUDA. Blender extension for a live viewport, SDF colliders and mesh export.",
    results: "3×3 GPU SVD validated to within 1.9·10⁻⁴ of NumPy on 5402 matrices · sand model validated by angle of repose (25°/35°/45°) · 184/185 tests passing (the last one is an interop test that skips cleanly when its 600 MB binary fixture hasn't been regenerated locally) · dam-break on a 128³ grid simulated up to 2.9 M particles per frame, mesh reconstructed on the fly by the solver's native Zhu-Bridson mesher (up to 3.2 M triangles/frame), ~7.6 s/frame for the full simulation + reconstruction + Cycles render pipeline.",
    videoLabels: [
      "Water — dam-break, 128³ grid",
      "Elastic — drop and bounce",
      "Sand — granular collapse (Drucker-Prager)",
      "Static collider — splash on a ramp",
    ],
    mediaLabel: "4 real solver simulations — captured from Cycles renders",
  },
  bvhnet: {
    tag: "Rendering engine",
    status: "v1 done",
    summary: "Physically based path tracer, on CPU (OpenMP) and GPU (OptiX / RT cores), importing glTF scenes exported from Blender.",
    problem: "Understand and control every stage of a path tracing pipeline — BVH construction, intersection, sampling — with the longer-term ambition of replacing the traversal heuristic with a small neural network (Neural BVH).",
    approach: "Binary BVH built by centroid sorting (simplified SAH), Möller–Trumbore intersection, path tracing integrator with Next Event Estimation and Russian roulette, PBR GGX/Cook-Torrance materials, ACES tone mapping. Full GPU port via OptiX to exploit hardware ray tracing.",
    results: "Working GPU rendering on complex glTF scenes (RTX 5070 Ti). The Neural BVH part remains a stated research goal, not yet implemented.",
  },
  hyperforge: {
    tag: "Blender add-on",
    status: "v1 done",
    summary: "Blender add-on to generate, animate and visualize the 6 regular 4-dimensional polytopes (tesseract, 120-cell, 600-cell...).",
    problem: "Make geometric objects of dimension higher than 3 — normally confined to abstract computation — manipulable by an artist, useful for morphing effects or non-Euclidean visuals.",
    approach: "Exact algebraic generation of each polytope's vertices (the 600-cell via even permutations of the golden ratio, the 120-cell by duality), 4D rotation composed of 6 elementary rotations per axis plane, and two visualization modes: slicing by a moving hyperplane and 4D→3D perspective projection. Pure NumPy math modules, testable outside Blender, decoupled from the UI/Geometry Nodes integration. The same 4D foundation (quaternions = 4-dimensional vectors) is also used to extract quaternion Julia sets by isosurface (marching cubes on a smoothed escape potential), outside the polytope framework.",
    results: "6 working polytopes, 2 visualization modes, 3 LOD levels, keyframe animation — add-on delivered in one focused development session.",
    videoLabels: [
      "5-cell (simplex) — 5 vertices, 10 edges",
      "8-cell (tesseract) — 16 vertices, 32 edges",
      "16-cell (cross-polytope) — 8 vertices, 24 edges",
      "24-cell — 24 vertices, 96 edges",
      "120-cell — 600 vertices, 1200 edges",
      "600-cell — 120 vertices, 720 edges",
      "Quaternion Julia set — c = (-0.2, 0.8, 0, 0)",
      "Quaternion Julia set — c = (-0.162, 0.163, 0.56, -0.599)",
      "Quaternion Julia set — c = (-0.45, -0.447, 0.181, 0.306)",
    ],
    mediaLabel: "6 regular 4D polytopes and 3 quaternion Julia sets",
  },
  "rl-mesh": {
    tag: "Reinforcement Learning",
    status: "in progress",
    summary: "An RL agent learns a character's physical locomotion by imitating mocap, with no manual key-framing.",
    problem: "Produce physically plausible, stylized character locomotion (walking, with controllable speed and heading) without frame-by-frame manual animation.",
    approach: "PD-actuated MuJoCo humanoid (PPO), trained by direct imitation of a mocap clip: residual around the reference pose, pose-tracking reward. Next step in progress: Adversarial Motion Priors (LSGAN discriminator + task reward on speed/heading), migrated to JAX/MJX to vectorize training across thousands of humanoids in parallel on GPU.",
    results: "On its best training run, the agent keeps walking without falling for the entire episode (300/300 steps). A dedicated evaluation script (eval_checkpoints.py) compares every checkpoint of a run to find the best one before a possible PPO collapse during long training. See the demo below.",
    mediaLabel: "6 training loops — PPO policy mid-training",
  },
  "erosion-hydraulique": {
    tag: "Blender add-on",
    status: "v1 done",
    summary: "Blender 5.0 extension simulating erosion on heightmaps, with two models: individual particles and grid-based runoff.",
    problem: "Blender has no native, physically plausible erosion tool: procedural terrains (noise + displace) stay smooth and lack a coherent drainage network, unlike real relief shaped by water.",
    approach: "Two complementary models. Particle (Beyer): each droplet follows the slope gradient with inertia, erodes according to its free transport capacity and deposits as it slows down, sediment bilinearly interpolated on the grid — good for fine, localized ravines. Grid (WaterSed, after BRGM/Landemaine et al.): simulates a full rain event over the whole terrain — priority-flood (Wang & Liu 2006) to fill depressions, Multiple Flow Direction routing (Freeman 1991) for natural flow instead of single-direction D8, Manning's formula for velocity, diffuse (splash) and concentrated (channel) erosion, transport and deposition based on carrying capacity.",
    results: "8 exposed parameters for Particle, 13 for WaterSed, 3 configurable output maps (erosion, deposition, runoff on a logarithmic scale) stored directly in bpy.data.images. Fully ported to the new Blender 5.0 API.",
    mediaLabel: "Real runoff map — output of the WaterSed (Grid) model",
  },
  "blender-version-manager": {
    tag: "Pipeline tool",
    status: "v1 done",
    summary: "Version manager for .blend files: automatic naming-convention detection, review statuses and a GUI built for VFX pipelines.",
    problem: "Without Perforce or Shotgun, a small team or a solo artist often manages .blend file versions by hand — inconsistent naming (_FINAL, _BACKUP, spaces), manual purges with no protection for active versions, no review-status tracking.",
    approach: "Automatic detection of the naming convention among 8 common patterns (scene_v001, scene-v001, sceneV001…), on a modular architecture separating the core (detection, version operations, statuses, linked assets) from the PyQt6 interface. A naming assistant that validates, flags and automatically fixes non-conforming files. Review-status tracking (WIP / ready for review / approved / rejected) with filtering. Hierarchical Show → Sequence → Shot structure with automatic detection of co-located renders/ and cache/ folders. Intelligent cleanup in dry-run, active versions protected.",
    results: "v2.2, light/dark themes, JSON/CSV report export, 32 unit and integration tests covering every module (pattern detection, file operations, statuses, linked assets, naming assistant).",
  },
};

type RenderText = Pick<Render, "title" | "blurb">;

const RENDER_TRANSLATIONS: Record<string, RenderText> = {
  foret: {
    title: "Forest",
    blurb: "Tracking shot following a character through instanced undergrowth, light filtered by the canopy. A study in shallow depth of field and atmospheric scattering under the trees.",
  },
  highland: {
    title: "Highland",
    blurb: "Flyover along a ridgeline at low sun. Volumetric clouds caught on the relief, high-altitude snow and haze that layers the planes out to the horizon.",
  },
  "cycle-de-course": {
    title: "Running cycle",
    blurb: "Low chase camera skimming a rain-soaked ground. Motion blur, mud kick-up and backlight, worked to carry the speed rather than describe it.",
  },
  mountain: {
    title: "Mountain",
    blurb: "Mountain lake at dusk. Ice sheets on the surface, peaks reflected on near-still water, camera sitting right at the waterline.",
  },
  "ville-abandonnee": {
    title: "Abandoned city",
    blurb: "Urban ruin reclaimed by vegetation, framed through a collapsed slab. Instanced ivy, volumetric haze and low light to separate the planes of a monochrome set.",
  },
};

export const PROJECTS_EN: Project[] = PROJECTS.map((p) => ({
  ...p,
  ...(PROJECT_TRANSLATIONS[p.slug] ?? {}),
})) as Project[];

export const RENDERS_EN: Render[] = RENDERS.map((r) => ({
  ...r,
  ...(RENDER_TRANSLATIONS[r.slug] ?? {}),
}));
