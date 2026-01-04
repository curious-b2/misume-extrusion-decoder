"""Command-line interface for the MISUMI decoder."""

import sys

from extrusion_decoder.decoder import (
    decode_misumi_name,
    extract_misumi_from_bom,
    format_bom_output,
    format_description,
)


def main() -> None:
    """Command-line interface for the decoder."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  misumi-decoder <part_number>")
        print("  misumi-decoder --bom <csv_file> [--voron]")
        print("\nExamples:")
        print("  misumi-decoder HFSB5-2020-500-LCP-RCP-AV360")
        print("  misumi-decoder --bom generated_bom.csv")
        print("  misumi-decoder --bom generated_bom.csv --voron")
        sys.exit(1)

    if sys.argv[1] == "--bom" or sys.argv[1] == "-bom":
        if len(sys.argv) < 3:
            print("Error: Please provide a CSV file path")
            print("Usage: misumi-decoder --bom <csv_file> [--voron]")
            sys.exit(1)

        csv_path = sys.argv[2]
        use_voron = "--voron" in sys.argv or "-voron" in sys.argv

        parts = extract_misumi_from_bom(csv_path)

        if use_voron:
            try:
                from extrusion_decoder.voron import format_voron_bom_output

                print(format_voron_bom_output(parts))
            except ImportError:
                print("Error: Voron module not available")
                sys.exit(1)
        else:
            print(format_bom_output(parts))
    else:
        part_number = sys.argv[1]
        decoded = decode_misumi_name(part_number)
        print(format_description(decoded))


if __name__ == "__main__":
    main()
