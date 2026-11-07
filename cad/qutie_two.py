#!/usr/bin/env python3
"""Qutie System Two - parametric model (build123d).

Rebuild of `originals/Qutie System Two v02.stl` (Tinkercad, design RQB2-mini-v02):
a palm-sized RasQberry Two on a 50 x 60 mm floor plate.

Parts and print colours (one body per colour in the 3MF):
  floor       stone          plate, "RasQberry" engraved in the underside
  wall        matte black    box with the IBM eye-bee-M rebus on the back
  RTE         silk silver    three server wings around a hexagonal core,
                             hexagonal cryostat cavity, open door slot
  lid         transparent    the Y-shaped plate on top of the RTE
  cryostat    silk gold      chandelier (the RasQberry chandelier, scaled
                             down) on a small wedge from the back wall

Boxes and hexagons come from PARAMS below; the free-form outlines (text,
rebus, chandelier) from two_outlines.json (see extract_outlines.py).
Coordinates as in Tinkercad: floor x -25..25, y -55..5, z 0..3; the wall is
at the back (y 0), the door faces -y. All dimensions in mm.

Usage:  python qutie_two.py [--outdir DIR]
Writes  Qutie System Two.stl / .step   one piece, single colour
        Qutie System Two.3mf           five coloured bodies
        Qutie System Two - <part>.stl  one STL per colour
"""
import argparse
import json
import math
from pathlib import Path

from build123d import Plane, Polygon, extrude

from qutie_cad import engrave_bottom, export, face, prism, report

HERE = Path(__file__).resolve().parent
OUTLINES = HERE / "two_outlines.json"
NAME = "Qutie System Two"

PARAMS = dict(
    floor=dict(x=(-25.0, 25.0), y=(-55.0, 5.0), h=3.0, text_depth=1.0),
    wall=dict(x=(-20.0, 20.0), y=(-10.0, 0.0), z=(3.0, 28.0), logo_h=0.6),
    # RTE: a hexagonal core (corners on +/- x) with a server wing on every
    # second side (outward normals 90, 210, 330 deg); 22 mm tall, lid 3 mm
    core_centre=(0.0, -36.5), core_r=7.5,
    wing_w=7.6, wing_l=10.0, wing_sides=(90, 210, 330), overlap=0.025,
    rte_z=(3.0, 25.0), lid_z=(25.0, 28.0),
    # cryostat cavity: hexagon 10 x 10 (stretched in y), door slot to the front
    cavity_centre=(0.0, -37.0), cavity_size=(10.0, 10.0), door_w=8.0,
    # chandelier: the RasQberry chandelier scaled to this bounding box
    chandelier_size=(5.0, 4.25, 16.0), chandelier_z=9.0,
    # wedge under the chandelier, hanging from the cavity's back wall
    wedge_w=3.0, wedge_y=(-38.0, -32.0), wedge_z=(6.0, 9.0),
)

# full-size chandelier (RasQberry-Two cryostat_model.py CHANDELIER)
CHANDELIER = dict(
    centre=(10.088, 8.7365), hex_r=10.088, hole_r=1.988,
    stem=(0.0, 14.7), column=(14.7, 64.2),
    plates=[(14.7, 16.2), (31.029, 32.529), (46.2, 47.7), (62.7, 64.2)],
)

COLOURS = {          # part: (filament, (r, g, b, alpha) for the 3MF preview)
    "floor": ("stone", (0.78, 0.76, 0.72, 1.0)),
    "wall": ("matte black", (0.08, 0.08, 0.09, 1.0)),
    "RTE": ("silk silver", (0.74, 0.76, 0.80, 1.0)),
    "lid": ("transparent", (0.88, 0.93, 0.97, 0.35)),
    "cryostat": ("silk gold", (0.85, 0.66, 0.15, 1.0)),
}


def hexagon(c, rx, ry):
    """Hexagon with corners on +/- x; rx = corner radius, ry = half height."""
    cx, cy = c
    return [(cx + rx, cy), (cx + rx / 2, cy + ry), (cx - rx / 2, cy + ry),
            (cx - rx, cy), (cx - rx / 2, cy - ry), (cx + rx / 2, cy - ry)]


def y_outline_parts(p):
    """Core hexagon and the three wings (as point lists)."""
    cx, cy = p["core_centre"]
    r = p["core_r"]
    apothem = r * math.sqrt(3) / 2
    shapes = [hexagon(p["core_centre"], r, apothem)]
    for side in p["wing_sides"]:
        a = math.radians(side)
        n, t = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        d0, d1 = apothem - p["overlap"], apothem + p["wing_l"]
        hw = p["wing_w"] / 2
        shapes.append([(cx + n[0] * d + t[0] * s, cy + n[1] * d + t[1] * s)
                       for d, s in ((d0, -hw), (d1, -hw), (d1, hw), (d0, hw))])
    return shapes


def y_solid(p, z0, z1):
    parts = [prism(s, z0, z1) for s in y_outline_parts(p)]
    body = parts[0]
    for s in parts[1:]:
        body += s
    return body


def floor(p, o):
    f = p["floor"]
    (x0, x1), (y0, y1) = f["x"], f["y"]
    body = prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0, f["h"])
    return engrave_bottom(body, o["text"], f["text_depth"]).clean()


def wall(p, o):
    w = p["wall"]
    (x0, x1), (y0, y1), (z0, z1) = w["x"], w["y"], w["z"]
    body = prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)
    # rebus outlines are (x, z); a plane in the back face, normal +y
    back = Plane(origin=(0, y1 - 0.01, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    for poly in o["logo"]:
        # Plane with normal +y maps local y to world -z: flip z
        flipped = {"ext": [(x, -z) for x, z in poly["ext"]],
                   "holes": [[(x, -z) for x, z in h] for h in poly["holes"]]}
        body += extrude(face(flipped, back), w["logo_h"] + 0.01, dir=(0, 1, 0))
    return body.clean()


def rte(p):
    body = y_solid(p, *p["rte_z"])
    cx, cy = p["cavity_centre"]
    sx, sy = p["cavity_size"]
    z0, z1 = p["rte_z"]
    body -= prism(hexagon((cx, cy), sx / 2, sy / 2), z0 - 1, z1 + 1)
    hw = p["door_w"] / 2
    body -= prism([(cx - hw, cy), (cx + hw, cy), (cx + hw, cy - 30), (cx - hw, cy - 30)],
                   z0 - 1, z1 + 1)
    return body.clean()


def lid(p):
    return y_solid(p, *p["lid_z"]).clean()


def chandelier(p, o, c=CHANDELIER):
    """The RasQberry chandelier scaled (non-uniformly) into chandelier_size,
    upright, centred on the cavity centre."""
    full = o["chandelier"]["size"]
    sx, sy, sz = (m / f for m, f in zip(p["chandelier_size"], full))
    ccx, ccy = c["centre"]
    x0, y0 = p["cavity_centre"]
    zb = p["chandelier_z"]

    def xy(pts):
        return [(x0 + (x - ccx) * sx, y0 + (y - ccy) * sy) for x, y in pts]

    def z(v):
        return zb + v * sz

    ch = o["chandelier"]
    body = prism(xy(ch["stem"]), z(c["stem"][0]), z(c["stem"][1]))
    body += prism(xy(ch["column"]), z(c["column"][0]), z(c["column"][1]))
    plate = xy([(ccx + x, ccy + y) for x, y in hexagon((0, 0), c["hex_r"], c["hex_r"] * math.sqrt(3) / 2)])
    for a, b in c["plates"]:
        body += prism(plate, z(a), z(b))
    hole = xy([(ccx + c["hole_r"] * math.cos(t), ccy + c["hole_r"] * math.sin(t))
               for t in [2 * math.pi * i / 24 for i in range(24)]])
    body -= prism(hole, z(0) - 0.1, z(c["column"][1]) + 0.1)
    return body.clean()


def wedge(p):
    hw = p["wedge_w"] / 2
    (ya, yb), (z0, z1) = p["wedge_y"], p["wedge_z"]
    x0 = p["cavity_centre"][0]
    side = Plane(origin=(x0 - hw, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    tri = Polygon((yb + 0.01, z0), (yb + 0.01, z1), (ya, z1), align=None)
    return extrude(side * tri, p["wedge_w"], dir=(1, 0, 0))


def build(p=PARAMS):
    o = json.loads(OUTLINES.read_text())
    return {
        "floor": floor(p, o),
        "wall": wall(p, o),
        "RTE": rte(p),
        "lid": lid(p),
        "cryostat": (chandelier(p, o) + wedge(p)).clean(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outdir", default=str(HERE.parent / "print"))
    a = ap.parse_args()
    parts = build()
    report(parts)
    whole = export(NAME, parts, COLOURS, a.outdir)
    print(f"whole: volume {whole.volume:.1f} mm3 -> {a.outdir}")


if __name__ == "__main__":
    main()
