"""Printer type support for different Voron models."""

from extrusion_decoder.printers.base import PrinterType
from extrusion_decoder.printers.trident import TridentPrinter

# Registry of available printer types
PRINTER_TYPES: dict[str, type[PrinterType]] = {
    "trident": TridentPrinter,
    # TODO: Add Voron 0 support
    # "voron0": Voron0Printer,
    # TODO: Add Voron 2.4 support
    # "voron24": Voron24Printer,
}


def get_printer(printer_name: str) -> PrinterType | None:
    """Get a printer instance by name.

    Args:
        printer_name: Name of the printer type (e.g., "trident", "voron0", "voron24")

    Returns:
        PrinterType instance or None if not found
    """
    printer_class = PRINTER_TYPES.get(printer_name.lower())
    if printer_class:
        return printer_class()
    return None


def list_printers() -> list[str]:
    """List all available printer types.

    Returns:
        List of printer type names
    """
    return list(PRINTER_TYPES.keys())
