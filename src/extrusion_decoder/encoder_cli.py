"""Command-line interface for the encoder (printer + build size -> part numbers)."""

import sys

from extrusion_decoder.makers import get_maker, list_makers
from extrusion_decoder.printers import get_printer, list_printers


def main() -> None:
    """Command-line interface for the encoder."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  voron-encoder <printer_type> <build_volume> [--maker <maker>]")
        print("\nExamples:")
        print("  voron-encoder trident 350x350x250")
        print("  voron-encoder trident 350x350x250 --maker misumi")
        print("\nAvailable printer types:")
        for printer_name in list_printers():
            printer = get_printer(printer_name)
            if printer:
                print(f"  - {printer_name}: {printer.display_name}")
        print("\nAvailable makers:")
        for maker_name in list_makers():
            maker = get_maker(maker_name)
            if maker:
                print(f"  - {maker_name}: {maker.display_name}")
        sys.exit(1)

    printer_name = sys.argv[1]

    if len(sys.argv) < 3:
        print("Error: Please provide a build volume (e.g., 350x350x250)")
        print(f"Usage: voron-encoder {printer_name} <build_volume> [--maker <maker>]")
        sys.exit(1)

    build_volume_str = sys.argv[2]

    # Parse build volume
    try:
        parts = build_volume_str.split("x")
        if len(parts) != 3:
            raise ValueError("Build volume must be in format XxYxZ (e.g., 350x350x250)")
        x, y, z = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as e:
        print(f"Error: Invalid build volume format: {e}")
        sys.exit(1)

    # Get maker (default to misumi)
    maker_name = "misumi"
    if "--maker" in sys.argv:
        idx = sys.argv.index("--maker")
        if idx + 1 < len(sys.argv):
            maker_name = sys.argv[idx + 1]

    # Get printer and maker instances
    printer = get_printer(printer_name)
    if not printer:
        print(f"Error: Unknown printer type: {printer_name}")
        print(f"Available types: {', '.join(list_printers())}")
        sys.exit(1)

    maker = get_maker(maker_name)
    if not maker:
        print(f"Error: Unknown maker: {maker_name}")
        print(f"Available makers: {', '.join(list_makers())}")
        sys.exit(1)

    # Create build volume object
    from extrusion_decoder.printers.base import BuildVolume

    build_volume = BuildVolume(x, y, z, build_volume_str)

    # Check if build volume is supported
    if not printer.supports_build_volume(build_volume):
        print(
            f"Warning: Build volume {build_volume_str} may not be officially supported"
        )
        print(f"Supported volumes for {printer.display_name}:")
        for vol in printer.get_supported_build_volumes():
            print(f"  - {vol.name}")

    # Get extrusion specifications
    specs = printer.get_extrusion_specs(build_volume)

    # Generate part numbers
    print("=" * 70)
    print(f"{printer.display_name} - {build_volume_str} Build Volume")
    print(f"Extrusion Maker: {maker.display_name}")
    print("=" * 70)
    print()

    total_extrusions = 0
    for spec in specs:
        part_number = maker.encode_part_number(
            series="HFSB5",  # TODO: Make series configurable
            size="2020",  # TODO: Make size configurable
            length=spec.length,
            alterations=spec.alterations,
        )

        print(f"{spec.letter} Extrusion (x{spec.quantity})")
        if spec.description:
            print(f"  Description: {spec.description}")
        print(f"  Length: {spec.length}mm")
        print(f"  Part Number: {part_number}")
        if spec.alterations:
            print(f"  Alterations: {', '.join(spec.alterations)}")
        print()

        total_extrusions += spec.quantity

    print("=" * 70)
    print(f"Total extrusions needed: {total_extrusions}")
    print("=" * 70)


if __name__ == "__main__":
    main()
