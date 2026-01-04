# MISUMI Extrusion Name Decoder

A Python application that decodes MISUMI aluminum extrusion part numbers into human-readable descriptions.

## Installation

```bash
uv sync
```

## Usage

### Decode a single part number:

```bash
uv run misumi-decoder <part_number>
```

### Extract and decode MISUMI parts from a BOM CSV:

```bash
uv run misumi-decoder --bom <csv_file>
```

### Examples

**Single part number:**
```bash
uv run misumi-decoder HFSB5-2020-500-LCP-RCP-AV360
```

**BOM extraction:**
```bash
uv run misumi-decoder --bom generated_bom.csv
```

Output:
```
MISUMI Extrusion: HFSB5-2020-500-LCP-RCP-AV360
  Series: HFSB5
  Size: 20mm × 20mm
  Length: 500mm
  Alterations:
    • Left Wrench Access Hole (1 Slot, Crisscross)
    • Right Wrench Access Hole (1 Slot, Crisscross)
    • Wrench Hole in Specified Position (Vertical, A position) (360mm from left end)
```

## Part Number Format

MISUMI extrusion part numbers follow this format:
```
SERIES-SIZE-LENGTH-ALTERATIONS...
```

Where:
- **SERIES**: The extrusion series code (e.g., HFSB5, HFS5)
- **SIZE**: Cross-sectional dimensions (e.g., 2020 = 20mm × 20mm)
- **LENGTH**: Length in millimeters (e.g., 500 = 500mm)
- **ALTERATIONS**: One or more alteration codes (e.g., LCP, RCP, AV360)

## Supported Alteration Codes

The decoder recognizes various alteration codes including:
- **End Tapping** (LTP, RTP, TPM, TPW, LHP, RHP, HPW, LSP, RSP, SPW, LTS, RTS, TSW)
- **High Precision Cut** (SC)
- **45-Degree Cut** (L_T45, R_T45)
- **Wrench Access Holes** - Fastening Location (from p2_0683.pdf):
  - 1 Slot: LCH, LCV, LCP, RCH, RCV, RCP
  - 2 Slots: LWH, LWV, LWP, RWH, RWV, RWP
  - 3 Slots: LEH, LEV, LEP, REH, REV, REP
- **Wrench Holes in Fixed Position** (RWIP)
- **Extrusion End Caps Hole Position Change** (FL, FR)
- **Wrench Holes in Specified Position** (from p2_0685.pdf):
  - Horizontal: AH, BH, CH, DH, EH
  - Vertical: AV, BV, CV, DV, EV
  - Crisscross: AP, BP, CP, DP, EP
- **Wrench Hole Diameter Specification** (X5, X8) (from p2_0685.pdf)
- **Counterboring** (from p2_0687.pdf):
  - General: Z5, Z6, Z8, Z12
  - Top to Bottom (Vertical): XA, XB, XC, XD, XE
  - Right to Left (Horizontal): YA, YB, YC, YD, YE
- **Blind Joints Dedicated Holes**:
  - D Hole (Pre-Assembly Insertion Double Joint) (from p2_0688.pdf): LDH, RDH, LDV, RDV
  - S Hole (Post-Assembly Insertion Double Joint, Center Joint) (from p2_0689.pdf): LSH, LSV, RSH, RSV
  - M Hole (Post-Assembly Insertion Double Joint, Post Connections) (from p2_0690.pdf): LMH, RMH
  - L Hole (Parallel Joint) (from p2_0691.pdf): JLP, KLP
- **Special Extrusions End Plates Alterations** (from p2_0692.pdf): GFS Series End Tapping (LTS, RTS, TSW), HFSR End Tapping (LTS, RTS, TSW)
- **Chamfering** (CW)
- **Labeling** (ZZZ, LL)

## BOM Extraction

The script can extract MISUMI frame rails from a Voron 3D printer BOM CSV file. It:
- Automatically detects CSV delimiter (semicolon or comma)
- Filters for rows containing "Misumi" in the Description column
- Extracts part numbers and quantities
- Decodes each part number with full details

The BOM CSV should have columns: `Category`, `Description`, `Qty`, `Notes` (or similar).

## API Usage

You can also use the decoder as a Python module:

```python
from extrusion_decoder import (
    decode_misumi_name,
    format_description,
    extract_misumi_from_bom,
    format_bom_output,
)

# Decode a single part
decoded = decode_misumi_name("HFSB5-2020-500-LCP-RCP-AV360")
print(format_description(decoded))

# Extract from BOM
parts = extract_misumi_from_bom("generated_bom.csv")
print(format_bom_output(parts))
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Reference

Based on MISUMI documentation:
- Overview of Aluminum Extrusion Alterations: [p679-680](https://us.misumi-ec.com/pdf/fa/2012/p2_0679.pdf)
- Tapping & Extrusion Cuts: [p681-682](https://us.misumi-ec.com/pdf/fa/2012/p2_0681.pdf)
- Fastening Location Wrench Access Hole Alterations: [p683-684](https://us.misumi-ec.com/pdf/fa/2012/p2_0683.pdf)
- Wrench Hole Alterations: [p685-686](https://us.misumi-ec.com/pdf/fa/2012/p2_0685.pdf)
- Counterboring & D-type Hole Alterations: [p687-488](https://us.misumi-ec.com/pdf/fa/2012/p2_0687.pdf)
- S type and M type Hole Alterations: [p688-689](https://us.misumi-ec.com/pdf/fa/2012/p2_0689.pdf)
- L type Hole Alterations, Other Alterations: [p691-692](https://us.misumi-ec.com/pdf/fa/2012/p2_0691.pdf)
