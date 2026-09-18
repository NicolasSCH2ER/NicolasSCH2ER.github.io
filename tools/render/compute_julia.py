"""Extrait l'isosurface d'un ensemble de Julia quaternionique par marching cubes.

q -> q^2 + c, q = (x, y, z, w_slice) quaternion, iteration echappement.
Tourne sous le python systeme (scikit-image/scipy installes), independant de Blender.
"""
import sys
import numpy as np
from skimage import measure

argv = sys.argv[1:]
out_path = argv[0]
cx, cy, cz, cw = (float(v) for v in argv[1:5])
w_slice = float(argv[5]) if len(argv) > 5 else 0.0
res = int(argv[6]) if len(argv) > 6 else 180
max_iter = int(argv[7]) if len(argv) > 7 else 12
bound = float(argv[8]) if len(argv) > 8 else 1.5
level_frac = float(argv[9]) if len(argv) > 9 else 0.5

lin = np.linspace(-bound, bound, res, dtype=np.float64)
X, Y, Z = np.meshgrid(lin, lin, lin, indexing="ij")
qx, qy, qz = X.copy(), Y.copy(), Z.copy()
qw = np.full_like(X, w_slice)

bailout = 4.0
escape2 = bailout * bailout
# potentiel lisse (a la Mandelbrot) : le compte d'iterations brut est un entier
# -> isosurface en marches d'escalier. On interpole avec la magnitude exacte
# au moment de l'echappement pour obtenir un champ continu.
esc_smooth = np.full(X.shape, float(max_iter), dtype=np.float64)
active = np.ones(X.shape, dtype=bool)

for it in range(max_iter):
    # produit quaternionique q*q (q = qx + qy i + qz j + qw k)
    nqx = qx * qx - qy * qy - qz * qz - qw * qw + cx
    nqy = 2 * qx * qy + cy
    nqz = 2 * qx * qz + cz
    nqw = 2 * qx * qw + cw
    qx, qy, qz, qw = nqx, nqy, nqz, nqw
    mag2 = qx * qx + qy * qy + qz * qz + qw * qw
    newly_escaped = active & (mag2 > escape2)
    if np.any(newly_escaped):
        mag = np.sqrt(mag2[newly_escaped])
        smooth = (it + 1) - np.log2(np.log(mag) / np.log(bailout))
        esc_smooth[newly_escaped] = smooth
    active &= ~newly_escaped
    # clamp pour eviter overflow sur les points deja echappes
    qx = np.where(active, qx, 0.0)
    qy = np.where(active, qy, 0.0)
    qz = np.where(active, qz, 0.0)
    qw = np.where(active, qw, 0.0)

field = esc_smooth  # champ scalaire continu : potentiel d'echappement
# niveau bas (proche de 0) = surface gonflee, comble les trous/details fins ;
# niveau haut (proche de max_iter) = surface serree sur la frontiere fractale
# reelle, qui a un genre (trous) non trivial. level_frac pilote ce compromis.
level = max_iter * level_frac

verts, faces, normals, _ = measure.marching_cubes(field, level=level)
# reprojection dans l'espace [-bound, bound]
scale = (2 * bound) / (res - 1)
verts = verts * scale - bound

np.savez(out_path, verts=verts.astype(np.float32), faces=faces.astype(np.int32),
         normals=normals.astype(np.float32))
print(f"[done] {out_path}: {len(verts)} verts, {len(faces)} faces", flush=True)
