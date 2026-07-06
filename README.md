# Qutie 🧸

**Cute, palm-sized models of quantum computers — 3D-printable in one piece.**

Qutie is the smallest member of the [Fun with Quantum](https://fun-with-quantum.org) family:
a mini version of [RasQberry](https://rasqberry.org) that prints in a single piece on any home
3D printer. No electronics, no assembly — just something to hold, give away, and start
conversations with.

🌐 **Website: [qutie.org](https://qutie.org)**

## Get one

1. **Download** an STL file from [`/stl`](./stl) (or from [qutie.org](https://qutie.org), with an interactive 3D preview).
2. **Slice** it with your favorite slicer. PLA works great. Suggested starting points:
   0.2 mm layers, ~15 % infill, no supports — Qutie is designed to print as one piece.
3. **Print.** A few hours later you're holding a quantum computer. Sort of.

## Repository layout

| Path | What it is |
|---|---|
| [`stl/`](./stl) | The 3D-printable models (STL). **Drop new `.stl` files here** — the website picks them up automatically. |
| [`images/`](./images) | Photos of printed Quties. **Drop new pictures here** — the website gallery picks them up automatically. |
| [`site/`](./site) | The [qutie.org](https://qutie.org) website (Astro). Deployed to GitHub Pages on every push to `main`. |

Adding a model or photo is a one-step job: commit the file into `stl/` or `images/` and push.
The deploy workflow copies them into the site, lists every model with a 3D viewer and download
button, and adds every picture to the gallery. Filenames become captions
(`Qutie-System-Two.stl` → “Qutie System Two”), so name files accordingly.

## The family

| Project | What it is |
|---|---|
| [Fun with Quantum](https://fun-with-quantum.org) | The family portal — quantum games, builds, and learning |
| [RasQberry Two](https://rasqberry.org) | 3D-printed model of IBM Quantum System Two with a Raspberry Pi inside |
| [RasQberry One](https://rasqberry.one) | The original — functional model of IBM Q System One |
| [Quantego](https://quantego.org) | Quantum computers built from LEGO bricks |
| [Qoffee-Maker](https://qoffee-maker.org) | Order coffee with a quantum circuit |

## License

The repository is licensed under [Apache-2.0](./LICENSE). The 3D models in [`stl/`](./stl) and
the photos in [`images/`](./images) are additionally available under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — use whichever of the two
licenses suits you.

Qutie is an independent educational project and is not affiliated with, endorsed by, or
sponsored by IBM Corporation. IBM®, IBM Quantum®, Qiskit®, IBM Quantum System One and IBM
Quantum System Two are trademarks of International Business Machines Corporation. This project
creates educational models inspired by IBM's quantum computing systems for teaching purposes.

Built by [Jan-R. Lahmann](https://www.linkedin.com/in/JanLahmann) and the RasQberry community.

*GOD DOES PLAY DICE. COME PLAY, BUILD, LEARN.*
