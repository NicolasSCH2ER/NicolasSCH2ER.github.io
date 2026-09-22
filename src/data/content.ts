export type Project = {
  slug: string;
  title: string;
  year: string;
  tag: string;
  stack: string[];
  /* string libre (pas d'union stricte) : la version anglaise (content.en.ts)
     doit pouvoir porter ses propres libellés de statut sans forcer un cast. */
  status: string;
  summary: string;
  problem: string;
  approach: string;
  results: string;
  github?: string;
  image?: string;
  videos?: string[];
  videoLabels?: string[];
  /* Legende de la galerie. Le champ `videos` porte aussi des JPG/GIF selon le
     projet, donc le libelle ne peut pas etre deduit du nombre de fichiers. */
  mediaLabel?: string;
  /* `upAxis` : axe vertical du maillage exporte. glTF impose +Y ; les exports
     issus du solveur sont en Z-up et doivent etre redresses a l'affichage. */
  model?: { src: string; poster?: string; label?: string; upAxis?: "y" | "z" };
  hue: number;
};

export type Render = {
  slug: string;
  title: string;
  tools: string[];
  loop: string;
  blurb: string;
  hue: number;
  aspect: "portrait" | "landscape" | "square";
};

export const PROJECTS: Project[] = [
  {
    slug: "bourrasque",
    title: "bourrasque_v2",
    year: "2026",
    tag: "Simulation fluide",
    stack: ["C++", "CUDA", "Python", "Blender API"],
    status: "actif",
    summary: "Solveur de simulation fluides et matériaux (eau, élastique, sable) accéléré GPU, avec extension Blender pour l'intégration artiste.",
    problem: "Mantaflow, le solveur natif de Blender, est CPU-only et lent à itérer ; les solveurs GPU commerciaux (Hurricane, FLIP Fluids) sont propriétaires et fermés.",
    approach: "Solveur MLS-MPM (Material Point Method) avec transferts APIC en CUDA pur : chaque matériau — élastique corotationnel, eau, sable en cours (plasticité de Drucker-Prager) — n'est qu'une fonction de contrainte ajoutée au même pipeline particules ↔ grille. Chaque évolution de l'algorithme est d'abord prototypée et validée dans une référence NumPy avant transcription en CUDA. Extension Blender pour viewport live, colliders SDF et export de maillage.",
    results: "SVD 3×3 GPU validée à 1,9·10⁻⁴ près de NumPy sur 5402 matrices · modèle de sable validé par angle de repos (25°/35°/45°) · 184/185 tests passés (le dernier est un test d'interop qui saute proprement quand sa fixture binaire de 600 Mo n'est pas régénérée localement) · dam-break à grille 128³ simulé jusqu'à 2,9 M particules par frame, maillage reconstruit à la volée par le mailleur Zhu-Bridson natif du solveur (jusqu'à 3,2 M triangles/frame), ~7,6 s/frame en pipeline complet simulation + reconstruction + rendu Cycles.",
    github: "https://github.com/NicolasSCH2ER/bourrasque_v2",
    image: "/media/projects/bourrasque.jpg",
    videos: [
      "/media/projects/bourrasque-dam.mp4",
      "/media/projects/bourrasque-jelly.mp4",
      "/media/projects/bourrasque-sand.mp4",
      "/media/projects/bourrasque-collider.mp4",
    ],
    videoLabels: [
      "Eau — dam-break, grille 128³",
      "Élastique — chute et rebond",
      "Sable — effondrement granulaire (Drucker-Prager)",
      "Collider statique — éclaboussure sur rampe",
    ],
    mediaLabel: "4 simulations réelles du solveur — captures de rendu Cycles",
    hue: 220,
  },
  {
    slug: "bvhnet",
    title: "BVHNet",
    year: "2026",
    tag: "Moteur de rendu",
    stack: ["C++", "CUDA", "OptiX", "OpenMP"],
    status: "v1 terminée",
    summary: "Path tracer physiquement basé, en CPU (OpenMP) et GPU (OptiX / RT cores), avec import de scènes glTF exportées de Blender.",
    problem: "Comprendre et contrôler chaque étage d'un pipeline de path tracing — construction du BVH, intersection, échantillonnage — avec l'ambition à terme de remplacer l'heuristique de traversée par un petit réseau de neurones (Neural BVH).",
    approach: "BVH binaire construit par tri de centroïdes (SAH simplifié), intersection Möller–Trumbore, intégrateur path tracing avec Next Event Estimation et roulette russe, matériaux PBR GGX/Cook-Torrance, tone mapping ACES. Portage GPU complet via OptiX pour exploiter le hardware ray tracing.",
    results: "Rendu GPU fonctionnel sur scènes glTF complexes (RTX 5070 Ti). Le volet Neural BVH reste un objectif de recherche affiché, pas encore implémenté.",
    github: "https://github.com/NicolasSCH2ER/BVHNET",
    image: "/media/projects/bvhnet.jpg",
    hue: 15,
  },
  {
    slug: "hyperforge",
    title: "hyperforge",
    year: "2026",
    tag: "Addon Blender",
    stack: ["Python", "NumPy", "Blender API", "Geometry Nodes"],
    status: "v1 terminée",
    summary: "Add-on Blender pour générer, animer et visualiser les 6 polytopes réguliers de dimension 4 (tesseract, 120-cell, 600-cell...).",
    problem: "Rendre manipulables par un artiste des objets géométriques de dimension supérieure à 3, normalement réservés au calcul abstrait — utile pour des effets de morphing ou des visuels non-euclidiens.",
    approach: "Génération algébrique exacte des sommets de chaque polytope (le 600-cell via permutations paires du nombre d'or, le 120-cell par dualité), rotation 4D composée de 6 rotations élémentaires par plan d'axes, et deux modes de visualisation : coupe par hyperplan mobile et projection perspective 4D→3D. Modules mathématiques purs NumPy testables hors Blender, découplés de l'intégration UI/Geometry Nodes. Le même socle 4D (quaternions = vecteurs de dimension 4) sert aussi à extraire des ensembles de Julia quaternioniques par isosurface (marching cubes sur un potentiel d'échappement lissé), en dehors du cadre polytopes.",
    results: "6 polytopes fonctionnels, 2 modes de visualisation, 3 niveaux de LOD, animation par keyframe — add-on livré en une session de développement ciblée.",
    image: "/media/projects/hyperforge.jpg",
    videos: [
      "/media/projects/hyperforge-cells/cell5.jpg",
      "/media/projects/hyperforge-cells/cell8.jpg",
      "/media/projects/hyperforge-cells/cell16.jpg",
      "/media/projects/hyperforge-cells/cell24.jpg",
      "/media/projects/hyperforge-cells/cell120.jpg",
      "/media/projects/hyperforge-cells/cell600.jpg",
      "/media/projects/hyperforge-julia/julia-a.jpg",
      "/media/projects/hyperforge-julia/julia-b.jpg",
      "/media/projects/hyperforge-julia/julia-c.jpg",
    ],
    videoLabels: [
      "5-cell (simplexe) — 5 sommets, 10 arêtes",
      "8-cell (tesseract) — 16 sommets, 32 arêtes",
      "16-cell (polytope croisé) — 8 sommets, 24 arêtes",
      "24-cell — 24 sommets, 96 arêtes",
      "120-cell — 600 sommets, 1200 arêtes",
      "600-cell — 120 sommets, 720 arêtes",
      "Julia quaternionique — c = (-0.2, 0.8, 0, 0)",
      "Julia quaternionique — c = (-0.162, 0.163, 0.56, -0.599)",
      "Julia quaternionique — c = (-0.45, -0.447, 0.181, 0.306)",
    ],
    mediaLabel: "6 polytopes réguliers 4D et 3 ensembles de Julia quaternioniques",
    model: {
      src: "/media/models/hyperforge-tesseract.glb",
      poster: "/media/projects/hyperforge-cells/cell8.jpg",
      label: "tesseract (8-cell) · orbit",
    },
    hue: 285,
  },
  {
    slug: "rl-mesh",
    title: "rl_mesh",
    year: "2026",
    tag: "Reinforcement Learning",
    stack: ["Python", "PyTorch", "MuJoCo / MJX", "JAX"],
    status: "en cours",
    summary: "Un agent RL apprend la locomotion physique d'un personnage par imitation de mocap, sans key-framing manuel.",
    problem: "Produire une locomotion de personnage physiquement plausible et stylisée (marche, vitesse et cap contrôlables) sans animation manuelle image par image.",
    approach: "Humanoïde MuJoCo actionné par PD (PPO), entraîné par imitation directe d'un clip de mocap : résidu autour de la pose de référence, reward de suivi de pose. Étape suivante en cours : Adversarial Motion Priors (discriminateur LSGAN + reward de tâche sur vitesse/cap), migré vers JAX/MJX pour vectoriser l'entraînement de milliers d'humanoïdes en parallèle sur GPU.",
    results: "Sur son meilleur run d'entraînement, l'agent tient la marche sans tomber sur l'intégralité de l'épisode (300/300 steps). Un script d'évaluation dédié (eval_checkpoints.py) compare tous les checkpoints d'un run pour repérer le meilleur avant un éventuel effondrement de PPO en entraînement long. Voir la démo ci-dessous.",
    image: "/media/projects/rl-mesh.jpg",
    videos: [
      "/media/projects/rlmesh-loops/loop-1.mp4",
      "/media/projects/rlmesh-loops/loop-2.mp4",
      "/media/projects/rlmesh-loops/loop-3.mp4",
      "/media/projects/rlmesh-loops/loop-4.mp4",
      "/media/projects/rlmesh-loops/loop-5.mp4",
      "/media/projects/rlmesh-loops/loop-6.mp4",
    ],
    mediaLabel: "6 boucles d'entraînement — politique PPO en cours d'apprentissage",
    hue: 320,
  },
  {
    slug: "erosion-hydraulique",
    title: "Érosion hydraulique",
    year: "2026",
    tag: "Addon Blender",
    stack: ["Python", "Blender API", "NumPy"],
    status: "v1 terminée",
    summary: "Extension Blender 5.0 de simulation d'érosion sur heightmaps, avec deux modèles : particules individuelles et ruissellement sur grille.",
    problem: "Blender n'a pas d'outil natif d'érosion physiquement plausible : les terrains procéduraux (bruit + displace) restent lisses et sans réseau de drainage cohérent, contrairement à un vrai relief façonné par l'eau.",
    approach: "Deux modèles complémentaires. Particle (Beyer) : chaque goutte suit le gradient de pente avec inertie, érode selon sa capacité de transport libre et dépose en ralentissant, sédiments interpolés bilinéairement sur la grille — bon pour des ravines fines et localisées. Grid (WaterSed, d'après BRGM/Landemaine et al.) : simule un évènement pluvieux complet sur tout le terrain — priority-flood (Wang & Liu 2006) pour combler les cuvettes, routage Multiple Flow Direction (Freeman 1991) pour un écoulement naturel plutôt qu'un D8 à direction unique, vitesse par la formule de Manning, érosion diffuse (splash) et concentrée (chenaux), transport et dépôt selon la capacité de charge.",
    results: "8 paramètres exposés pour Particle, 13 pour WaterSed, 3 maps de sortie configurables (érosion, dépôt, ruissellement en échelle logarithmique) stockées directement en bpy.data.images. Portage complet sur la nouvelle API Blender 5.0.",
    github: "https://github.com/NicolasSCH2ER/Hydraulic-Erosion",
    image: "/media/projects/erosion.jpg",
    mediaLabel: "Carte de ruissellement réelle — sortie du modèle WaterSed (Grid)",
    hue: 95,
  },
  {
    slug: "blender-version-manager",
    title: "Blender Version Manager",
    year: "2026",
    tag: "Outil pipeline",
    stack: ["Python", "PyQt6"],
    status: "v1 terminée",
    summary: "Gestionnaire de versions pour fichiers .blend : détection automatique de nomenclature, statuts de revue et interface graphique pensée pipeline VFX.",
    problem: "Sans Perforce ni Shotgun, une petite équipe ou un solo gère souvent ses versions de fichiers .blend à la main — nommage incohérent (_FINAL, _BACKUP, espaces), purge manuelle sans protection des versions actives, aucun suivi de statut de revue.",
    approach: "Détection automatique de la convention de nommage parmi 8 patterns courants (scene_v001, scene-v001, sceneV001…), sur une architecture modulaire séparant le cœur (détection, opérations de version, statuts, assets liés) de l'interface PyQt6. Assistant de nommage qui valide, signale et corrige automatiquement les fichiers non conformes. Suivi de statut de revue (WIP / prêt pour revue / approuvé / rejeté) avec filtrage. Structure hiérarchique Show → Séquence → Shot avec détection automatique des dossiers renders/ et cache/ colocalisés. Nettoyage intelligent en dry-run, versions actives protégées.",
    results: "v2.2, thèmes clair/sombre, export de rapports JSON/CSV, 32 tests unitaires et d'intégration couvrant chaque module (détection de patterns, opérations de fichiers, statuts, assets liés, assistant de nommage).",
    github: "https://github.com/NicolasSCH2ER/Blender_Version_manager",
    hue: 205,
  },
];

export const RENDERS: Render[] = [
  {
    slug: "foret",
    title: "Forêt",
    tools: ["Blender", "Cycles"],
    loop: "20s",
    blurb: "Travelling d'accompagnement derrière un personnage, sous-bois instancié et lumière filtrée par la canopée. Étude de profondeur de champ courte et de diffusion atmosphérique en sous-bois.",
    hue: 145,
    aspect: "landscape",
  },
  {
    slug: "highland",
    title: "Highland",
    tools: ["Blender", "Cycles"],
    loop: "15s",
    blurb: "Survol d'une ligne de crête au soleil rasant. Nuages volumétriques accrochés au relief, neige d'altitude et brume qui étage les plans jusqu'à l'horizon.",
    hue: 40,
    aspect: "landscape",
  },
  {
    slug: "cycle-de-course",
    title: "Cycle de course",
    tools: ["Blender", "Cycles"],
    loop: "16s",
    blurb: "Caméra basse en poursuite, au ras d'un sol détrempé. Flou de mouvement, projections de boue et contre-jour travaillés pour porter la vitesse plutôt que la décrire.",
    hue: 25,
    aspect: "landscape",
  },
  {
    slug: "mountain",
    title: "Mountain",
    tools: ["Blender", "Cycles"],
    loop: "19s",
    blurb: "Lac de montagne à la tombée du jour. Plaques de glace en surface, réflexion des sommets sur une eau presque immobile, caméra posée au ras de l'eau.",
    hue: 220,
    aspect: "landscape",
  },
  {
    slug: "ville-abandonnee",
    title: "Ville abandonnée",
    tools: ["Blender", "Cycles"],
    loop: "15s",
    blurb: "Ruine urbaine reprise par la végétation, cadrée à travers une dalle effondrée. Lierre instancié, brume volumétrique et lumière rasante pour séparer les plans d'un décor monochrome.",
    hue: 55,
    aspect: "landscape",
  },
];
