"""MISUMI extrusion maker support."""

from typing import Any

from extrusion_decoder.decoder import (
    decode_misumi_name,
)
from extrusion_decoder.decoder import (
    format_description as format_misumi_description,
)
from extrusion_decoder.makers.base import ExtrusionMaker


class MisumiMaker(ExtrusionMaker):
    """MISUMI extrusion maker."""

    @property
    def name(self) -> str:
        return "misumi"

    @property
    def display_name(self) -> str:
        return "MISUMI"

    def decode_part_number(self, part_number: str) -> dict[str, Any]:
        """Decode a MISUMI part number.

        Args:
            part_number: The MISUMI part number to decode

        Returns:
            Dictionary with decoded information
        """
        return decode_misumi_name(part_number)

    def encode_part_number(
        self,
        series: str,
        size: str,
        length: int,
        alterations: list[str] | None = None,
    ) -> str:
        """Encode components into a MISUMI part number.

        Args:
            series: Extrusion series code (e.g., "HFSB5")
            size: Cross-sectional size code (e.g., "2020")
            length: Length in mm (e.g., 500)
            alterations: List of alteration codes (e.g., ["LCP", "RCP", "AV360"])

        Returns:
            MISUMI part number string
        """
        parts = [series, size, str(length)]
        if alterations:
            parts.extend(alterations)
        return "-".join(parts)

    def format_description(self, decoded: dict[str, Any]) -> str:
        """Format decoded MISUMI information.

        Args:
            decoded: Dictionary returned from decode_part_number()

        Returns:
            Formatted string description
        """
        return format_misumi_description(decoded)
