#!/usr/bin/env python3
"""Measure the free-form outlines of the Qutie models from their STLs.

Both models are mostly boxes (plus hexagons / a cylinder) and are built from
numbers in qutie_one.py / qutie_two.py. Only the outlines that cannot
sensibly be typed in are measured here and written to <model>_outlines.json:

System One (one_outlines.json)
  text   "RasQberry", engraved 3 mm into the underside of the base
         (cut at z = 1.5, mirrored as seen from above)
  logo   IBM eye-bee-M rebus on top of the base, raised 0.7 mm (cut at z = 20.35)

System Two (two_outlines.json)
  text   "RasQberry", engraved 1 mm into the underside of the floor (cut at z = 0.5)
  logo   the rebus on the back of the wall, raised 0.6 mm (cut at y = 0.3,
         stored as (x, z))
  chandelier  the two free-form outlines (stem, six-armed column) of the
         RasQberry chandelier at full size, copied from RasQberry-Two
         (`3D Model/parametric/cryostat/cryo_profiles.json`, branch
         3D-model-parametric); qutie_two.py scales it down

Usage:
    python3 extract_outlines.py one "../stl/Qutie System One v06.stl"
    python3 extract_outlines.py two "../stl/Qutie System Two v02.stl" <path to cryo_profiles.json>
"""
import json
import sys
from functools import reduce
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon, box


def outlines(mesh, origin, normal, axes, keep=None):
    """Cross-section as polygons with holes (nested rings: even-odd).
    keep(region) may post-process the shapely region."""
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    rings = [Polygon(np.asarray(r)[:, axes]).buffer(0) for r in sec.discrete if len(r) > 3]
    rings = [r for r in rings if r.area > 1e-4]
    region = reduce(lambda a, b: a.symmetric_difference(b), rings).buffer(0)
    if keep:
        region = keep(region)
    out = []
    for p in getattr(region, "geoms", [region]):
        if p.geom_type != "Polygon" or p.area < 1e-3:
            continue
        p = p.simplify(0.002)
        out.append({"ext": np.round(p.exterior.coords[:-1], 3).tolist(),
                    "holes": [np.round(h.coords[:-1], 3).tolist() for h in p.interiors]})
    return out


def letters(region):
    """A cut through a plate with engraved letters: the letters are the holes."""
    return box(*region.bounds).difference(region)


def one(stl):
    mesh = trimesh.load(stl)
    return {
        "source": stl.name,
        "text": outlines(mesh, [0, 0, 1.5], [0, 0, 1], [0, 1], keep=letters),
        # the cut also crosses the back wall (y < -10.5): keep the base top only
        "logo": outlines(mesh, [0, 0, 20.35], [0, 0, 1], [0, 1],
                         keep=lambda r: r.intersection(box(-100, -10.0, 100, 100))),
    }


def two(stl, cryo):
    mesh = trimesh.load(stl)
    c = json.loads(Path(cryo).read_text())
    ch = c["R2_ChandelierSingle"]
    snap = c["snap_mm"]
    return {
        "source": stl.name,
        "text": outlines(mesh, [0, 0, 0.5], [0, 0, 1], [0, 1], keep=letters),
        # the y = 0.3 cut also crosses the floor plate (z < 3): drop it
        "logo": outlines(mesh, [0, 0.3, 0], [0, 1, 0], [0, 2],
                         keep=lambda r: r.intersection(box(-100, 3.0, 100, 100))),
        "chandelier": {
            "source": "RasQberry-Two cryo_profiles.json (R2_ChandelierSingle)",
            "size": ch["size"],
            "stem": [[x * snap, y * snap] for x, y in ch["stem"]["pts"]],
            "column": [[x * snap, y * snap] for x, y in ch["column"]["pts"]],
        },
    }


def main():
    model, stl = sys.argv[1], Path(sys.argv[2])
    data = one(stl) if model == "one" else two(stl, sys.argv[3])
    out = Path(__file__).parent / f"{model}_outlines.json"
    out.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {out}: {len(data['text'])} text, {len(data['logo'])} logo polygons")


if __name__ == "__main__":
    main()
