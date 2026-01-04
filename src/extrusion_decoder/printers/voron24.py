"""Voron 2.4 printer type support (placeholder)."""

from typing import Any

from extrusion_decoder.printers.base import BuildVolume, ExtrusionSpec, PrinterType


class Voron24Printer(PrinterType):
    """Voron 2.4 printer type (placeholder - not yet implemented)."""

    @property
    def name(self) -> str:
        return "voron24"

    @property
    def display_name(self) -> str:
        return "Voron 2.4"

    def get_supported_build_volumes(self) -> list[BuildVolume]:
        """Get supported build volumes for Voron 2.4.

        TODO: Add actual build volume dimensions for Voron 2.4
        """
        return [
            # TODO: Add actual Voron 2.4 build volumes
        ]

    def get_extrusion_specs(self, build_volume: BuildVolume) -> list[ExtrusionSpec]:
        """Get extrusion specifications for Voron 2.4 build volume.

        TODO: Implement Voron 2.4 extrusion specifications
        """
        raise NotImplementedError("Voron 2.4 support not yet implemented")

    def get_extrusion_letter(
        self,
        decoded: dict[str, Any],
        quantity: int = 1,
        build_volume: BuildVolume | None = None,
    ) -> str | None:
        """Determine the letter designation for an extrusion.

        TODO: Implement Voron 2.4 letter mapping
        """
        raise NotImplementedError("Voron 2.4 support not yet implemented")
