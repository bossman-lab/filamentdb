# FilamentDB 🧵📊

**Open-source 3D printing filament parameter database.**

Stop guessing print settings. Stop wasting filament on bad temperatures. Stop digging through Reddit threads for that one PLA profile that worked.

FilamentDB is a searchable database of **real filament parameters** — brand, model, material type, nozzle temp, bed temp, retraction, drying, and community ratings.

## Quick Start

```bash
pip install tabulate  # required for table output
cd filamentdb && pip install -e .

# Search for a filament
filamentdb search "PLA+"

# Get exact recommended settings
filamentdb recommend --brand "Bambu Lab" --model "PLA Basic"

# Compare two filaments
filamentdb compare "Bambu Lab PLA Basic" "eSun PLA+"

# Find alternatives
filamentdb alternatives PETG --exclude "eSun"

# List everything
filamentdb list brands
filamentdb list types
```

## Data

The database currently includes **7 brands, 25+ models**, covering:
- PLA, PLA+, PLA Matte, PLA Silk, PLA Marble
- PETG (translucent, basic)
- ABS
- TPU 95A
- PAHT-CF (Carbon fiber nylon)
- Polycarbonate

All with exact print parameters (nozzle temp range, bed temp, volumetric speed, retraction, drying, bed adhesion, enclosure requirements).

## Output

```bash
$ filamentdb recommend --brand "Polymaker" --model "PolyMax PC"

=======================================================
  Recommended Settings: Polymaker PolyMax PC
  Source: exact_match
=======================================================

  🔥 Nozzle temperature:  275°C  (range: 260-290°C)
  🔥 Bed temperature:     100°C  (range: 90-110°C)
  ⚡ Max volumetric:      8 mm³/s
  ↩  Retraction:          1.5mm @ 40mm/s
  🌬️ Fan speed:           0%
  🛏️ Bed adhesion:        PEI + Magigoo PC
  💧 Drying:              80°C for 12h
  🏠 Enclosure:           REQUIRED

  💡 Polycarbonate, exceptional strength and heat resistance
```

## Roadmap

- [x] Built-in database (7 brands, 25+ models)
- [x] Search by brand/type/model
- [x] Per-filament recommended settings
- [x] Side-by-side comparison
- [ ] Community contributions (submit your settings)
- [ ] Web UI (searchable online)
- [ ] Integration with SupportSage CLI
- [ ] API for slicing software plugins

## License

MIT
