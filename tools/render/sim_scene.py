"""Simulation bourrasque generique (eau / gelee / sable / collider) + export
de mesh par frame via le mailleur natif, pour rendu video."""
import ctypes
import os
import sys
import time

import numpy as np

DLL = r"C:\Users\nicol\Code\bourrasque_v2\build_hires\Release\bourrasque.dll"

SCENE = sys.argv[1]
OUT_DIR = sys.argv[2]
N_FRAMES = int(sys.argv[3]) if len(sys.argv) > 3 else 90
GRID_RES = int(sys.argv[4]) if len(sys.argv) > 4 else 128

os.makedirs(OUT_DIR, exist_ok=True)

d = ctypes.CDLL(DLL)
F = ctypes.POINTER(ctypes.c_float)
I = ctypes.POINTER(ctypes.c_int32)


class Cfg(ctypes.Structure):
    _fields_ = [("grid_res", ctypes.c_int * 3), ("cell_size", ctypes.c_float),
                ("gravity_y", ctypes.c_float), ("cfl", ctypes.c_float),
                ("ppc_axis", ctypes.c_int), ("max_particles", ctypes.c_int)]


class Mat(ctypes.Structure):
    _fields_ = [("model", ctypes.c_int), ("rho", ctypes.c_float),
                ("E", ctypes.c_float), ("nu", ctypes.c_float),
                ("bulk", ctypes.c_float), ("gamma", ctypes.c_float),
                ("friction_angle", ctypes.c_float), ("cohesion", ctypes.c_float)]


class MesherCfg(ctypes.Structure):
    _fields_ = [("grid_res", ctypes.c_int * 3), ("cell_size", ctypes.c_float),
                ("influence_radius", ctypes.c_float), ("particle_radius", ctypes.c_float),
                ("collider_offset", ctypes.c_float), ("smoothing_iters", ctypes.c_int),
                ("min_component_tris", ctypes.c_int), ("channels", ctypes.c_int)]


sigs = [
    ("bq_default_config", [ctypes.POINTER(Cfg)], None),
    ("bq_create", [ctypes.POINTER(Cfg)], ctypes.c_void_p),
    ("bq_destroy", [ctypes.c_void_p], None),
    ("bq_add_material", [ctypes.c_void_p, ctypes.POINTER(Mat)], ctypes.c_int),
    ("bq_emit_box", [ctypes.c_void_p, ctypes.c_int, F, F, F], ctypes.c_int),
    ("bq_set_colliders", [ctypes.c_void_p, F, F, F, ctypes.POINTER(ctypes.c_int32), ctypes.c_int], ctypes.c_int),
    ("bq_step", [ctypes.c_void_p, ctypes.c_float], ctypes.c_int),
    ("bq_particle_count", [ctypes.c_void_p], ctypes.c_int),
    ("bq_read_positions", [ctypes.c_void_p, F], ctypes.c_int),
    ("bq_read_sdf", [ctypes.c_void_p, F], ctypes.c_int),
    ("bq_mesher_default_config", [ctypes.POINTER(MesherCfg)], None),
    ("bq_mesher_create", [ctypes.POINTER(MesherCfg)], ctypes.c_void_p),
    ("bq_mesher_destroy", [ctypes.c_void_p], None),
    ("bq_mesher_run", [ctypes.c_void_p, F, ctypes.c_int], ctypes.c_int),
    ("bq_mesher_set_collider_sdf", [ctypes.c_void_p, F, ctypes.POINTER(ctypes.c_int32), ctypes.c_float], ctypes.c_int),
    ("bq_mesher_counts", [ctypes.c_void_p, I, I], ctypes.c_int),
    ("bq_mesher_read", [ctypes.c_void_p, F, ctypes.POINTER(ctypes.c_int32), F], ctypes.c_int),
]
for name, argt, rest in sigs:
    getattr(d, name).argtypes = argt
    if rest:
        getattr(d, name).restype = rest
d.bq_last_error.restype = ctypes.c_char_p

cfg = Cfg()
d.bq_default_config(ctypes.byref(cfg))
cfg.grid_res[0] = GRID_RES
cfg.grid_res[1] = GRID_RES
cfg.grid_res[2] = GRID_RES
cfg.cell_size = 1.0 / GRID_RES
cfg.max_particles = 10_000_000

sim = d.bq_create(ctypes.byref(cfg))
if not sim:
    raise RuntimeError(f"bq_create: {d.bq_last_error().decode()}")

collider_tris = None  # (n_tri, 3, 3) float32, espace [0,1]^3

if SCENE == "water":
    mat = Mat(model=1, rho=1000.0, E=0.0, nu=0.0, bulk=4.0e4, gamma=3.0,
               friction_angle=0.0, cohesion=0.0)
    mid = d.bq_add_material(sim, ctypes.byref(mat))
    lo = (ctypes.c_float * 3)(0.10, 0.10, 0.10)
    hi = (ctypes.c_float * 3)(0.35, 0.60, 0.90)
    v0 = (ctypes.c_float * 3)(0.0, 0.0, 0.0)
    d.bq_emit_box(sim, mid, lo, hi, v0)

elif SCENE == "jelly":
    mat = Mat(model=0, rho=1000.0, E=5.0e4, nu=0.2, bulk=0.0, gamma=0.0,
               friction_angle=0.0, cohesion=0.0)
    mid = d.bq_add_material(sim, ctypes.byref(mat))
    lo = (ctypes.c_float * 3)(0.30, 0.55, 0.30)
    hi = (ctypes.c_float * 3)(0.70, 0.85, 0.70)
    v0 = (ctypes.c_float * 3)(0.0, -2.0, 0.0)
    d.bq_emit_box(sim, mid, lo, hi, v0)

elif SCENE == "sand":
    mat = Mat(model=2, rho=1600.0, E=3.5e5, nu=0.3, bulk=0.0, gamma=0.0,
               friction_angle=35.0, cohesion=0.0)
    mid = d.bq_add_material(sim, ctypes.byref(mat))
    lo = (ctypes.c_float * 3)(0.15, 0.15, 0.30)
    hi = (ctypes.c_float * 3)(0.40, 0.75, 0.70)
    v0 = (ctypes.c_float * 3)(0.0, 0.0, 0.0)
    d.bq_emit_box(sim, mid, lo, hi, v0)

elif SCENE == "collider":
    mat = Mat(model=1, rho=1000.0, E=0.0, nu=0.0, bulk=4.0e4, gamma=3.0,
               friction_angle=0.0, cohesion=0.0)
    mid = d.bq_add_material(sim, ctypes.byref(mat))
    lo = (ctypes.c_float * 3)(0.30, 0.65, 0.30)
    hi = (ctypes.c_float * 3)(0.70, 0.90, 0.70)
    v0 = (ctypes.c_float * 3)(0.0, 0.0, 0.0)
    d.bq_emit_box(sim, mid, lo, hi, v0)

    # rampe statique inclinee : solide FERME (plaque avec epaisseur), pour que
    # le SDF ait un "interieur" bien defini (un plan ouvert rend un demi-espace
    # entier solide au lieu du seul volume de la plaque -> cropping errone).
    cx, cz = 0.5, 0.5
    y0, y1 = 0.15, 0.42
    hw = 0.42
    th = 0.03  # epaisseur, le long de la normale (approx. -Y)
    t1 = np.array([cx - hw, y0, cz - hw])
    t2 = np.array([cx + hw, y1, cz - hw])
    t3 = np.array([cx + hw, y1, cz + hw])
    t4 = np.array([cx - hw, y0, cz + hw])
    b1, b2, b3, b4 = (p - np.array([0, th, 0]) for p in (t1, t2, t3, t4))

    def quad(a, b, c, d_):
        # ordre inverse : le solveur/mailleur attend la normale
        # (b-a)x(c-a) pointant VERS L'INTERIEUR du solide, pas vers l'exterieur
        return [[a, c, b], [a, d_, c]]

    tris = []
    tris += quad(t1, t2, t3, t4)          # dessus
    tris += quad(b4, b3, b2, b1)          # dessous
    tris += quad(t1, t4, b4, b1)          # cote x-
    tris += quad(t2, t1, b1, b2)          # cote z-
    tris += quad(t3, t2, b2, b3)          # cote x+
    tris += quad(t4, t3, b3, b4)          # cote z+
    collider_tris = np.array(tris, dtype=np.float32)

else:
    raise ValueError(f"scene inconnue: {SCENE}")

print(f"[sim] scene={SCENE} grid={GRID_RES}^3 cell={cfg.cell_size:.5f}  "
      f"{d.bq_particle_count(sim)} particules emises", flush=True)

if collider_tris is not None:
    n_tri = collider_tris.shape[0]
    tri = np.ascontiguousarray(collider_tris, dtype=np.float32)
    vel = np.zeros_like(tri)
    fric = np.full(n_tri, 0.3, dtype=np.float32)
    r = d.bq_set_colliders(sim, tri.ctypes.data_as(F), vel.ctypes.data_as(F),
                            fric.ctypes.data_as(F), None, n_tri)
    if r != 0:
        raise RuntimeError(f"set_colliders: {d.bq_last_error().decode()}")
    print(f"[sim] {n_tri} triangles collider poses", flush=True)

mcfg = MesherCfg()
d.bq_mesher_default_config(ctypes.byref(mcfg))
mesh_res = min(GRID_RES * 2, 384)
mcfg.grid_res[0] = mesh_res
mcfg.grid_res[1] = mesh_res
mcfg.grid_res[2] = mesh_res
mcfg.cell_size = 1.0 / mesh_res
mcfg.influence_radius = 3.0 / mesh_res
mcfg.particle_radius = 1.0 / mesh_res

mesher = d.bq_mesher_create(ctypes.byref(mcfg))
if not mesher:
    raise RuntimeError(f"mesher_create: {d.bq_last_error().decode()}")

buf = np.empty((cfg.max_particles, 3), dtype=np.float32)
n_cells = GRID_RES * GRID_RES * GRID_RES
sdf_buf = np.empty(n_cells, dtype=np.float32)
mesher_res_arr = (ctypes.c_int32 * 3)(GRID_RES, GRID_RES, GRID_RES)

t0 = time.time()
for fr in range(N_FRAMES):
    if collider_tris is not None:
        n_tri = collider_tris.shape[0]
        tri = np.ascontiguousarray(collider_tris, dtype=np.float32)
        vel = np.zeros_like(tri)
        fric = np.full(n_tri, 0.3, dtype=np.float32)
        d.bq_set_colliders(sim, tri.ctypes.data_as(F), vel.ctypes.data_as(F),
                            fric.ctypes.data_as(F), None, n_tri)
    if d.bq_step(sim, 1.0 / 24.0) < 0:
        raise RuntimeError(f"bq_step: {d.bq_last_error().decode()}")
    n = d.bq_particle_count(sim)
    d.bq_read_positions(sim, buf.ctypes.data_as(F))
    pos = buf[:n]

    if collider_tris is not None:
        if d.bq_read_sdf(sim, sdf_buf.ctypes.data_as(F)) < 0:
            raise RuntimeError(f"read_sdf: {d.bq_last_error().decode()}")
        r = d.bq_mesher_set_collider_sdf(mesher, sdf_buf.ctypes.data_as(F),
                                          mesher_res_arr, cfg.cell_size)
        if r < 0:
            raise RuntimeError(f"mesher_set_collider_sdf: {d.bq_last_error().decode()}")

    if d.bq_mesher_run(mesher, pos.ctypes.data_as(F), n) < 0:
        raise RuntimeError(f"mesher_run: {d.bq_last_error().decode()}")
    nv = ctypes.c_int32(0)
    nt = ctypes.c_int32(0)
    d.bq_mesher_counts(mesher, ctypes.byref(nv), ctypes.byref(nt))
    nv, nt = nv.value, nt.value

    verts = np.empty((nv, 3), dtype=np.float32)
    tris = np.empty((nt, 3), dtype=np.int32)
    if nv > 0 and nt > 0:
        d.bq_mesher_read(mesher, verts.ctypes.data_as(F),
                          tris.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)), None)

    out_path = os.path.join(OUT_DIR, f"frame_{fr:04d}.npz")
    np.savez(out_path, verts=verts, tris=tris)
    if fr % 10 == 0 or fr == N_FRAMES - 1:
        elapsed = time.time() - t0
        print(f"[frame {fr:4d}/{N_FRAMES}] {n:>8} particules  {nv:>7} verts  {nt:>7} tris  "
              f"({elapsed:.1f}s ecoule)", flush=True)

d.bq_mesher_destroy(mesher)
d.bq_destroy(sim)
print(f"[done] {N_FRAMES} frames en {time.time()-t0:.1f}s -> {OUT_DIR}", flush=True)
