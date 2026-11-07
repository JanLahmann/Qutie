"""Shared helpers for the Qutie models (build123d). All dimensions in mm."""
import re
import zipfile
from pathlib import Path

from build123d import (Color, Face, Mesher, Plane, Polygon, Wire, export_step,
                       export_stl, extrude)

# Mesh export: linear tolerance (mm) and angular tolerance (rad)
TOL, ANG_TOL = 0.005, 0.2


def prism(pts, z0, z1):
    """Prism over z0..z1 from a 2D outline (any winding)."""
    face = Plane.XY.offset(z0) * Polygon(*pts, align=None)
    return extrude(face, z1 - z0, dir=(0, 0, 1))


def box(x, y, z):
    """Axis-aligned box from three (min, max) ranges."""
    (x0, x1), (y0, y1) = x, y
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], *z)


def face(poly, plane=Plane.XY):
    """Planar face from a measured polygon {"ext", "holes"} on `plane`."""
    def wire(pts):
        return Wire.make_polygon([plane.from_local_coords((x, y)) for x, y in pts], close=True)
    return Face(wire(poly["ext"]), [wire(h) for h in poly["holes"]])


def engrave_bottom(body, polys, depth):
    """Cut measured outlines `depth` deep into the underside (z = 0)."""
    for poly in polys:
        body -= extrude(Plane.XY.offset(-0.01) * face(poly), depth + 0.01, dir=(0, 0, 1))
    return body


def export(name, parts, colours, outdir):
    """parts: {part: shape}; colours: {part: (filament name, (r, g, b, a))}.
    Writes
        <name>.stl / .step            one piece (all parts fused), single colour
        <name>.3mf                    one coloured body per part
        parts/<name> - <part>.stl     one STL per part (for slicers that
                                      assign filaments per object)"""
    outdir = Path(outdir)
    (outdir / "parts").mkdir(parents=True, exist_ok=True)
    whole = None
    for part, shape in parts.items():
        whole = shape if whole is None else whole + shape
        export_stl(shape, str(outdir / "parts" / f"{name} - {part}.stl"), tolerance=TOL,
                   angular_tolerance=ANG_TOL)
    whole = whole.clean()
    export_stl(whole, str(outdir / f"{name}.stl"), tolerance=TOL, angular_tolerance=ANG_TOL)
    export_step(whole, str(outdir / f"{name}.step"))
    m = Mesher()
    for part, shape in parts.items():
        for i, solid in enumerate(shape.solids()):
            solid.color = Color(*colours[part][1])
            solid.label = part if i == 0 else f"{part} {i + 1}"
            m.add_shape(solid, linear_deflection=TOL, angular_deflection=ANG_TOL,
                        part_number=solid.label)
    path = outdir / f"{name}.3mf"
    m.write(str(path))
    _name_materials(path, [colours[p][0] for p, s in parts.items() for _ in s.solids()])
    return whole


def _name_materials(path, names):
    """Give the 3MF materials the filament names (build123d writes
    'Color: (r, g, b, a) near ...'); the slicer shows these names."""
    with zipfile.ZipFile(path) as z:
        files = {n: z.read(n) for n in z.namelist()}
    model = files["3D/3dmodel.model"].decode()
    it = iter(names)
    model = re.sub(r'(<base name=")Color: [^"]*(")', lambda m: m.group(1) + next(it) + m.group(2), model)
    files["3D/3dmodel.model"] = model.encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(n, data)


def report(parts):
    for part, s in parts.items():
        bb = s.bounding_box()
        print(f"{part:9s} {len(s.solids())} solid(s), volume {s.volume:9.1f} mm3, "
              f"x {bb.min.X:.2f}..{bb.max.X:.2f} y {bb.min.Y:.2f}..{bb.max.Y:.2f} "
              f"z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
