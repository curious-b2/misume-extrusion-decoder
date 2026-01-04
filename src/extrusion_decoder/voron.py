"""Voron Trident specific functionality for MISUMI extrusions.

This module provides Voron Trident-specific letter designation mapping
for extrusions. The core MISUMI decoder functionality is in the decoder module.

Note: This module is maintained for backward compatibility. New code should
use the printer system (extrusion_decoder.printers) instead.
"""

from extrusion_decoder.decoder import decode_misumi_name
from extrusion_decoder.printers import get_printer


def get_extrusion_letter(
    decoded: dict[str, any], quantity: int = 1, build_size: str | None = None
) -> str | None:
    """Determine the letter designation for an extrusion based on length, alterations, and quantity.

    This mapping is based on the Voron Trident assembly manual where extrusions
    are labeled A through H. The mapping uses length, alteration patterns, and
    quantity to identify which letter each extrusion corresponds to.

    Note: Build sizes (250mm, 300mm, 350mm) refer to X/Y build volume dimensions.
    All standard builds share a 250mm Z height. A, C, D, E, F, and G extrusions are
    size-dependent (lengths change with X/Y build size). B and H extrusions are fixed
    length for the standard 250mm Z height, but would change if the build height
    is customized.

    Args:
        decoded: Dictionary returned from decode_misumi_name()
        quantity: Quantity of this extrusion in the BOM
        build_size: Build size string ("250mm", "300mm", or "350mm") to help
                    distinguish C from H extrusions

    Returns:
        Letter designation (A-H) or None if unknown
    """
    if "error" in decoded:
        return None

    length_raw = decoded.get("length_raw", "")
    alterations = decoded.get("alterations", [])

    try:
        length = int(length_raw)
    except (ValueError, TypeError):
        return None

    # B Extrusions: 4 uprights/vertical pieces, FIXED LENGTH for standard 250mm Z height
    # Always 500mm for standard builds (X/Y sizes: 250mm, 300mm, or 350mm)
    # Note: Would change if build height (Z dimension) is customized
    if (
        length == 500
        and "LCP" in alterations
        and "RCP" in alterations
        and "AV360" in alterations
    ):
        return "B"

    # A Extrusion: Lower back extrusion, SIZE-DEPENDENT (X/Y dimensions)
    # 250mm X/Y: 240mm, 300mm X/Y: 290mm, 350mm X/Y: 340mm
    # Used throughout the manual to mark the lower back of the printer
    if length == 340 and quantity == 1:
        return "A"  # 350mm build size
    if length == 290 and quantity == 1:
        return "A"  # 300mm build size
    if length == 240 and quantity == 1:
        return "A"  # 250mm build size

    # E Extrusions: SIZE-DEPENDENT (X/Y dimensions), with LTP (left end tapping)
    # 250mm X/Y: 330mm, 300mm X/Y: 380mm, 350mm X/Y: 430mm
    # Manual explicitly mentions "330mm E extrusion" for 250 X/Y size
    if length in (330, 332) and "LTP" in alterations:
        return "E"  # 250mm build size (330mm) or slight variant (332mm)
    if length in (380, 382) and "LTP" in alterations:
        return "E"  # 300mm build size
    if length in (430, 432) and "LTP" in alterations:
        return "E"  # 350mm build size

    # D Extrusion: Rear brace, SIZE-DEPENDENT (X/Y dimensions)
    # 250mm X/Y: 380mm, 300mm X/Y: 430mm, 350mm X/Y: 480mm
    if length == 430 and quantity == 1:
        return "D"  # 300mm build size
    if length == 380 and quantity == 1:
        return "D"  # 250mm build size
    if length == 480 and quantity == 1:
        return "D"  # 350mm build size

    # C Extrusions: Horizontal frame pieces, SIZE-DEPENDENT (X/Y dimensions)
    # 250mm X/Y: 420mm, 300mm X/Y: 470mm, 350mm X/Y: 520mm
    # H Extrusions: Horizontal frame pieces, FIXED LENGTH for standard 250mm Z height
    # Always 470mm for standard builds (X/Y sizes: 250mm, 300mm, or 350mm)
    # Note: Would change if build height (Z dimension) is customized
    # They use the same part number but are used in different positions
    if length == 470 and "TPW" in alterations and "AH235" not in alterations:
        # Could be C (300mm build) or H (any build size, fixed at 470mm)
        if build_size == "300mm":
            return "C"  # 300mm build: C is 470mm
        elif build_size in ("250mm", "350mm"):
            return "H"  # H is always 470mm regardless of build size
        else:
            # Can't determine without build size
            return "C/H"
    if length == 420 and "TPW" in alterations and "AH235" not in alterations:
        return "C"  # 250mm build size
    if length == 520 and "TPW" in alterations and "AH235" not in alterations:
        return "C"  # 350mm build size

    # F Extrusion: SIZE-DEPENDENT (X/Y dimensions), with AH235-TPW (quantity 1)
    # 250mm X/Y: 420mm, 300mm X/Y: 470mm, 350mm X/Y: 520mm
    if (
        length == 470
        and "AH235" in alterations
        and "TPW" in alterations
        and quantity == 1
    ):
        return "F"  # 300mm build size
    if (
        length == 420
        and "AH235" in alterations
        and "TPW" in alterations
        and quantity == 1
    ):
        return "F"  # 250mm build size
    if (
        length == 520
        and "AH235" in alterations
        and "TPW" in alterations
        and quantity == 1
    ):
        return "F"  # 350mm build size

    # G Extrusion: SIZE-DEPENDENT (X/Y dimensions), with AH235 only (quantity 1)
    # 250mm X/Y: 420mm, 300mm X/Y: 470mm, 350mm X/Y: 520mm
    if (
        length == 470
        and "AH235" in alterations
        and "TPW" not in alterations
        and quantity == 1
    ):
        return "G"  # 300mm build size
    if (
        length == 420
        and "AH235" in alterations
        and "TPW" not in alterations
        and quantity == 1
    ):
        return "G"  # 250mm build size
    if (
        length == 520
        and "AH235" in alterations
        and "TPW" not in alterations
        and quantity == 1
    ):
        return "G"  # 350mm build size

    return None


def detect_build_size(parts: list[dict[str, any]]) -> str | None:
    """Detect Voron Trident build size from extrusion lengths in BOM.

    Note: This function is maintained for backward compatibility.
    Consider using the printer system instead.
    """
    """Detect Voron Trident build size from extrusion lengths in BOM.

    Args:
        parts: List of part dictionaries from extract_misumi_from_bom()

    Returns:
        Build size string ("250mm", "300mm", or "350mm") or None if undetectable
    """
    for part in parts:
        decoded = decode_misumi_name(part["part_number"])
        if "error" not in decoded:
            length_raw = decoded.get("length_raw", "")
            try:
                length = int(length_raw)
                # A extrusion lengths: 240 (250mm), 290 (300mm), 340 (350mm)
                if length == 340:
                    return "350mm"
                elif length == 290:
                    return "300mm"
                elif length == 240:
                    return "250mm"
            except (ValueError, TypeError):
                continue
    return None


def format_voron_bom_output(parts: list[dict[str, any]]) -> str:
    """Format extracted MISUMI parts from BOM with Voron Trident letter designations.

    This is a Voron-specific formatter that adds letter designations (A-H) to
    the output. For general-purpose BOM formatting, use format_bom_output from
    the decoder module.

    Note: This function is maintained for backward compatibility.
    Consider using the printer system instead.

    Args:
        parts: List of part dictionaries from extract_misumi_from_bom()

    Returns:
        Formatted string output with Voron letter designations
    """

    if not parts:
        return "No MISUMI parts found in BOM."

    if "error" in parts[0]:
        return f"Error: {parts[0]['error']}"

    # Detect build size from extrusions
    build_size = detect_build_size(parts)

    # Check if all extrusions share the same series and/or size
    all_series = set()
    all_sizes = set()
    for part in parts:
        decoded = decode_misumi_name(part["part_number"])
        if "error" not in decoded:
            all_series.add(decoded.get("series", ""))
            all_sizes.add(decoded.get("size", ""))

    common_series = list(all_series)[0] if len(all_series) == 1 else None
    common_size = list(all_sizes)[0] if len(all_sizes) == 1 else None

    lines = []
    lines.append("=" * 70)
    lines.append("MISUMI Frame Rails from BOM")
    if build_size:
        lines.append(f"Build Size: {build_size} Trident")
    lines.append("=" * 70)
    lines.append("")

    # Show common series/size if all extrusions share them
    if common_series or common_size:
        common_info = []
        if common_series:
            common_info.append(f"Series: {common_series}")
        if common_size:
            common_info.append(f"Size: {common_size}")
        lines.append("Common to all extrusions: " + " | ".join(common_info))
        lines.append("")

    if build_size:
        lines.append(
            "Note: Build sizes (250/300/350mm) refer to X/Y build volume dimensions. "
            "All standard builds share a 250mm Z height.\n"
            "A, C, D, E, F, and G extrusions are size-dependent (X/Y dimensions). "
            "B and H extrusions are fixed for standard 250mm Z height, but would "
            "change if build height is customized."
        )
        lines.append("")

    # Sort parts by letter designation (A, B, C, D, E, F, G, H, then unknown)
    def get_sort_key(part: dict[str, any]) -> tuple[int, str]:
        """Get sort key for a part: (priority, letter or part_number)."""
        decoded = decode_misumi_name(part["part_number"])
        qty = part.get("quantity", "1")
        try:
            quantity = int(qty)
        except (ValueError, TypeError):
            quantity = 1

        # Get letter designation
        printer = get_printer("trident")
        if printer:
            from extrusion_decoder.printers.base import BuildVolume

            build_volume = None
            if build_size:
                if build_size == "250mm":
                    build_volume = BuildVolume(250, 250, 250)
                elif build_size == "300mm":
                    build_volume = BuildVolume(300, 300, 250)
                elif build_size == "350mm":
                    build_volume = BuildVolume(350, 350, 250)
            letter = printer.get_extrusion_letter(decoded, quantity, build_volume)
        else:
            letter = get_extrusion_letter(decoded, quantity, build_size)

        # Define sort order: A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, unknown=999
        letter_order = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        if letter and letter in letter_order:
            return (letter_order[letter], part["part_number"])
        else:
            # Unknown letters go at the end, sorted by part number
            return (999, part["part_number"])

    sorted_parts = sorted(parts, key=get_sort_key)

    for i, part in enumerate(sorted_parts, 1):
        decoded = decode_misumi_name(part["part_number"])
        qty = part["quantity"]

        try:
            quantity = int(qty)
        except (ValueError, TypeError):
            quantity = 1

        # Get letter designation using printer system
        printer = get_printer("trident")
        if printer:
            from extrusion_decoder.printers.base import BuildVolume

            # Convert build_size string to BuildVolume
            build_volume = None
            if build_size:
                if build_size == "250mm":
                    build_volume = BuildVolume(250, 250, 250)
                elif build_size == "300mm":
                    build_volume = BuildVolume(300, 300, 250)
                elif build_size == "350mm":
                    build_volume = BuildVolume(350, 350, 250)
            letter = printer.get_extrusion_letter(decoded, quantity, build_volume)
        else:
            # Fallback to old function
            letter = get_extrusion_letter(decoded, quantity, build_size)

        lines.append(f"[{i}] Qty: {qty}")
        if letter:
            if letter == "C/H":
                lines.append(
                    "     Designation: C/H Extrusion (horizontal frame pieces)"
                )
            else:
                lines.append(f"     Designation: {letter} Extrusion")
        lines.append(f"     Part Number: {part['part_number']}")

        if "error" not in decoded:
            # Only show series/size if they're not common to all
            if decoded.get("series") != common_series:
                lines.append(f"     Series: {decoded['series']}")
            if decoded.get("size") != common_size:
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
