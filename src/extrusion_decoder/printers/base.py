"""Base classes for printer type support."""

from abc import ABC, abstractmethod
from typing import Any


class BuildVolume:
    """Represents a build volume configuration."""

    def __init__(self, x: int, y: int, z: int, name: str | None = None):
        """Initialize build volume.

        Args:
            x: X dimension in mm
            y: Y dimension in mm
            z: Z dimension in mm
            name: Optional name for this build volume (e.g., "350x350x250")
        """
        self.x = x
        self.y = y
        self.z = z
        self.name = name or f"{x}x{y}x{z}"

    def __repr__(self) -> str:
        return f"BuildVolume({self.name})"


class ExtrusionSpec:
    """Specification for a single extrusion in a printer frame."""

    def __init__(
        self,
        letter: str,
        length: int,
        quantity: int,
        alterations: list[str] | None = None,
        description: str | None = None,
    ):
        """Initialize extrusion specification.

        Args:
            letter: Letter designation (A-H for Voron Trident)
            length: Length in mm
            quantity: Number of this extrusion needed
            alterations: List of alteration codes (e.g., ["LCP", "RCP", "AV360"])
            description: Human-readable description of this extrusion's purpose
        """
        self.letter = letter
        self.length = length
        self.quantity = quantity
        self.alterations = alterations or []
        self.description = description

    def __repr__(self) -> str:
        return f"ExtrusionSpec({self.letter}, {self.length}mm, qty={self.quantity})"


class PrinterType(ABC):
    """Base class for printer type support."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this printer type."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return the display name of this printer type."""
        pass

    @abstractmethod
    def get_supported_build_volumes(self) -> list[BuildVolume]:
        """Get list of supported build volumes for this printer type.

        Returns:
            List of BuildVolume objects
        """
        pass

    @abstractmethod
    def get_extrusion_specs(self, build_volume: BuildVolume) -> list[ExtrusionSpec]:
        """Get extrusion specifications for a given build volume.

        Args:
            build_volume: The build volume configuration

        Returns:
            List of ExtrusionSpec objects
        """
        pass

    @abstractmethod
    def get_extrusion_letter(
        self,
        decoded: dict[str, Any],
        quantity: int = 1,
        build_volume: BuildVolume | None = None,
    ) -> str | None:
        """Determine the letter designation for an extrusion.

        Args:
            decoded: Dictionary returned from decode_misumi_name()
            quantity: Quantity of this extrusion in the BOM
            build_volume: Build volume configuration (optional, for disambiguation)

        Returns:
            Letter designation or None if unknown
        """
        pass

    def supports_build_volume(self, build_volume: BuildVolume) -> bool:
        """Check if this printer type supports a given build volume.

        Args:
            build_volume: The build volume to check

        Returns:
            True if supported, False otherwise
        """
        supported = self.get_supported_build_volumes()
        for vol in supported:
            if (
                vol.x == build_volume.x
                and vol.y == build_volume.y
                and vol.z == build_volume.z
            ):
                return True
        return False
