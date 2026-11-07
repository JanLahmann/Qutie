"""Shared helpers for the Qutie models (build123d). All dimensions in mm."""
import zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

from build123d import Face, Plane, Polygon, Wire, export_step, export_stl, extrude

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
    bodies = [(f"{part} {i + 1}" if i else part, *colours[part], mesh(solid))
              for part, shape in parts.items() for i, solid in enumerate(shape.solids())]
    write_3mf(outdir / f"{name}.3mf", name, bodies)
    return whole


def mesh(shape):
    """(vertices, triangles) of a shape, with the vertices on shared edges
    merged so the mesh is closed."""
    verts, tris = shape.tessellate(TOL, ANG_TOL)
    index, out, remap = {}, [], []
    for v in verts:
        key = (round(v.X, 5), round(v.Y, 5), round(v.Z, 5))
        if key not in index:
            index[key] = len(out)
            out.append((v.X, v.Y, v.Z))
        remap.append(index[key])
    faces = [tuple(remap[i] for i in t) for t in tris]
    return out, [f for f in faces if len(set(f)) == 3]


def write_3mf(path, name, bodies):
    """3MF with ONE object made of the bodies [(label, filament, rgba, mesh)].

    Each body is a named part with its filament as material (name + display
    colour) and, for PrusaSlicer / Bambu Studio / OrcaSlicer, its own
    extruder (Metadata/Slic3r_PE_model.config; filaments numbered in order of
    first use). Plain 3MF readers see one multi-colour mesh."""
    filaments = list(dict.fromkeys(b[1] for b in bodies))
    rgba = {b[1]: b[2] for b in bodies}

    def hexcol(c):
        return "#" + "".join(f"{round(v * 255):02X}" for v in c)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
           'xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">',
           '<metadata name="slic3rpe:Version3mf">1</metadata>',
           '<resources>', '<basematerials id="1">']
    out += [f'<base name={quoteattr(f)} displaycolor="{hexcol(rgba[f])}"/>' for f in filaments]
    out += ['</basematerials>', f'<object id="2" type="model" name={quoteattr(name)} pid="1" '
            'pindex="0"><mesh><vertices>']
    for *_, (verts, _) in bodies:
        out += [f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in verts]
    out.append('</vertices><triangles>')
    config = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>',
              '<object id="2" instances_count="1">',
              f'<metadata type="object" key="name" value={quoteattr(name)}/>']
    base = first = 0
    for label, filament, _, (verts, tris) in bodies:
        k = filaments.index(filament)
        out += [f'<triangle v1="{a + base}" v2="{b + base}" v3="{c + base}" pid="1" p1="{k}"/>'
                for a, b, c in tris]
        config += [f'<volume firstid="{first}" lastid="{first + len(tris) - 1}">',
                   f'<metadata type="volume" key="name" value={quoteattr(label + " - " + filament)}/>',
                   f'<metadata type="volume" key="extruder" value="{k + 1}"/>', '</volume>']
        base += len(verts)
        first += len(tris)
    config += ['</object>', '</config>']
    out += ['</triangles></mesh></object>', '</resources>',
            '<build><item objectid="2"/></build>', '</model>']
    types = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
             'package/2006/content-types"><Default Extension="rels" ContentType="application/'
             'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
             'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
             '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.'
            'openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/'
            '3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/'
            '2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", "\n".join(out))
        z.writestr("Metadata/Slic3r_PE_model.config", "\n".join(config))


def report(parts):
    for part, s in parts.items():
        bb = s.bounding_box()
        print(f"{part:9s} {len(s.solids())} solid(s), volume {s.volume:9.1f} mm3, "
              f"x {bb.min.X:.2f}..{bb.max.X:.2f} y {bb.min.Y:.2f}..{bb.max.Y:.2f} "
              f"z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
