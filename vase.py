# Druckbare Vase: geschwungener Loft Dreieck -> Viereck -> Fünfeck -> Sechseck -> Kreis.
# Ausgabe: STL (für Cura) und USDZ mit Material (blaues Glas oder gebürstetes Kupfer) für Vorschau.
import struct, numpy as np
from scipy.interpolate import CubicSpline
from manifold3d import Manifold, Mesh, CrossSection, JoinType

# Querschnitte: (Eckenzahl, Umkreisradius mm, Höhe mm, Verdrehung Grad); 0 Ecken = Kreis
SCHNITTE = [(3, 52, 0, 0), (4, 58, 50, 25), (5, 60, 100, 50), (6, 50, 150, 75), (0, 38, 200, 90)]
ECKRADIUS = 6.0      # Rundung der Polygonecken (druckbar, keine Spitzen)
WAND, BODEN = 2.5, 3.0
NA, NZ = 360, 240    # Auflösung: Winkel, Höhenschritte
# Erhabener Schriftzug auf der Außenwand
TEXT, SCHRIFT = "Evolution", "/System/Library/Fonts/Supplemental/Brush Script.ttf"
TEXTHOEHE, RELIEF = 17.0, 1.2      # Schriftgröße mm, Erhebung über der Wand mm
TEXT_NEIGUNG = 35.0                # Schrift ansteigend gedreht (Grad), damit sie ganz auf einer Fünfeckseite liegt
TEXT_Z, TEXT_WINKEL = 100.0, -112.0  # Mitte des Schriftzugs: Höhe mm, Winkel Grad (Mitte einer Fünfeckseite)
MATERIAL = "kupfer"   # "glas" oder "kupfer"
NAME = {"glas": "/Users/haraldbeker/Allerlei/vase_glas_evolution",
        "kupfer": "/Users/haraldbeker/Allerlei/vase_kupfer_evolution"}[MATERIAL]

theta = np.linspace(0, 2 * np.pi, NA, endpoint=False)

def radial(n, R, dreh):
    """Radius r(theta) eines regelmäßigen n-Ecks mit gerundeten Ecken, um 'dreh' Grad verdreht."""
    if n == 0:
        return np.full(NA, float(R))
    w = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    poly = CrossSection([np.c_[R * np.cos(w), R * np.sin(w)].tolist()])
    poly = poly.offset(-ECKRADIUS, JoinType.Miter).offset(ECKRADIUS, JoinType.Round, 2.0, 256)
    p = np.array(poly.to_polygons()[0])
    q = np.roll(p, -1, 0)                                       # gerade Kanten fein unterteilen
    p = np.vstack([p + (q - p) * s for s in np.linspace(0, 1, 50, endpoint=False)])
    a, r =np.arctan2(p[:, 1], p[:, 0]), np.hypot(p[:, 0], p[:, 1])
    o = np.argsort(a)
    return np.interp(theta - np.radians(dreh), a[o], r[o], period=2 * np.pi)

# Radius pro Winkel als glatte Spline über die Höhe -> geschwungener Übergang
zk = np.array([s[2] for s in SCHNITTE], float)
rk = np.array([radial(n, R, d) for n, R, _, d in SCHNITTE])
z = np.linspace(zk[0], zk[-1], NZ)
spline = CubicSpline(zk, rk, axis=0, bc_type="natural")
r = spline(z)                                                   # NZ x NA
P = np.stack([r * np.cos(theta), r * np.sin(theta), np.repeat(z[:, None], NA, 1)], -1)

def koerper(ringe):
    """Geschlossener Körper aus übereinanderliegenden Ringen (je NA Punkte) mit Deckel unten/oben."""
    m = len(ringe)
    v = np.vstack([ringe.reshape(-1, 3), ringe[0].mean(0), ringe[-1].mean(0)])
    i = np.arange(NA); j = (i + 1) % NA
    f = []
    for k in range(m - 1):
        a, b = k * NA + i, k * NA + j
        f += [np.c_[a, b, b + NA], np.c_[a, b + NA, a + NA]]
    unten, oben = m * NA, m * NA + 1
    f += [np.c_[np.full(NA, unten), j, i], np.c_[np.full(NA, oben), (m - 1) * NA + i, (m - 1) * NA + j]]
    return Manifold(Mesh(vert_properties=v.astype(np.float32), tri_verts=np.vstack(f).astype(np.uint32)))

aussen = koerper(P)

# Innenfläche: horizontal um WAND entlang der Flächennormale versetzt, ab Bodenstärke, oben offen
dt = np.roll(P, -1, 1) - np.roll(P, 1, 1)
dz = np.gradient(P, axis=0)
nrm = np.cross(dt, dz)
nxy = nrm[..., :2] / np.linalg.norm(nrm, axis=-1, keepdims=True)
laenge = np.maximum(np.linalg.norm(nxy, axis=-1, keepdims=True), 0.5)
Q = P.copy()
Q[..., :2] -= WAND * nxy / laenge ** 2
Q = Q[z >= BODEN]
Q[0, :, 2] = BODEN
Q = np.concatenate([Q, Q[-1:] + [0, 0, 5]])                     # über den Rand hinaus -> Öffnung
vase = aussen - koerper(Q)

def schriftzug():
    """Text als Fläche (mm), extrudiert und um die Außenwand gewickelt."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from manifold3d import FillRule
    from scipy.interpolate import RegularGridInterpolator
    tp = TextPath((0, 0), TEXT, size=TEXTHOEHE, prop=FontProperties(fname=SCHRIFT))
    kont = [np.asarray(k) for k in tp.to_polygons(closed_only=True) if len(k) > 2]
    cs = CrossSection([k.tolist() for k in kont], FillRule.NonZero)
    (x0, y0), (x1, y1) = np.array(cs.bounds()).reshape(2, 2)
    cs = cs.translate([-(x0 + x1) / 2, -(y0 + y1) / 2]).rotate(TEXT_NEIGUNG)
    t = Manifold.extrude(cs, RELIEF + 1.0).translate([0, 0, -1.0]).refine_to_length(0.8)
    # Radius der Außenwand r(theta, z) als Tabelle für schnelle Interpolation
    zt = np.linspace(TEXT_Z - 45, TEXT_Z + 45, 600)
    tab = spline(zt)
    tab = np.hstack([tab, tab[:, :1]])
    rint = RegularGridInterpolator((zt, np.append(theta, 2 * np.pi)), tab)
    r_mitte = float(rint([[TEXT_Z, np.radians(TEXT_WINKEL) % (2 * np.pi)]])[0])
    def wickeln(p):
        p = np.array(p, dtype=float)
        zz = TEXT_Z + p[:, 1]
        th = (np.radians(TEXT_WINKEL) + p[:, 0] / r_mitte) % (2 * np.pi)   # x nach links->rechts von außen gelesen
        rr = rint(np.c_[zz, th]) + p[:, 2]
        return np.c_[rr * np.cos(th), rr * np.sin(th), zz]
    return t.warp_batch(wickeln)

vase = vase + schriftzug()
if vase.volume() < 0 or vase.is_empty():
    raise SystemExit("Fehler: ungültiger Körper")

m = vase.to_mesh()
v, f = np.array(m.vert_properties)[:, :3], np.array(m.tri_verts)
a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
fn = np.cross(b - a, c - a)
with open(NAME + ".stl", "wb") as o:
    o.write(b"vase glas blau".ljust(80, b" ") + struct.pack("<I", len(f)))
    rec = np.zeros(len(f), dtype=[("d", "<f4", 12), ("attr", "<u2")])
    rec["d"] = np.hstack([fn / np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12), a, b, c])
    o.write(rec.tobytes())

# USDZ mit Material für die Ansicht in Vorschau
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdUtils
import os
stage = Usd.Stage.CreateNew(NAME + ".usdc")
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z); UsdGeom.SetStageMetersPerUnit(stage, 0.001)
root = UsdGeom.Xform.Define(stage, "/Vase"); stage.SetDefaultPrim(root.GetPrim())
mesh = UsdGeom.Mesh.Define(stage, "/Vase/Mesh")
mesh.CreatePointsAttr([Gf.Vec3f(*p) for p in v.tolist()])
mesh.CreateFaceVertexCountsAttr([3] * len(f)); mesh.CreateFaceVertexIndicesAttr(f.flatten().tolist())
mesh.CreateSubdivisionSchemeAttr("none")
vn = np.zeros_like(v)
for k in range(3): np.add.at(vn, f[:, k], fn)
vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
mesh.CreateNormalsAttr([Gf.Vec3f(*p) for p in vn.tolist()]); mesh.SetNormalsInterpolation("vertex")
mat = UsdShade.Material.Define(stage, "/Vase/Material")
sh = UsdShade.Shader.Define(stage, "/Vase/Material/Surface"); sh.CreateIdAttr("UsdPreviewSurface")
textur = None
if MATERIAL == "glas":
    sh.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.05, 0.30, 0.85))
    sh.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.45)
    sh.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.5)
    sh.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.05)
    sh.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    sh.CreateInput("specularColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(1, 1, 1))
else:
    # Gebürstetes Kupfer: umlaufende Schleifriefen als Textur, die nur über die Höhe variiert (v = z / Höhe)
    from PIL import Image
    rng = np.random.default_rng(7)
    hz = 4096
    riefen = sum(w * np.interp(np.arange(hz), np.linspace(0, hz, hz // k + 1), rng.random(hz // k + 1))
                 for w, k in ((0.35, 64), (0.35, 12), (0.3, 3)))
    riefen = (riefen - riefen.min()) / np.ptp(riefen)
    kupfer = np.array([0.88, 0.42, 0.26])
    farbe = np.clip(kupfer[None, :] * (0.7 + 0.5 * riefen[:, None]), 0, 1)
    rau = 0.30 + 0.25 * (1 - riefen)
    bild = np.dstack([np.repeat(farbe[:, None, :], 8, 1), np.repeat(rau[:, None, None], 8, 1)])
    textur = NAME + "_textur.png"
    Image.fromarray((bild[::-1] * 255).astype(np.uint8), "RGBA").save(textur)
    st = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    st.Set([Gf.Vec2f(0.5, float(zz) / zk[-1]) for zz in v[:, 2]])
    leser = UsdShade.Shader.Define(stage, "/Vase/Material/st"); leser.CreateIdAttr("UsdPrimvarReader_float2")
    leser.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
    tex = UsdShade.Shader.Define(stage, "/Vase/Material/Textur"); tex.CreateIdAttr("UsdUVTexture")
    tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("./" + os.path.basename(textur))
    tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(leser.ConnectableAPI(), "result")
    tex.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")
    sh.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI().CreateOutput("rgb", Sdf.ValueTypeNames.Float3))
    sh.CreateInput("roughness", Sdf.ValueTypeNames.Float).ConnectToSource(tex.ConnectableAPI().CreateOutput("a", Sdf.ValueTypeNames.Float))
    sh.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(1.0)
mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), "surface")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
stage.GetRootLayer().Save()
UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(NAME + ".usdc"), NAME + ".usdz")
os.remove(NAME + ".usdc")
if textur: os.remove(textur)

print("Dreiecke:", len(f), "Volumen cm3:", round(vase.volume() / 1000, 1), "Genus:", vase.genus(),
      "Bbox:", np.round(v.min(0), 1), np.round(v.max(0), 1))
