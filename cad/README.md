# Qutie models as code (build123d)

The two Qutie models, rebuilt as code from the Tinkercad designs, so they
can be changed by editing numbers, and printed in colour.

| Script | Rebuilds | Parts and colours |
|---|---|---|
| `qutie_one.py` | `originals/Qutie System One v06.stl` | body: matte black · cryostat: silk silver |
| `qutie_two.py` | `originals/Qutie System Two v02.stl` | floor: stone · wall: matte black · RTE: silk silver · lid: transparent · cryostat: silk gold |

Each script writes to `../print/`:

- `<model>.3mf` — one body per colour, each named after its filament.
  PrusaSlicer, Bambu Studio and OrcaSlicer import it as several objects
  (or one object with several parts); assign a filament to each.
- `parts/<model> - <part>.stl` — the same parts as separate STLs.
- `<model>.stl` — all parts fused, for a single-colour print (the shape of
  the original in `originals/`).
- `<model>.step` — for editing in Fusion, FreeCAD, Onshape (not committed;
  run the script to get it).

All parts of a model share one coordinate frame, so they line up when
loaded together. Parts touch but do not overlap.

## How the models are built

Almost everything is boxes, hexagons and a cylinder, typed in as numbers
in `PARAMS` at the top of each script (sizes, heights, positions; mm).
The free-form outlines are measured from the STLs by `extract_outlines.py`
and stored in `one_outlines.json` / `two_outlines.json`:

- "RasQberry" engraved in the underside of both models,
- the IBM eye-bee-M rebus (on the base of One, on the back of the wall of Two),
- for Two, the chandelier: the RasQberry chandelier's two outlines, taken
  from the RasQberry-Two parametric model (`3D Model/cad/cryostat/`)
  and scaled to 5 x 4.25 x 16 mm.

`qutie_cad.py` holds the shared helpers (prisms, engraving, export).

## Differences to the Tinkercad designs

The rebuilds match the originals within 0.06 mm, except where
hand-placed parts were centred:

- One: the rib holding the cryostat is centred behind it (was 2.7 mm off).
- Two: the chandelier and its wedge are centred in the cryostat cavity
  (were 0.7 mm off); the door slot is centred (0.1 mm); the right RTE wing
  touches the core (Tinkercad left a 0.03 mm gap).

## Running

```bash
pip install build123d trimesh shapely numpy
python3 qutie_one.py
python3 qutie_two.py
# only to re-measure the outlines:
python3 extract_outlines.py one "../originals/Qutie System One v06.stl"
python3 extract_outlines.py two "../originals/Qutie System Two v02.stl" <RasQberry-Two>/3D\ Model/cad/cryostat/cryo_profiles.json
```
