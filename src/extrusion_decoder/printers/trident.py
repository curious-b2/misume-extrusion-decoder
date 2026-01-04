"""Voron Trident printer type support.

Assumptions:
- X and Y dimensions of the build volume are the same.
- Z-height of the build volume is fixed at 250mm.

Frame Structure:
The Voron Trident frame is a cube structure with the following arrangement:

Vertical Extrusions:
- B Extrusions (4): Vertically oriented, span the entire height of the frame

Top Face (horizontal):
- A Extrusions (4): Horizontal, at top
All 4 top extrusions mount to the top of B extrusions via wrench-access bolts.

Bottom Face (horizontal):
- C Extrusion (1): Horizontal, at bottom rear
- A Extrusions (3): Horizontal, at bottom (front and sides)
All 4 bottom extrusions mount to the bottom of B extrusions via wrench-access bolts
threaded into the ends of A/C extrusions.

Print Bed rear linear rail support:
- H Extrusion (1): Vertically oriented, mounted to the center of the C Extrusion.

Gantry Linear Rail supports:
- A Extrusions (2): Mounted partway up on left/right sides via wrench-access bolts
These leave 330mm (dependent on Z build volume) of space between the top of the
bottom A extrusion and the bottom of the middle A extrusion.

Other Components:
- D Extrusion (1): Mounts via 3D printed part to the upper end of H extrusion
- E Extrusion (1): Part of the gantry that carries the 3D printer head. A linear rail is
  mounted to it for X-axis motion. E rides on linear rails attached to the midpoint A
  extrusions, allowing motion in the Y axis.
- F Extrusion (1): Supports the print bed (along with G)
- G Extrusion (1): Supports the print bed (along with F). Mounts to midpoint of F extrusion
  via wrench-access bolt. The print bed is constrained by 3D printed parts attached to
  linear rails on the front of H extrusion and the rear face (lower side) of the two
  front B extrusions.
"""

from typing import Any

from extrusion_decoder.printers.base import BuildVolume, ExtrusionSpec, PrinterType


class TridentPrinter(PrinterType):
    """Voron Trident printer type."""

    @property
    def name(self) -> str:
        return "trident"

    @property
    def display_name(self) -> str:
        return "Voron Trident"

    def get_supported_build_volumes(self) -> list[BuildVolume]:
        """Get supported build volumes for Voron Trident.

        Standard sizes: 250x250x250, 300x300x250, 350x350x250
        """
        return [
            BuildVolume(250, 250, 250, "250x250x250"),
            BuildVolume(300, 300, 250, "300x300x250"),
            BuildVolume(350, 350, 250, "350x350x250"),
            # TODO: Add support for custom build volumes
        ]

    def get_extrusion_specs(self, build_volume: BuildVolume) -> list[ExtrusionSpec]:
        """Get extrusion specifications for Voron Trident build volume.

        Args:
            build_volume: The build volume configuration

        Returns:
            List of ExtrusionSpec objects
        """
        # Mathematical relationships based on build volume dimensions (X x Y x Z)
        # Standard builds: 250x250x250, 300x300x250, 350x350x250
        # All dimensions in millimeters
        #
        # Size-dependent extrusions (vary with X/Y build size):
        # - A, C, F: length = build_size_x + 120mm (horizontal frame pieces)
        # - D: length = build_size_x - 10mm (gantry frame)
        # - E: length = build_size_x + 80mm (gantry X-axis)
        # - G: length = build_size_x - 18mm (bed support)
        # - H: length = build_size_x + 80mm (rear vertical, but 350mm BOM shows 330mm - may be fixed)
        #
        # Fixed-length extrusions (for standard 250mm Z height):
        # - B: 500mm (upright extrusions, fixed regardless of X/Y size)

        build_size_x = build_volume.x

        # A, C, F: Horizontal frame extrusions - length = build_size_x + 120mm
        a_length = build_size_x + 120
        c_length = build_size_x + 120  # C is same as A but with midpoint wrench hole
        f_length = build_size_x + 120  # F is same length as A

        # D: Gantry frame extrusion - length = build_size_x - 10mm
        d_length = build_size_x - 10

        # E: Gantry X-axis extrusion - length = build_size_x + 80mm
        e_length = build_size_x + 80

        # G: Bed support extrusion - length = build_size_x - 18mm
        g_length = build_size_x - 18

        # B: Upright extrusions - FIXED for standard 250mm Z height
        # Always 500mm regardless of X/Y build size
        b_length = 500

        # H: Vertical center extrusion (rear)
        # FIXED at 330mm for standard 250mm Z height, regardless of X/Y build size
        # User confirmed: "H extrusion stays the same size (because all of the 'common' variants
        # only change the X/Y build volume dimensions, not the Z build volume dimension)"
        # Both 250mm and 350mm BOMs show 330mm-LTP for H
        h_length = 330

        specs = [
            ExtrusionSpec(
                "A",
                a_length,
                9,
                alterations=["TPW"],
                description="Horizontal frame extrusions (3 bottom, 4 top, 2 middle sides)",
            ),
            ExtrusionSpec(
                "B",
                b_length,
                4,
                alterations=["LCP", "RCP", "AV360"],
                description="Vertical upright extrusions (span full height, 4 corners)",
            ),
            ExtrusionSpec(
                "C",
                c_length,
                1,
                alterations=[f"AV{c_length // 2}", "TPW"],
                description="Bottom rear horizontal extrusion (identical to A but with wrench-access hole at midpoint, tapped holes at ends)",
            ),
            ExtrusionSpec(
                "D",
                d_length,
                1,
                alterations=[],
                description="Rear Brace of print-head gantry support",
            ),
            ExtrusionSpec(
                "E",
                e_length,
                1,
                alterations=[],
                description="Gantry X-axis extrusion (used in X axis assembly, carries print head)",
            ),
            ExtrusionSpec(
                "F",
                f_length,
                1,
                alterations=["AH235", "TPW"],
                description="Print bed support extrusion (G mounts to its midpoint)",
            ),
            ExtrusionSpec(
                "G",
                g_length,
                1,
                alterations=["AH235"],
                description="Print bed support extrusion (mounts to F midpoint; bed constrained by rails on H front and front B extrusions)",
            ),
            ExtrusionSpec(
                "H",
                h_length,
                1,
                alterations=[],
                description="Vertical center extrusion (mounts to C center, D mounts to top)",
            ),
        ]

        return specs

    def get_extrusion_letter(
        self,
        decoded: dict[str, Any],
        quantity: int = 1,
        build_volume: BuildVolume | None = None,
    ) -> str | None:
        """Determine the letter designation for an extrusion.

        This is the same logic as the original get_extrusion_letter from voron.py,
        but now part of the printer type system.
        """
        if "error" in decoded:
            return None

        length_raw = decoded.get("length_raw", "")
        alterations = decoded.get("alterations", [])

        try:
            length = int(length_raw)
        except (ValueError, TypeError):
            return None

        # Determine build size from build_volume or detect from length
        build_size = None
        if build_volume:
            if build_volume.x == 250:
                build_size = "250mm"
            elif build_volume.x == 300:
                build_size = "300mm"
            elif build_volume.x == 350:
                build_size = "350mm"

        # B Extrusions: 4 uprights/vertical pieces, FIXED LENGTH for standard 250mm Z height
        # Always 500mm regardless of X/Y build size
        if (
            length == 500
            and "LCP" in alterations
            and "RCP" in alterations
            and "AV360" in alterations
        ):
            return "B"

        # C Extrusion: Bottom rear horizontal, SIZE-DEPENDENT (X/Y dimensions)
        # CAD shows: HFSB5-2020-370-AH185-TPW-C Extrusion
        # Identical to A extrusion but with wrench hole at midpoint (AH185 for 250mm = 185mm from end)
        # CAD uses AH (horizontal) not AV (vertical) for the wrench hole
        # Formula: length = build_size_x + 120mm (same as A)
        # 250mm: 370mm, 300mm: 420mm, 350mm: 470mm
        if "TPW" in alterations and quantity == 1:
            # Check for AV or AH codes that indicate midpoint wrench hole
            position_codes = [
                alt
                for alt in alterations
                if alt.startswith("AV") or alt.startswith("AH")
            ]
            if position_codes:
                # Extract the position value
                for pos_code in position_codes:
                    try:
                        position = int(
                            pos_code[2:]
                        )  # Extract number after "AV" or "AH"
                        expected_c = (
                            250
                            if build_size == "250mm"
                            else 300
                            if build_size == "300mm"
                            else 350
                            if build_size == "350mm"
                            else None
                        )
                        if expected_c and length == expected_c + 120:
                            midpoint = length // 2
                            # Allow some tolerance (within 5mm of midpoint)
                            if abs(position - midpoint) <= 5:
                                return "C"
                    except (ValueError, IndexError):
                        continue

        # F Extrusion: Print bed support, SIZE-DEPENDENT (X/Y dimensions)
        # CAD shows: HFSB5-2020-370-AH185-F Extrusion (NO TPW!)
        # Has AH185 (or AH235) but NO TPW - check BEFORE A and G
        # Formula: length = build_size_x + 120mm (same as A)
        # 250mm: 370mm, 300mm: 420mm, 350mm: 470mm
        if "TPW" not in alterations and quantity == 1:
            expected_f = (
                250
                if build_size == "250mm"
                else 300
                if build_size == "300mm"
                else 350
                if build_size == "350mm"
                else None
            )
            if expected_f and length == expected_f + 120:
                if "AH185" in alterations or "AH235" in alterations:
                    return "F"

        # A Extrusions: Horizontal frame extrusions, SIZE-DEPENDENT (X/Y dimensions)
        # The 9 pieces with TPW (and no AH235/AV235/AH185) are the A extrusions
        # Formula: length = build_size_x + 120mm
        # 250mm: 370mm, 300mm: 420mm, 350mm: 470mm
        if (
            "TPW" in alterations
            and "AH235" not in alterations
            and "AV235" not in alterations
            and "AH185" not in alterations
        ):
            expected_a = (
                250
                if build_size == "250mm"
                else 300
                if build_size == "300mm"
                else 350
                if build_size == "350mm"
                else None
            )
            if expected_a and length == expected_a + 120:
                return "A"

        # D Extrusion: Gantry frame extrusion, SIZE-DEPENDENT (X/Y dimensions)
        # CAD gantry shows: HFSB5-2020-240-D Extrusion (used in gantry frame)
        # No alterations, just plain extrusion
        # Formula: length = build_size_x - 10mm
        # 250mm: 240mm, 300mm: 290mm, 350mm: 340mm
        if not alterations and quantity == 1:
            expected_d = (
                250
                if build_size == "250mm"
                else 300
                if build_size == "300mm"
                else 350
                if build_size == "350mm"
                else None
            )
            if expected_d and length == expected_d - 10:
                return "D"

        # E Extrusion: Gantry X-axis extrusion, SIZE-DEPENDENT (X/Y dimensions)
        # CAD gantry X Axis shows: HFSB5-20-330 (likely HFSB5-2020-330)
        # No alterations, just plain extrusion (used in X axis for gantry)
        # Formula: length = build_size_x + 80mm
        # 250mm: 330mm, 300mm: 380mm, 350mm: 430mm
        if not alterations and quantity == 1:
            expected_e = (
                250
                if build_size == "250mm"
                else 300
                if build_size == "300mm"
                else 350
                if build_size == "350mm"
                else None
            )
            if expected_e and length == expected_e + 80:
                return "E"

        # G Extrusion: Print bed support, SIZE-DEPENDENT (X/Y dimensions)
        # CAD shows: HFSB5-2020-232-LTP-G Extrusion
        # Has LTP (left end tapping), shorter length for bed support
        # Formula: length = build_size_x - 18mm
        # 250mm: 232mm, 300mm: 282mm, 350mm: 332mm
        # Note: Must check G BEFORE H to avoid misidentification
        if "LTP" in alterations and quantity == 1:
            expected_g = (
                250
                if build_size == "250mm"
                else 300
                if build_size == "300mm"
                else 350
                if build_size == "350mm"
                else None
            )
            if expected_g and length == expected_g - 18:
                return "G"

        # H Extrusion: Vertical center extrusion (rear), FIXED for standard 250mm Z height
        # Has LTP (left end tapping), rear vertical piece
        # CAD shows: HFSB5-2020-330-LTP-H Extrusion for 250mm build
        # FIXED at 330mm regardless of X/Y build size (for standard 250mm Z height)
        # User confirmed: "H extrusion stays the same size (because all of the 'common' variants
        # only change the X/Y build volume dimensions, not the Z build volume dimension)"
        # Both 250mm and 350mm BOMs show 330mm-LTP for H
        # Check H AFTER G to avoid misidentification
        if "LTP" in alterations and quantity == 1:
            if length == 330:
                return "H"

        return None
