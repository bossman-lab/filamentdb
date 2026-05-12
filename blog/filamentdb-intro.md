---
title: "I Built a Database That Saves You From Googling 'PLA Temperature' Ever Again"
description: "FilamentDB is an open-source CLI tool with 25+ pre-built filament profiles — search, compare, and get exact print settings for any brand."
published: false
tags: 3dprinting, python, opensource, showdev
---

Every time I switch filament brands, the same ritual: Google "Bambu Lab PLA Basic temperature", scroll through Reddit threads, find a comment from 2023, try 220°C, get stringing, try 230°C, get blobbing, end up at 225°C after burning half a spool.

This is insane. Every filament has an optimal temperature range. The manufacturer prints it on the box. But somehow we're all still guessing.

So I built **FilamentDB** — an open-source database of real filament parameters that you query from your terminal.

## What It Does

```bash
# Search for a filament
filamentdb search "PLA+"

# Get exact recommended settings  
filamentdb recommend --brand "Bambu Lab" --model "PLA Basic"

# Compare two filaments side by side
filamentdb compare "Bambu Lab PLA Basic" "eSun PLA+"

# Find alternatives when your go-to is out of stock
filamentdb alternatives PETG --exclude eSun
```

## The Data

The database currently covers **7 brands, 25+ models**, with full parameter sets for each:

| Brand | Models | Coverage |
|-------|--------|----------|
| Bambu Lab | PLA Basic, PLA Matte, PETG, ABS, TPU, PAHT-CF | Full |
| eSun | PLA+, PLA Matte, PETG, TPU | Full |
| Polymaker | PolyLite PLA, PolySonic PLA, PolyMax PC, PETG, ABS | Full |
| Sunlu | PLA Meta, PLA Plus, PETG, PLA Marble | Full |
| Overture | PLA Professional, PETG | Full |
| Prusament | PLA Galaxy Black, PETG Galaxy Black | Full |
| Creality | CR-Silk, Hyper PLA, ABS | Full |

Each entry includes:

```
Nozzle temperature (min/max/recommended)
Bed temperature (min/max/recommended)
Max volumetric speed
Retraction distance & speed
Fan speed
Bed adhesion method
Drying temperature & time
Enclosure requirement
Community rating
Notes
```

## Why FilamentDB Exists

Three observations drove this:

1. **Filament parameters are public knowledge** — manufacturers print them on the box and post them online. But they're scattered across PDFs, product pages, and forum posts.
2. **The same material type from different brands prints differently** — eSun PLA+ at 215°C and Bambu PLA Basic at 225°C are both "PLA" but need very different settings. A generic profile wastes time and filament.
3. **The 3D printing community already crowdsources this** — every Reddit thread, every Printables review, every Discord message is a data point. I just centralized it.

## The CLI

The tool is designed for speed. No waiting for a web page to load, no CAPTCHAs, no 15-second page transitions:

```bash
# Query and get an answer in under 100ms
$ filamentdb recommend --brand Polymaker --model "PolyMax PC"

🔥 Nozzle temperature:  275°C  (range: 260-290°C)
🔥 Bed temperature:     100°C  (range: 90-110°C)
⚡ Max volumetric:      8 mm³/s
🌬️ Fan speed:           0%
🏠 Enclosure:           REQUIRED
💧 Drying:              80°C for 12h
```

Compare mode is where it gets interesting:

```bash
$ filamentdb compare "Bambu Lab PLA Basic" "eSun PLA+"

                      A                B
Brand           Bambu Lab           eSun
Model           PLA Basic           PLA+
Type                 PLA            PLA
Nozzle °C           225°C          215°C
Bed °C               60°C           60°C
Retract            0.8mm          1.0mm
Rating              4.6 ★          4.5 ★
```

A 10°C nozzle difference — same material type. If you sliced for eSun and loaded Bambu, you'd be 10°C off. That's the difference between a perfect print and a failure.

## What's Next

The database is a v0.1 with curated entries. The real value comes from:

- **Community contributions** — a `filamentdb submit` command that lets anyone add their settings
- **Integration with SupportSage** — use the filament profile to tune support generation parameters
- **Web UI** — searchable online version for non-CLI users
- **Slicer plugins** — Cura/OrcaSlicer/Bambu Studio import your filament profile in one click

## Try It

```bash
git clone https://github.com/bossman-lab/filamentdb
cd filamentdb && pip install -e .

# Or just browse the data — it's a single JSON file
cat data/filaments.json
```

Repo: [github.com/bossman-lab/filamentdb](https://github.com/bossman-lab/filamentdb)

---

*Built because I was tired of guessing temperatures. Contributions welcome — open a PR with your filament data.*
