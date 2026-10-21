# Technische Zeichnung (A4 quer, Maßstab 1:2) der Loft-Vase mit Schriftzug als PDF, Beschriftung englisch.
# Liest die STL von vase.py: Ansicht auf die Schriftseite, Längsschnitt B-B, Draufsicht mit Querschnitten.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from manifold3d import Manifold, Mesh

STL = "/Users/haraldbeker/Allerlei/vase_kupfer_evolution.stl"
PDF = "/Users/haraldbeker/Allerlei/vase_evolution_drawing.pdf"
M = 0.5                                     # Maßstab 1:2
# Werte aus vase.py
SCHNITTE = [(3, 52, 0, 0), (4, 58, 50, 25), (5, 60, 100, 50), (6, 50, 150, 75), (0, 38, 200, 90)]
ECKRADIUS, WAND, BODEN = 6.0, 2.5, 3.0
TEXT, TEXTHOEHE, RELIEF, TEXT_NEIGUNG, TEXT_Z, TEXT_WINKEL = "Evolution", 17.0, 1.2, 35.0, 100.0, -112.0
NAMEN = {3: "Triangle", 4: "Square", 5: "Pentagon", 6: "Hexagon", 0: "Circle"}

raw = np.fromfile(STL, dtype=[("d", "<f4", 12), ("a", "<u2")], offset=84)["d"][:, 3:].reshape(-1, 3)
uv, idx = np.unique(np.round(raw, 4), axis=0, return_inverse=True)
vase = Manifold(Mesh(vert_properties=uv.astype(np.float32), tri_verts=idx.reshape(-1, 3).astype(np.uint32)))
volumen = vase.volume()
# drehen, sodass die Schriftseite zum Betrachter (-Y) zeigt
vase_v = vase.rotate([0, 0, -90 - TEXT_WINKEL])

fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 297); ax.set_ylim(0, 210); ax.set_aspect("equal"); ax.axis("off")
DICK, DUENN, FS = 0.7, 0.25, 7

def linie(pts, lw=DUENN, **k):
    pts = np.asarray(pts); ax.plot(pts[:, 0], pts[:, 1], color="black", lw=lw, solid_capstyle="butt", **k)

def mittellinie(p1, p2):
    linie([p1, p2], lw=DUENN, dashes=(8, 2, 1.5, 2))

def pfeil(spitze, richtung):
    d = np.asarray(richtung, float); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    s = np.asarray(spitze, float)
    ax.fill(*np.array([s, s - 2.5 * d + 0.5 * n, s - 2.5 * d - 0.5 * n]).T, color="black", lw=0)

def mass(p1, p2, abstand, text, achse):
    """Maßlinie zwischen p1 und p2 (Blattkoordinaten), parallel zu 'x' oder 'y', um 'abstand' versetzt."""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    if achse == "x":
        y = p1[1] + abstand; a, b = np.array([p1[0], y]), np.array([p2[0], y])
        for p in (p1, p2): linie([p + [0, np.sign(abstand)], [p[0], y + np.sign(abstand) * 1.5]])
        ax.text((a[0] + b[0]) / 2, y + 0.8, text, ha="center", va="bottom", fontsize=FS)
    else:
        x = p1[0] + abstand; a, b = np.array([x, p1[1]]), np.array([x, p2[1]])
        for p in (p1, p2): linie([p + [np.sign(abstand), 0], [x + np.sign(abstand) * 1.5, p[1]]])
        ax.text(x - 0.8, (a[1] + b[1]) / 2, text, ha="right", va="center", rotation=90, fontsize=FS)
    linie([a, b]); pfeil(a, a - b); pfeil(b, b - a)

def hinweis(spitze, text_pos, text):
    ax.annotate(text, xy=spitze, xytext=text_pos, fontsize=FS, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=DUENN, color="black", mutation_scale=6))

def polygone(polys, ox, oy, lw=DICK, schraffur=False, **k):
    verts, codes = [], []
    for p in polys:
        p = np.asarray(p) * M + [ox, oy]
        verts += p.tolist() + [p[0].tolist()]; codes += [Path.MOVETO] + [Path.LINETO] * (len(p) - 1) + [Path.CLOSEPOLY]
    pfad = Path(verts, codes)
    if schraffur:
        ax.add_patch(PathPatch(pfad, facecolor="white", edgecolor="none"))
        ax.add_patch(PathPatch(pfad, facecolor="none", edgecolor="black", lw=0, hatch="//////"))
    ax.add_patch(PathPatch(pfad, facecolor="none", edgecolor="black", lw=lw, **k))

# Rahmen und Schriftfeld
linie([[10, 10], [287, 10], [287, 200], [10, 200], [10, 10]], lw=DICK)
sx, sy, sw, sh = 187, 10, 100, 36
linie([[sx, sy + sh], [sx, sy]], lw=DICK); linie([[sx, sy + sh], [sx + sw, sy + sh]], lw=DICK)
for yy in (sy + 9, sy + 18, sy + 27): linie([[sx, yy], [sx + sw, yy]])
linie([[sx + 50, sy], [sx + 50, sy + 27]])
for x, y, t, fs, fw in [
    (sx + 2, sy + 31.5, f"Vase “{TEXT}” – Loft 3/4/5/6-gon → Circle", 8.5, "bold"),
    (sx + 2, sy + 22.5, "Material: copper, brushed", FS, None),
    (sx + 52, sy + 22.5, f"Volume: ≈ {volumen / 1000:.0f} cm³", FS, None),
    (sx + 2, sy + 13.5, "Scale: 1:2", FS, None),
    (sx + 52, sy + 13.5, "Dimensions in mm", FS, None),
    (sx + 2, sy + 4.5, "General tolerance ISO 2768-m", FS, None),
    (sx + 52, sy + 4.5, "Date: 2026-10-21   Sheet 1/1", FS, None)]:
    ax.text(x, y, t, fontsize=fs, fontweight=fw, va="center")

# --- Ansicht auf die Schriftseite: orthogonal projiziert, schattiert ---
ax0, ay0 = 52, 62                                   # Blattposition von (x=0, z=0)
ax.text(ax0, ay0 + 200 * M + 12, "Front view", ha="center", fontsize=9, fontweight="bold")
# orthogonal mit OpenGL gerendert (Blick in +Y), als Bild maßstäblich eingesetzt
import moderngl
mm = vase_v.to_mesh()
v, f = np.array(mm.vert_properties)[:, :3], np.array(mm.tri_verts)
fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
vn = np.zeros_like(v)
for k in range(3): np.add.at(vn, f[:, k], fn)
vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
xmin, xmax = v[:, 0].min() - 1, v[:, 0].max() + 1
PX = 24                                             # Pixel pro mm Blatt
Wp, Hp = int((xmax - xmin) * M * PX), int(202 * M * PX)
ctx = moderngl.create_standalone_context()
prog = ctx.program(vertex_shader="""
#version 410
uniform vec4 bereich; in vec3 pos; in vec3 nrm; out vec3 n;
void main() { n = nrm; gl_Position = vec4((pos.x - bereich.x) / bereich.y * 2.0 - 1.0,
                                          (pos.z - bereich.z) / bereich.w * 2.0 - 1.0, pos.y / 200.0, 1.0); }
""", fragment_shader="""
#version 410
in vec3 n; out vec4 c;
void main() { vec3 N = normalize(n); vec3 L = normalize(vec3(-0.6, -1.0, 0.7));
  float d = max(dot(N, L), 0.0); float s = pow(max(dot(reflect(-L, N), vec3(0, -1, 0)), 0.0), 20.0);
  c = vec4(vec3(0.42 + 0.5 * d + 0.25 * s), 1.0); }
""")
prog["bereich"].value = (xmin, xmax - xmin, -1.0, 202.0)
vao = ctx.vertex_array(prog, [(ctx.buffer(np.hstack([v, vn]).astype("f4").tobytes()), "3f 3f", "pos", "nrm")],
                       ctx.buffer(f.astype("u4").tobytes()))
fbo = ctx.simple_framebuffer((Wp, Hp)); fbo.use(); fbo.clear(1, 1, 1, 0); ctx.enable(moderngl.DEPTH_TEST)
vao.render()
bild = np.frombuffer(fbo.read(components=4), np.uint8).reshape(Hp, Wp, 4)[::-1]
ax.imshow(bild, extent=[ax0 + xmin * M, ax0 + xmax * M, ay0 - 1 * M, ay0 + 201 * M], interpolation="lanczos", zorder=1)
xmin, xmax = v[:, 0].min(), v[:, 0].max()
mittellinie([ax0, ay0 - 5], [ax0, ay0 + 200 * M + 5])
umriss = vase_v.rotate([90, 0, 0])                 # Umriss = Projektion auf X-Z-Ebene
polygone([np.c_[p[:, 0], -p[:, 1]] for p in map(np.asarray, umriss.project().to_polygons())], ax0, ay0, lw=DICK)
mass([ax0 + xmin * M, ay0], [ax0 + xmin * M, ay0 + 200 * M], -8, "200", "y")
hinweis([ax0 - 4, ay0 + (TEXT_Z - 6) * M], [ax0 - 40, ay0 - 9],
        f"Lettering “{TEXT}” raised {RELIEF:g}")
# Höhenmarken der Querschnitte
for nE, R, z, d in SCHNITTE:
    linie([[ax0 + xmax * M + 3, ay0 + z * M], [ax0 + xmax * M + 9, ay0 + z * M]])
    ax.text(ax0 + xmax * M + 10, ay0 + z * M, f"{z:g}  {NAMEN[nE]}", fontsize=FS - 1, va="center")

# --- Schnitt B–B: Längsschnitt durch die Achse (Ebene parallel zur Ansicht) ---
bx0, by0 = 150, 62
ax.text(bx0, by0 + 200 * M + 12, "Section B–B", ha="center", fontsize=9, fontweight="bold")
sch = [np.c_[p[:, 0], -p[:, 1]] for p in map(np.asarray, vase_v.rotate([90, 0, 0]).slice(0.0).to_polygons())]
polygone(sch, bx0, by0, schraffur=True)
mittellinie([bx0, by0 - 5], [bx0, by0 + 200 * M + 5])
alle = np.vstack(sch)
oben = alle[alle[:, 1] > 199.5]
mass([bx0 + oben[:, 0].min() * M, by0 + 200 * M], [bx0 + oben[:, 0].max() * M, by0 + 200 * M], 6,
     f"Ø{oben[:, 0].max() - oben[:, 0].min():.0f}", "x")
hinweis([bx0 + 2, by0 + BODEN * M / 2], [bx0 + 14, by0 - 9], f"Bottom {BODEN:g}")
zr = 120
rechts = alle[np.abs(alle[:, 1] - zr) < 1.5][:, 0].max()
hinweis([bx0 + (rechts - WAND / 2) * M, by0 + zr * M], [bx0 + 34, by0 + zr * M + 14], f"Wall {WAND:g}")

# --- Draufsicht: Querschnitte der Außenkontur in den Konstruktionshöhen ---
dx0, dy0 = 245, 128
ax.text(dx0, dy0 + 48, "Top view / cross-sections", ha="center", fontsize=9, fontweight="bold")
stile = {0: dict(lw=DICK), 50: dict(lw=0.4, ls=(0, (4, 1.5))), 100: dict(lw=0.6),
         150: dict(lw=0.4, ls=(0, (1, 1))), 200: dict(lw=0.5, ls=(0, (6, 1.5, 1, 1.5)))}
for nE, R, z, d in SCHNITTE:
    zz = min(max(z, 0.3), 199.7)
    polys = [np.asarray(p) for p in vase_v.slice(zz).to_polygons()]
    aussen = max(polys, key=lambda p: np.ptp(p[:, 0]))
    polygone([aussen], dx0, dy0, **stile[z])
mittellinie([dx0 - 36, dy0], [dx0 + 36, dy0]); mittellinie([dx0, dy0 - 36], [dx0, dy0 + 36])
for i, (nE, R, z, d) in enumerate(SCHNITTE):
    yy = dy0 - 42 - i * 4.2
    st = stile[z]
    ax.plot([dx0 - 38, dx0 - 28], [yy, yy], color="black", lw=st["lw"], ls=st.get("ls", "-"))
    ax.text(dx0 - 26, yy, f"z={z:g}: {NAMEN[nE]} R{R:g}, {d:g}° twist", fontsize=FS - 1, va="center")

# Hinweise
for i, s in enumerate([
    "Notes:",
    "1. Outer contour: smooth loft (cubic spline) through the cross-sections at z = 0/50/100/150/200; R = circumradius.",
    f"2. Polygon corners rounded R{ECKRADIUS:g}; wall {WAND:g}, bottom {BODEN:g}; open top.",
    f"3. Lettering “{TEXT}” (Brush Script, {TEXTHOEHE:g} mm), raised {RELIEF:g} mm, inclined {TEXT_NEIGUNG:g}°,",
    f"    centred on one pentagon face at z = {TEXT_Z:g}.",
    f"4. Volume ≈ {volumen / 1000:.1f} cm³ (solid copper ≈ {volumen / 1000 * 8.96:.0f} g, PETG ≈ {volumen / 1000 * 1.27:.0f} g)."]):
    ax.text(14, 42 - i * 5, s, fontsize=FS,
            fontweight="bold" if i == 0 else None)

fig.savefig(PDF)
print("gespeichert:", PDF)
