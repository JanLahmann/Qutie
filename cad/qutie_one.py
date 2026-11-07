#!/usr/bin/env python3
"""Qutie System One - parametric model (build123d).

Rebuild of `originals/Qutie System One v06.stl` (Tinkercad, design RasQberry
mini v06): a C-shaped frame (base, back wall, roof) with the cryostat
hanging from the roof.

Parts and print colours:
  body       matte black   base with "RasQberry" engraved in the underside
                           and the IBM eye-bee-M rebus on top, back wall with
                           a framed side step, block and band under the roof,
                           roof plate, rib holding the cryostat
  cryostat   silk silver   cylinder hanging from the block under the roof

Everything except the text and the rebus (one_outlines.json, see
extract_outlines.py) comes from PARAMS. Coordinates as in Tinkercad: the
back wall is at -y, the open side faces +y. All dimensions in mm.

Usage:  python qutie_one.py [--outdir DIR]
"""
import argparse
import json
from pathlib import Path

from build123d import Cylinder, Plane, Pos, extrude

from qutie_cad import box, engrave_bottom, export, face, report

HERE = Path(__file__).resolve().parent
OUTLINES = HERE / "one_outlines.json"
NAME = "Qutie System One"

PARAMS = dict(
    width=136.1, depth=95.0,            # base and roof, centred on x = 0, y = 0
    base_h=20.0, text_depth=3.0, logo_h=0.7,
    roof_z=(103.113, 112.113),
    # back wall: outer slab over the full width, inner block 7 mm in from
    # each side (the step that frames the sides)
    back_outer_y=(-47.5, -36.228), back_inner_y=(-36.228, -10.502), side_inset=7.0,
    # under the roof: a block, and a narrower band up to the roof
    block_y=(-36.228, 36.981), block_z=(88.713, 100.713),
    band_y=(-10.502, 30.861), band_inset=5.95,
    # cryostat
    cryo_centre=(0.0, 13.568), cryo_r=16.49, cryo_z=(40.213, 88.713),
    rib_w=1.0, rib_z=(40.397, 88.713),
)

COLOURS = {          # part: (filament, (r, g, b, alpha) for the 3MF preview)
    "body": ("matte black", (0.08, 0.08, 0.09, 1.0)),
    "cryostat": ("silk silver", (0.74, 0.76, 0.80, 1.0)),
}


def body(p, o):
    hw = p["width"] / 2
    hd = p["depth"] / 2
    roof_z0 = p["roof_z"][0]
    iw = hw - p["side_inset"]
    b = box((-hw, hw), (-hd, hd), (0, p["base_h"]))
    b = engrave_bottom(b, o["text"], p["text_depth"])
    top = Plane.XY.offset(p["base_h"] - 0.01)
    for poly in o["logo"]:
        b += extrude(top * face(poly), p["logo_h"] + 0.01, dir=(0, 0, 1))
    b += box((-hw, hw), p["back_outer_y"], (p["base_h"] - 0.01, roof_z0 + 0.01))
    b += box((-iw, iw), p["back_inner_y"], (p["base_h"] - 0.01, roof_z0 + 0.01))
    b += box((-iw, iw), p["block_y"], p["block_z"])
    bw = iw - p["band_inset"]
    b += box((-bw, bw), p["band_y"], (p["block_z"][1] - 0.01, roof_z0 + 0.01))
    b += box((-hw, hw), (-hd, hd), p["roof_z"])
    # rib from the back wall to the cryostat (into it by 1 mm)
    cx, cy = p["cryo_centre"]
    r = p["rib_w"] / 2
    b += box((cx - r, cx + r), (p["back_inner_y"][1] - 0.01, cy - p["cryo_r"] + 1.0),
             (p["rib_z"][0], p["rib_z"][1] + 0.01))
    return b.clean()


def cryostat(p):
    z0, z1 = p["cryo_z"]
    return Pos(*p["cryo_centre"], (z0 + z1) / 2) * Cylinder(p["cryo_r"], z1 - z0)


def build(p=PARAMS):
    o = json.loads(OUTLINES.read_text())
    cryo = cryostat(p)
    return {"body": (body(p, o) - cryo).clean(), "cryostat": cryo}


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
