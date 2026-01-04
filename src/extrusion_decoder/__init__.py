"""MISUMI Extrusion Name Decoder.

Decodes MISUMI aluminum extrusion part numbers into human-readable descriptions.

Core functionality is in the decoder module. Voron Trident-specific functionality
(letter designations) is in the voron module.
"""

from extrusion_decoder.decoder import (
    decode_misumi_name,
    extract_misumi_from_bom,
    format_bom_output,
    format_description,
)

# Voron-specific functionality (optional)
try:
    from extrusion_decoder.voron import (
        detect_build_size,
        format_voron_bom_output,
        get_extrusion_letter,
    )
except ImportError:
    # Allow importing even if voron module has issues
    pass

__all__ = [
    # Core decoder functions
    "decode_misumi_name",
    "format_description",
    "extract_misumi_from_bom",
    "format_bom_output",
    # Voron-specific functions (optional)
    "get_extrusion_letter",
    "detect_build_size",
    "format_voron_bom_output",
]
