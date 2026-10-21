# Prompt: Vase "Evolution"

Use Python to generate a printable 3D vase and save all files in the current folder.

## Shape

- Height 200 mm, smooth swept loft (cubic spline of the radius r(θ) over the height) through these cross-sections:

| Height | Cross-section | Circumradius | Twist |
|---|---|---|---|
| 0 mm | Triangle | 52 mm | 0° |
| 50 mm | Square | 58 mm | 25° |
| 100 mm | Pentagon | 60 mm | 50° |
| 150 mm | Hexagon | 50 mm | 75° |
| 200 mm | Circle | 38 mm | 90° |

- Polygon corners rounded R 6 mm
- Wall 2.5 mm, bottom 3 mm, open top
- One closed, manifold solid with the bottom at z = 0

## Lettering

- "Evolution" in Brush Script (`/System/Library/Fonts/Supplemental/Brush Script.ttf`), font size 17 mm
- Raised 1.2 mm, rotated to rise at 35°
- Wrapped around the outer wall, centred on one pentagon face at z = 100 mm (angle −112°)
- The lettering must lie entirely on that one face.

## Output

1. **`vase_kupfer_evolution.stl`**: binary STL in mm, for Cura
2. **`vase_kupfer_evolution.usdz`**: with brushed copper
   - `UsdPreviewSurface`, metallic 1
   - reddish colour, ≈ 0.88/0.42/0.26
   - texture of horizontal circumferential brush marks that vary colour and roughness
3. **`vase_evolution_drawing.pdf`**: technical drawing in English, A4 landscape, scale 1:2
   - front view of the lettering side, shaded, with the 200 height and the cross-section heights
   - section B–B with opening Ø76, wall 2.5, bottom 3
   - top view with the overlaid cross-sections and a legend
   - notes and title block: material copper brushed, scale 1:2, ISO 2768-m

Tools: `numpy`, `scipy`, `manifold3d` (loft, booleans, extruding the text and wrapping it with `warp_batch`), `matplotlib` (TextPath, PDF), `moderngl` (shaded view), `usd-core`.

Then open the USDZ file and the PDF in Preview.

## Expected result

- Volume ≈ 158 cm³ (PETG ≈ 200 g)
- Genus 0
- Bounding box about 111 × 112 × 200 mm

## Result

### Technical drawing

[![Technical drawing of the Evolution vase](vase_evolution_drawing.png)](vase_evolution_drawing.pdf)

PDF: [vase_evolution_drawing.pdf](vase_evolution_drawing.pdf) (English) · [vase_evolution_zeichnung.pdf](vase_evolution_zeichnung.pdf) (German)

### Video

[![Brushed copper vase rotating around three axes](vase_kupfer_evolution_drehung.gif)](vase_kupfer_evolution_drehung.mp4)

Full resolution (1920 × 1080, 20 s): [vase_kupfer_evolution_drehung.mp4](vase_kupfer_evolution_drehung.mp4)
