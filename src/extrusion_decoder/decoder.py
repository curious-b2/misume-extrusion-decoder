"""Core decoder logic for MISUMI extrusion part numbers."""

import csv
import re

# Alteration code mappings from MISUMI documentation
ALTERATION_CODES: dict[str, str] = {
    # End Tapping
    "LTP": "Left End Tapping (Center Hole)",
    "RTP": "Right End Tapping (Center Hole)",
    "TPM": "End Tapping (Center Hole)",
    "TPW": "End Tapping (Center Hole, Both Sides, Heli-Coil Insert)",
    "LHP": "Left End Tapping (Center Hole)",
    "RHP": "Right End Tapping (Center Hole)",
    "HPW": "End Tapping (Center Hole, Heli-Coil Insert)",
    "LSP": "Left End Tapping (4 Side Holes)",
    "RSP": "Right End Tapping (4 Side Holes)",
    "SPW": "End Tapping (4 Side Holes)",
    # Sitting Method Change
    "SC": "High Precision Cut (L=0.2 tolerance)",
    "L_T45": "Left 45-Degree Cut",
    "R_T45": "Right 45-Degree Cut",
    # Drill Wrench Hole - Fastening Location Wrench Access Hole Alterations
    # 1 Slot (Single Line)
    "LCH": "Left Wrench Access Hole (1 Slot, Horizontal)",
    "LCV": "Left Wrench Access Hole (1 Slot, Vertical)",
    "LCP": "Left Wrench Access Hole (1 Slot, Crisscross)",
    "RCH": "Right Wrench Access Hole (1 Slot, Horizontal)",
    "RCV": "Right Wrench Access Hole (1 Slot, Vertical)",
    "RCP": "Right Wrench Access Hole (1 Slot, Crisscross)",
    # 2 Slots (Two Lines)
    "LWH": "Left Wrench Access Hole (2 Slots, Horizontal)",
    "LWV": "Left Wrench Access Hole (2 Slots, Vertical)",
    "LWP": "Left Wrench Access Hole (2 Slots, Crisscross)",
    "RWH": "Right Wrench Access Hole (2 Slots, Horizontal)",
    "RWV": "Right Wrench Access Hole (2 Slots, Vertical)",
    "RWP": "Right Wrench Access Hole (2 Slots, Crisscross)",
    # 3 Slots (Three Lines)
    "LEH": "Left Wrench Access Hole (3 Slots, Horizontal)",
    "LEV": "Left Wrench Access Hole (3 Slots, Vertical)",
    "LEP": "Left Wrench Access Hole (3 Slots, Crisscross)",
    "REH": "Right Wrench Access Hole (3 Slots, Horizontal)",
    "REV": "Right Wrench Access Hole (3 Slots, Vertical)",
    "REP": "Right Wrench Access Hole (3 Slots, Crisscross)",
    # Other Wrench Hole Alterations
    "RWIP": "Right Wrench Hole in Fixed Position",
    # Wrench Hole Diameter Specifications (for Series 6)
    "X5": "Wrench Hole Diameter Specification (5mm)",
    "X8": "Wrench Hole Diameter Specification (8mm)",
    "FL": "Extrusion End Caps Hole Position Change (Left, for 3mm cap)",
    "FR": "Extrusion End Caps Hole Position Change (Right, for 3mm cap)",
    # Wrench Hole in Specified Position - Multiple positions (up to 5 locations)
    "AH": "Wrench Hole in Specified Position (Horizontal, A position)",
    "BH": "Wrench Hole in Specified Position (Horizontal, B position)",
    "CH": "Wrench Hole in Specified Position (Horizontal, C position)",
    "DH": "Wrench Hole in Specified Position (Horizontal, D position)",
    "EH": "Wrench Hole in Specified Position (Horizontal, E position)",
    "AV": "Wrench Hole in Specified Position (Vertical, A position)",
    "BV": "Wrench Hole in Specified Position (Vertical, B position)",
    "CV": "Wrench Hole in Specified Position (Vertical, C position)",
    "DV": "Wrench Hole in Specified Position (Vertical, D position)",
    "EV": "Wrench Hole in Specified Position (Vertical, E position)",
    "AP": "Wrench Hole in Specified Position (Crisscross, A position)",
    "BP": "Wrench Hole in Specified Position (Crisscross, B position)",
    "CP": "Wrench Hole in Specified Position (Crisscross, C position)",
    "DP": "Wrench Hole in Specified Position (Crisscross, D position)",
    "EP": "Wrench Hole in Specified Position (Crisscross, E position)",
    # Counterboring
    "Z5": "Counterbore in Specified Position (Z5, d=5.5mm)",
    "Z6": "Counterbore in Specified Position (Z6, d=6.5mm)",
    "Z8": "Counterbore in Specified Position (Z8, d=9mm)",
    "Z12": "Counterbore in Specified Position (Z12, d=13mm)",
    # Counterbore positions (Top to Bottom - Vertical)
    "XA": "Counterbore (Top to Bottom, Vertical, A position)",
    "XB": "Counterbore (Top to Bottom, Vertical, B position)",
    "XC": "Counterbore (Top to Bottom, Vertical, C position)",
    "XD": "Counterbore (Top to Bottom, Vertical, D position)",
    "XE": "Counterbore (Top to Bottom, Vertical, E position)",
    # Counterbore positions (Right to Left - Horizontal)
    "YA": "Counterbore (Right to Left, Horizontal, A position)",
    "YB": "Counterbore (Right to Left, Horizontal, B position)",
    "YC": "Counterbore (Right to Left, Horizontal, C position)",
    "YD": "Counterbore (Right to Left, Horizontal, D position)",
    "YE": "Counterbore (Right to Left, Horizontal, E position)",
    # Blind Joints Dedicated Holes
    # D Type Hole Alterations
    "LDH": "Left D Hole (Horizontal on Left End, Pre-Assembly Insertion Double Joint)",
    "LDV": "Left D Hole (Vertical on Left End, Pre-Assembly Insertion Double Joint)",
    "RDH": "Right D Hole (Horizontal on Right End, Pre-Assembly Insertion Double Joint)",
    "RDV": "Right D Hole (Vertical on Right End, Pre-Assembly Insertion Double Joint)",
    # S Type Hole Alterations
    "LSH": "Left S Hole (Horizontal on Left End, Post-Assembly Insertion Double Joint, Center Joint)",
    "LSV": "Left S Hole (Vertical on Left End, Post-Assembly Insertion Double Joint, Center Joint)",
    "RSH": "Right S Hole (Horizontal on Right End, Post-Assembly Insertion Double Joint, Center Joint)",
    "RSV": "Right S Hole (Vertical on Right End, Post-Assembly Insertion Double Joint, Center Joint)",
    # M Type Hole Alterations
    "LMH": "Left M Hole (Post-Assembly Insertion Double Joint, Post Connection)",
    "RMH": "Right M Hole (Horizontal on Right End, Post-Assembly Insertion Double Joint, Post Connection)",
    # L Type Hole Alterations
    "JLP": "L Hole (Crisscross on Top, Parallel Joint)",
    "KLP": "L Hole (Crisscross on Bottom, Parallel Joint)",
    # Special Extrusions End Plates Alterations
    "LTS": "Left End Tapping (GFS/HFSR Series)",
    "RTS": "Right End Tapping (GFS/HFSR Series)",
    "TSW": "End Tapping (GFS/HFSR Series)",
    # Chamfering
    "CW": "End Face C Chamfering",
    # Labeling
    "ZZZ": "Labeling (Serial Number)",
    "LL": "Labeling (Unit Number)",
}


def parse_size(size_str: str) -> str:
    """Parse size string (e.g., '2020' -> '20mm × 20mm').

    Handles various formats:
    - 2020 -> 20mm × 20mm
    - 3030 -> 30mm × 30mm
    - 404020 -> 40mm × 40mm × 20mm (if applicable)
    """
    if len(size_str) == 4:
        # Square cross-section: 2020 = 20mm × 20mm
        dim = size_str[:2]
        return f"{dim}mm × {dim}mm"
    elif len(size_str) == 6:
        # Rectangular: 404020 = 40mm × 40mm × 20mm
        dim1 = size_str[:2]
        dim2 = size_str[2:4]
        dim3 = size_str[4:6]
        return f"{dim1}mm × {dim2}mm × {dim3}mm"
    else:
        return f"{size_str} (custom size)"


def parse_length(length_str: str) -> str:
    """Parse length string (e.g., '500' -> '500mm')."""
    try:
        length = int(length_str)
        return f"{length}mm"
    except ValueError:
        return length_str


def parse_alteration_code(code: str) -> tuple[str, str | None]:
    """Parse an alteration code, handling numeric suffixes.

    Returns:
        Tuple of (description, numeric_value). numeric_value is None if not applicable.
    """
    # Check for exact match first (important for codes like Z6, Z8, etc.)
    if code in ALTERATION_CODES:
        return ALTERATION_CODES[code], None

    # Check for codes with underscores (e.g., L_T45)
    if "_" in code:
        if code in ALTERATION_CODES:
            return ALTERATION_CODES[code], None

    # Check for codes with numeric suffixes (e.g., AV360, XA200)
    # This should come after exact match check to avoid splitting codes like Z6
    match = re.match(r"^([A-Z]+)(\d+)$", code)
    if match:
        base_code = match.group(1)
        numeric_value = match.group(2)

        if base_code in ALTERATION_CODES:
            description = ALTERATION_CODES[base_code]
            # Add numeric value context for position-based codes
            if base_code in [
                "AV",
                "BV",
                "CV",
                "DV",
                "EV",
                "AH",
                "BH",
                "CH",
                "DH",
                "EH",
                "AP",
                "BP",
                "CP",
                "DP",
                "EP",
                "XA",
                "XB",
                "XC",
                "XD",
                "XE",
                "YA",
                "YB",
                "YC",
                "YD",
                "YE",
            ]:
                return description, f"{numeric_value}mm from left end"
            elif base_code in ["JLP", "KLP"]:
                # L Hole codes have format like JLP1100-H2 (hole pitch and number of holes)
                return description, f"Hole pitch: {numeric_value}mm"
            elif base_code == "ZZZ":
                return description, f"Serial: {numeric_value}"
            elif base_code == "LL":
                return description, f"Unit: {numeric_value}"
            else:
                return description, numeric_value
        else:
            return f"Unknown alteration code: {base_code}", numeric_value

    return f"Unknown alteration code: {code}", None


def decode_misumi_name(part_number: str) -> dict[str, any]:
    """Decode a MISUMI extrusion part number into its components.

    Format: SERIES-SIZE-LENGTH-ALTERATIONS...

    Example: HFSB5-2020-500-LCP-RCP-AV360

    Args:
        part_number: The MISUMI part number to decode

    Returns:
        Dictionary with decoded information including:
        - part_number: Original part number
        - series: Extrusion series
        - size: Parsed size string
        - size_raw: Raw size code
        - length: Parsed length string
        - length_raw: Raw length code
        - alterations: List of alteration codes
        - alteration_descriptions: List of human-readable alteration descriptions
        - error: Error message if decoding failed
    """
    parts = part_number.split("-")

    if len(parts) < 3:
        return {
            "error": f"Invalid part number format. Expected at least 3 parts separated by hyphens, got: {part_number}"
        }

    series = parts[0]
    size = parts[1]
    length = parts[2]
    alterations = parts[3:] if len(parts) > 3 else []

    # Decode alterations
    alteration_descriptions = []
    for alt_code in alterations:
        desc, value = parse_alteration_code(alt_code)
        if value:
            alteration_descriptions.append(f"{desc} ({value})")
        else:
            alteration_descriptions.append(desc)

    return {
        "part_number": part_number,
        "series": series,
        "size": parse_size(size),
        "size_raw": size,
        "length": parse_length(length),
        "length_raw": length,
        "alterations": alterations,
        "alteration_descriptions": alteration_descriptions,
    }


def format_description(decoded: dict[str, any]) -> str:
    """Format decoded information into a human-readable description.

    Args:
        decoded: Dictionary returned from decode_misumi_name()

    Returns:
        Formatted string description
    """
    if "error" in decoded:
        return f"Error: {decoded['error']}"

    lines = [
        f"MISUMI Extrusion: {decoded['part_number']}",
        f"  Series: {decoded['series']}",
        f"  Size: {decoded['size']}",
        f"  Length: {decoded['length']}",
    ]

    if decoded["alterations"]:
        lines.append("  Alterations:")
        for desc in decoded["alteration_descriptions"]:
            lines.append(f"    • {desc}")
    else:
        lines.append("  Alterations: None")

    return "\n".join(lines)


def extract_misumi_from_bom(csv_path: str) -> list[dict[str, any]]:
    """Extract MISUMI part numbers from a BOM CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of dictionaries with 'part_number', 'quantity', and 'description' keys.
        Returns list with error dict if file cannot be read.
    """
    misumi_parts = []

    try:
        with open(csv_path, encoding="utf-8") as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            delimiter = ";" if ";" in sample else ","

            reader = csv.DictReader(f, delimiter=delimiter)

            for row in reader:
                description = row.get("Description", "").strip()
                quantity = row.get("Qty", "").strip()

                # Check if description contains "Misumi" (case-insensitive)
                if "misumi" in description.lower():
                    # Extract part number - typically "Misumi PART-NUMBER"
                    # Pattern: "Misumi" followed by space and then the part number
                    match = re.search(
                        r"misumi\s+([A-Z0-9][A-Z0-9\-]+)", description, re.IGNORECASE
                    )
                    if match:
                        part_number = match.group(1)
                        misumi_parts.append(
                            {
                                "part_number": part_number,
                                "quantity": quantity if quantity else "1",
                                "description": description,
                            }
                        )

    except FileNotFoundError:
        return [{"error": f"File not found: {csv_path}"}]
    except Exception as e:
        return [{"error": f"Error reading CSV: {str(e)}"}]

    return misumi_parts


def format_bom_output(parts: list[dict[str, any]]) -> str:
    """Format extracted MISUMI parts from BOM into a readable output.

    This is a general-purpose formatter. For Voron Trident-specific formatting
    with letter designations (A-H), use format_voron_bom_output from the voron module.

    Args:
        parts: List of part dictionaries from extract_misumi_from_bom()

    Returns:
        Formatted string output
    """
    if not parts:
        return "No MISUMI parts found in BOM."

    if "error" in parts[0]:
        return f"Error: {parts[0]['error']}"

    lines = []
    lines.append("=" * 70)
    lines.append("MISUMI Parts from BOM")
    lines.append("=" * 70)
    lines.append("")

    for i, part in enumerate(parts, 1):
        decoded = decode_misumi_name(part["part_number"])
        qty = part["quantity"]

        lines.append(f"[{i}] Qty: {qty}")
        lines.append(f"     Part Number: {part['part_number']}")

        if "error" not in decoded:
            lines.append(f"     Series: {decoded['series']}")
            lines.append(f"     Size: {decoded['size']}")
            lines.append(f"     Length: {decoded['length']}")

            if decoded["alterations"]:
                lines.append("     Alterations:")
                for desc in decoded["alteration_descriptions"]:
                    lines.append(f"       • {desc}")
            else:
                lines.append("     Alterations: None")
        else:
            lines.append(f"     Error: {decoded['error']}")

        lines.append("")

    return "\n".join(lines)
