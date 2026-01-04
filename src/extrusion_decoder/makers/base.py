"""Base classes for extrusion maker support."""

from abc import ABC, abstractmethod
from typing import Any


class ExtrusionMaker(ABC):
    """Base class for extrusion maker support."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this maker."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return the display name of this maker."""
        pass

    @abstractmethod
    def decode_part_number(self, part_number: str) -> dict[str, Any]:
        """Decode a part number into its components.

        Args:
            part_number: The part number to decode

        Returns:
            Dictionary with decoded information
        """
        pass

    @abstractmethod
    def encode_part_number(
        self,
        series: str,
        size: str,
        length: int,
        alterations: list[str] | None = None,
    ) -> str:
        """Encode components into a part number.

        Args:
            series: Extrusion series code
            size: Cross-sectional size code
            length: Length in mm
            alterations: List of alteration codes

        Returns:
            Part number string
        """
        pass

    @abstractmethod
    def format_description(self, decoded: dict[str, Any]) -> str:
        """Format decoded information into a human-readable description.

        Args:
            decoded: Dictionary returned from decode_part_number()

        Returns:
            Formatted string description
        """
        pass
